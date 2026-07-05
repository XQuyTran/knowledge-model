import tempfile
from pathlib import Path
from typing import List

from .interfaces import Analyzer
from .models import DiagnosticRequest, EvidenceInstance, SourceLocation
from .resource_limits import make_process_limiter
from .tooling import ToolRunner


class LocalSandboxRunner(Analyzer):
    """Compile and run tests locally through subprocess.run with resource.setrlimit.

    This runner assumes the whole service already runs inside a hardened Docker
    container. It applies additional Unix process limits to the student subprocess.
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

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not request.test_cases:
            return []
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            binary = workdir / 'submission.out'
            src.write_text(request.source_code, encoding='utf-8')
            limiter = make_process_limiter(cpu_seconds=self.cpu_seconds, memory_bytes=self.memory_bytes)
            compile_cmd = ['clang++', '-std=c++23', '-O0', '-g', str(src), '-o', str(binary)] + request.compiler_flags
            compile_result = self.runner.run(compile_cmd, cwd=workdir, timeout_seconds=8.0, preexec_fn=limiter)
            evidence: List[EvidenceInstance] = []
            if not compile_result.available:
                return evidence
            if compile_result.exit_code != 0:
                evidence.append(EvidenceInstance(
                    evidence_id='ev.compile.error',
                    source='LocalSandboxRunner',
                    confidence=0.99,
                    description='Compilation failed before runtime diagnosis.',
                    location=SourceLocation(request.file_path),
                    metadata={'stderr': compile_result.stderr[-2000:]},
                ))
                return evidence
            for test in request.test_cases:
                result = self.runner.run(
                    [str(binary)],
                    cwd=workdir,
                    timeout_seconds=test.timeout_seconds,
                    input_data=test.input_data,
                    preexec_fn=limiter,
                )
                if result.timed_out:
                    evidence.append(EvidenceInstance('ev.loop.timeout', 'LocalSandboxRunner', 0.85, f"Test '{test.name}' timed out.", SourceLocation(request.file_path)))
                elif result.exit_code != 0:
                    evidence.append(EvidenceInstance('ev.runtime.crash', 'LocalSandboxRunner', 0.80, f"Test '{test.name}' crashed or exited abnormally.", SourceLocation(request.file_path), {'stderr': result.stderr[-1000:]}))
                elif test.expected_output and result.stdout.strip() != test.expected_output.strip():
                    evidence.append(EvidenceInstance('ev.cross.edge_only_failure', 'LocalSandboxRunner', 0.68, f"Test '{test.name}' produced unexpected output.", SourceLocation(request.file_path), {'stdout': result.stdout[-1000:], 'expected': test.expected_output}))
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

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not request.enable_sanitizers or not request.test_cases:
            return []
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            binary = workdir / 'submission_san.out'
            src.write_text(request.source_code, encoding='utf-8')
            limiter = make_process_limiter(cpu_seconds=self.cpu_seconds, memory_bytes=self.memory_bytes)
            compile_cmd = [
                'clang++', '-std=c++23', '-O0', '-g',
                '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                str(src), '-o', str(binary),
            ] + request.compiler_flags
            compile_result = self.runner.run(compile_cmd, cwd=workdir, timeout_seconds=10.0, preexec_fn=limiter)
            if not compile_result.available or compile_result.exit_code != 0:
                return []
            evidence: List[EvidenceInstance] = []
            for test in request.test_cases:
                result = self.runner.run(
                    [str(binary)],
                    cwd=workdir,
                    timeout_seconds=test.timeout_seconds,
                    input_data=test.input_data,
                    preexec_fn=limiter,
                )
                output = result.stdout + '\n' + result.stderr
                if 'heap-use-after-free' in output or 'use-after-free' in output:
                    evidence.append(EvidenceInstance('ev.memory.sanitizer_uaf', 'SanitizerRunner', 0.99, 'AddressSanitizer reports use-after-free.', SourceLocation(request.file_path), {'raw': output[-2000:]}))
                if 'LeakSanitizer' in output or 'detected memory leaks' in output:
                    evidence.append(EvidenceInstance('ev.memory.sanitizer_leak', 'SanitizerRunner', 0.99, 'LeakSanitizer reports unreleased allocations.', SourceLocation(request.file_path), {'raw': output[-2000:]}))
                if 'out-of-bounds' in output or 'buffer-overflow' in output or 'global-buffer-overflow' in output or 'stack-buffer-overflow' in output:
                    evidence.append(EvidenceInstance('ev.array.bounds.crash', 'SanitizerRunner', 0.96, 'Sanitizer reports out-of-bounds memory access.', SourceLocation(request.file_path), {'raw': output[-2000:]}))
                if 'runtime error' in output and 'null pointer' in output:
                    evidence.append(EvidenceInstance('ev.pointer.clang_null', 'SanitizerRunner', 0.94, 'UndefinedBehaviorSanitizer reports null pointer use.', SourceLocation(request.file_path), {'raw': output[-2000:]}))
            return evidence
