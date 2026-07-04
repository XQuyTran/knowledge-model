import re
import tempfile
from pathlib import Path
from typing import List

from .interfaces import Analyzer
from .models import DiagnosticRequest, EvidenceInstance, SourceLocation
from .tooling import ToolRunner


class ClangASTAnalyzer(Analyzer):
    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=6.0)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            src.write_text(request.source_code, encoding="utf-8")
            command = ["clang++", "-std=c++23", "-Xclang", "-ast-dump", "-fsyntax-only", str(src)] + request.compiler_flags
            result = self.runner.run(command, cwd=workdir)
            evidence: List[EvidenceInstance] = []
            if not result.available:
                return evidence
            ast = result.stdout + "" + result.stderr
            if "ForStmt" in ast and re.search(r"<=", request.source_code):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.loop.boundary.le_length",
                    source="ClangAST",
                    confidence=0.82,
                    description="Clang AST found a for-loop whose source contains a non-strict upper-bound comparison.",
                    location=self._find_line(request, "<="),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
            if "ArraySubscriptExpr" in ast and re.search(r"<=", request.source_code):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.array.index.size_access",
                    source="ClangAST",
                    confidence=0.72,
                    description="Clang AST found array indexing near a possibly inclusive upper-bound loop.",
                    location=self._find_line(request, "["),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
            if "UnaryOperator" in ast and "*" in request.source_code and "nullptr" not in request.source_code and "NULL" not in request.source_code:
                evidence.append(EvidenceInstance(
                    evidence_id="ev.pointer.null_check_missing",
                    source="ClangAST",
                    confidence=0.58,
                    description="Clang AST found pointer dereference without an obvious null guard in source text.",
                    location=self._find_line(request, "*"),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
            return evidence

    def _find_line(self, request: DiagnosticRequest, token: str) -> SourceLocation:
        for idx, line in enumerate(request.source_code.splitlines(), start=1):
            if token in line:
                return SourceLocation(request.file_path, idx, idx)
        return SourceLocation(request.file_path)


class ClangStaticAnalyzer(Analyzer):
    WARNING_MAP = [
        (re.compile(r"Dereference of null pointer|null dereference", re.I), "ev.pointer.clang_null", "Static analyzer reports a possible null dereference.", 0.96),
        (re.compile(r"Use of memory after it is freed|use-after-free", re.I), "ev.memory.release_then_use", "Static analyzer reports use after release.", 0.96),
        (re.compile(r"Potential leak|leak", re.I), "ev.memory.alloc_without_release", "Static analyzer reports a possible resource leak.", 0.88),
        (re.compile(r"Assigned value is garbage|uninitialized", re.I), "ev.uninitialized.value", "Static analyzer reports possible uninitialized value use.", 0.80),
    ]

    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=10.0)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            src.write_text(request.source_code, encoding="utf-8")
            command = ["clang++", "--analyze", "-std=c++23", str(src)] + request.compiler_flags
            result = self.runner.run(command, cwd=workdir, timeout_seconds=10.0)
            if not result.available:
                return []
            output = result.stdout + "" + result.stderr
            evidence: List[EvidenceInstance] = []
            for regex, evidence_id, description, confidence in self.WARNING_MAP:
                if regex.search(output):
                    evidence.append(EvidenceInstance(
                        evidence_id=evidence_id,
                        source="ClangStaticAnalyzer",
                        confidence=confidence,
                        description=description,
                        location=self._parse_location(request, output),
                        metadata={"raw": output[-2000:]},
                    ))
            return evidence

    def _parse_location(self, request: DiagnosticRequest, output: str) -> SourceLocation:
        match = re.search(r":(\d+):(\d+):\s+warning:", output)
        if match:
            return SourceLocation(request.file_path, int(match.group(1)), int(match.group(1)), int(match.group(2)), int(match.group(2)))
        return SourceLocation(request.file_path)


class ClangTidyAnalyzer(Analyzer):
    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=10.0)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            src.write_text(request.source_code, encoding="utf-8")
            command = ["clang-tidy", str(src), "--", "-std=c++23"] + request.compiler_flags
            result = self.runner.run(command, cwd=workdir, timeout_seconds=10.0)
            if not result.available:
                return []
            output = result.stdout + "" + result.stderr
            evidence: List[EvidenceInstance] = []
            if re.search(r"bugprone.*use-after-move|use after move", output, re.I):
                evidence.append(EvidenceInstance("ev.move.use_after_move", "clang-tidy", 0.86, "clang-tidy reports possible use after move.", self._parse_location(request, output), {"raw": output[-2000:]}))
            if re.search(r"cppcoreguidelines.*virtual.*destructor|virtual destructor", output, re.I):
                evidence.append(EvidenceInstance("ev.oop.delete_base_no_virtual", "clang-tidy", 0.88, "clang-tidy reports a polymorphic base class without virtual destructor.", self._parse_location(request, output), {"raw": output[-2000:]}))
            if re.search(r"bugprone.*format|format", output, re.I):
                evidence.append(EvidenceInstance("ev.format.printf_type_mismatch", "clang-tidy", 0.82, "clang-tidy reports possible format string issue.", self._parse_location(request, output), {"raw": output[-2000:]}))
            return evidence

    def _parse_location(self, request: DiagnosticRequest, output: str) -> SourceLocation:
        match = re.search(r":(\d+):(\d+):\s+warning:", output)
        if match:
            return SourceLocation(request.file_path, int(match.group(1)), int(match.group(1)), int(match.group(2)), int(match.group(2)))
        return SourceLocation(request.file_path)
