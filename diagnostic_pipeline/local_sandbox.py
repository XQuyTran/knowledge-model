import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from .interfaces import Analyzer
from .models import DiagnosticRequest, EvidenceInstance, SourceLocation
from .resource_limits import make_process_limiter
from .tooling import ToolRunner


@dataclass
class _ExecutionResult:
    available: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class LocalSandboxRunner(Analyzer):
    """Compile with ToolRunner and execute local binaries directly via subprocess.

    Rationale:
    - Compile steps still benefit from ToolRunner's tool-discovery and timeout logic.
    - Runtime steps should not go through PATH-based tool discovery because the
      produced binary lives inside a temporary working directory.
    """

    def __init__(
        self,
        runner: ToolRunner | None = None,
        cpu_seconds: int = 3,
        memory_bytes: int = 512 * 1024 * 1024,
    ) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=8.0)
        self.cpu_seconds = cpu_seconds
        self.memory_bytes = memory_bytes

    def _run_binary(self, binary: Path, cwd: Path, timeout_seconds: float, input_data: str, limiter) -> _ExecutionResult:
        try:
            completed = subprocess.run(
                [str(binary)],
                cwd=str(cwd),
                input=input_data,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                preexec_fn=limiter,
            )
            return _ExecutionResult(
                available=True,
                exit_code=int(completed.returncode),
                stdout=completed.stdout,
                stderr=completed.stderr,
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            return _ExecutionResult(
                available=True,
                exit_code=-1,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                timed_out=True,
            )
        except (FileNotFoundError, PermissionError) as exc:
            return _ExecutionResult(
                available=False,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                timed_out=False,
            )

    def _classify_runtime_failure(self, result: _ExecutionResult) -> Tuple[str, float, str, dict]:
        output = (result.stdout + "\n" + result.stderr).lower()
        metadata = {"stderr": result.stderr[-2000:], "stdout": result.stdout[-2000:]}
        if any(token in output for token in (
            "stack-buffer-overflow",
            "heap-buffer-overflow",
            "global-buffer-overflow",
            "out-of-bounds",
            "out of bounds",
            "buffer overflow",
            "index out of bounds",
        )):
            return (
                "ev.array.bounds.crash",
                0.92,
                "Runtime behavior suggests an out-of-bounds access.",
                metadata,
            )
        if any(token in output for token in (
            "use-after-free",
            "heap-use-after-free",
            "addresssanitizer: heap-use-after-free",
        )):
            return (
                "ev.memory.release_then_use",
                0.96,
                "Runtime behavior suggests use-after-free or access after release.",
                metadata,
            )
        if any(token in output for token in (
            "null pointer",
            "member access within null pointer",
            "dereference of null",
            "segmentation fault",
            "access violation",
        )) and ("->" in (result.stdout + result.stderr) or "nullptr" in output or "null" in output):
            return (
                "ev.pointer.clang_null",
                0.88,
                "Runtime behavior suggests a null-pointer dereference or invalid pointer access.",
                metadata,
            )
        if any(token in output for token in (
            "stack overflow",
            "addresssanitizer: stack-overflow",
            "stackoverflow",
        )):
            return (
                "ev.recursion.stack_overflow",
                0.95,
                "Runtime behavior suggests unbounded recursion or stack overflow.",
                metadata,
            )
        return (
            "ev.runtime.crash",
            0.80,
            "Test crashed or exited abnormally.",
            metadata,
        )

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not request.test_cases:
            return []
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            binary = workdir / "submission.out"
            src.write_text(request.source_code, encoding="utf-8")
            limiter = make_process_limiter(cpu_seconds=self.cpu_seconds, memory_bytes=self.memory_bytes)
            compile_cmd = ["clang++", "-std=c++23", "-O0", "-g", str(src), "-o", str(binary)] + request.compiler_flags
            compile_result = self.runner.run(compile_cmd, cwd=workdir, timeout_seconds=8.0, preexec_fn=limiter)
            evidence: List[EvidenceInstance] = []
            if not compile_result.available:
                return evidence
            if compile_result.exit_code != 0:
                evidence.append(EvidenceInstance(
                    evidence_id="ev.compile.error",
                    source="LocalSandboxRunner",
                    confidence=0.99,
                    description="Compilation failed before runtime diagnosis.",
                    location=SourceLocation(request.file_path),
                    metadata={"stderr": compile_result.stderr[-2000:], "stdout": compile_result.stdout[-2000:]},
                ))
                return evidence
            if not binary.exists():
                evidence.append(EvidenceInstance(
                    evidence_id="ev.compile.error",
                    source="LocalSandboxRunner",
                    confidence=0.99,
                    description="Compilation reported success but no executable was produced.",
                    location=SourceLocation(request.file_path),
                    metadata={"stderr": compile_result.stderr[-2000:], "stdout": compile_result.stdout[-2000:]},
                ))
                return evidence
            binary.chmod(0o755)
            for test in request.test_cases:
                result = self._run_binary(
                    binary=binary,
                    cwd=workdir,
                    timeout_seconds=test.timeout_seconds,
                    input_data=test.input_data,
                    limiter=limiter,
                )
                if not result.available:
                    evidence.append(EvidenceInstance(
                        evidence_id="ev.runtime.crash",
                        source="LocalSandboxRunner",
                        confidence=0.75,
                        description="The compiled submission could not be executed.",
                        location=SourceLocation(request.file_path),
                        metadata={"stderr": result.stderr[-2000:]},
                    ))
                    continue
                if result.timed_out:
                    evidence.append(EvidenceInstance(
                        "ev.loop.timeout",
                        "LocalSandboxRunner",
                        0.88,
                        f"Test '{test.name}' timed out.",
                        SourceLocation(request.file_path),
                        {"stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]},
                    ))
                elif result.exit_code != 0:
                    evidence_id, confidence, description, metadata = self._classify_runtime_failure(result)
                    evidence.append(EvidenceInstance(
                        evidence_id=evidence_id,
                        source="LocalSandboxRunner",
                        confidence=confidence,
                        description=description,
                        location=SourceLocation(request.file_path),
                        metadata=metadata,
                    ))
                elif test.expected_output and result.stdout.strip() != test.expected_output.strip():
                    evidence.append(EvidenceInstance(
                        "ev.cross.edge_only_failure",
                        "LocalSandboxRunner",
                        0.68,
                        f"Test '{test.name}' produced unexpected output.",
                        SourceLocation(request.file_path),
                        {"stdout": result.stdout[-1000:], "expected": test.expected_output},
                    ))
            return evidence


class SanitizerRunner(Analyzer):
    def __init__(
        self,
        runner: ToolRunner | None = None,
        cpu_seconds: int = 3,
        memory_bytes: int = 512 * 1024 * 1024,
    ) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=10.0)
        self.cpu_seconds = cpu_seconds
        self.memory_bytes = memory_bytes

    def _run_binary(self, binary: Path, cwd: Path, timeout_seconds: float, input_data: str, limiter) -> _ExecutionResult:
        try:
            completed = subprocess.run(
                [str(binary)],
                cwd=str(cwd),
                input=input_data,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                preexec_fn=limiter,
            )
            return _ExecutionResult(True, int(completed.returncode), completed.stdout, completed.stderr, False)
        except subprocess.TimeoutExpired as exc:
            return _ExecutionResult(True, -1, exc.stdout or "", exc.stderr or "", True)
        except (FileNotFoundError, PermissionError) as exc:
            return _ExecutionResult(False, -1, "", str(exc), False)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not request.enable_sanitizers or not request.test_cases:
            return []
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            binary = workdir / "submission_san.out"
            src.write_text(request.source_code, encoding="utf-8")
            limiter = make_process_limiter(cpu_seconds=self.cpu_seconds, memory_bytes=self.memory_bytes)
            compile_cmd = [
                "clang++", "-std=c++23", "-O0", "-g",
                "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                str(src), "-o", str(binary),
            ] + request.compiler_flags
            compile_result = self.runner.run(compile_cmd, cwd=workdir, timeout_seconds=10.0, preexec_fn=limiter)
            if not compile_result.available or compile_result.exit_code != 0 or not binary.exists():
                return []
            evidence: List[EvidenceInstance] = []
            for test in request.test_cases:
                result = self._run_binary(binary, workdir, test.timeout_seconds, test.input_data, limiter)
                if not result.available:
                    continue
                output = (result.stdout + "\n" + result.stderr)
                lowered = output.lower()
                raw = {"raw": output[-4000:]}
                if result.timed_out:
                    evidence.append(EvidenceInstance("ev.loop.timeout", "SanitizerRunner", 0.86, f"Sanitizer run for test '{test.name}' timed out.", SourceLocation(request.file_path), raw))
                    continue
                if any(token in lowered for token in ("heap-use-after-free", "use-after-free", "addresssanitizer: heap-use-after-free")):
                    evidence.append(EvidenceInstance("ev.memory.sanitizer_uaf", "SanitizerRunner", 0.99, "AddressSanitizer reports use-after-free.", SourceLocation(request.file_path), raw))
                if any(token in lowered for token in ("leaksanitizer", "detected memory leaks", "direct leak", "indirect leak")):
                    evidence.append(EvidenceInstance("ev.memory.sanitizer_leak", "SanitizerRunner", 0.99, "LeakSanitizer reports unreleased allocations.", SourceLocation(request.file_path), raw))
                if any(token in lowered for token in ("out-of-bounds", "buffer-overflow", "global-buffer-overflow", "stack-buffer-overflow", "heap-buffer-overflow", "index out of bounds")):
                    evidence.append(EvidenceInstance("ev.array.bounds.crash", "SanitizerRunner", 0.96, "Sanitizer reports out-of-bounds memory access.", SourceLocation(request.file_path), raw))
                if any(token in lowered for token in ("runtime error") ) and any(token in lowered for token in ("null pointer", "member access within null pointer", "load of null pointer", "store to null pointer")):
                    evidence.append(EvidenceInstance("ev.pointer.clang_null", "SanitizerRunner", 0.94, "UndefinedBehaviorSanitizer reports null pointer use.", SourceLocation(request.file_path), raw))
                if any(token in lowered for token in ("stack-overflow", "addresssanitizer: stack-overflow", "stack overflow")):
                    evidence.append(EvidenceInstance("ev.recursion.stack_overflow", "SanitizerRunner", 0.97, "Sanitizer reports stack overflow, often caused by missing recursive progress or base case.", SourceLocation(request.file_path), raw))
            return evidence
