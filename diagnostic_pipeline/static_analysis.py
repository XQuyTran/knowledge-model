"""Heuristic static analyzer.

This implementation is intentionally lightweight so the pipeline can run without
external dependencies. In production, replace or supplement it with Clang AST,
Clang Static Analyzer, clang-tidy, and sanitizer outputs.
"""



import re
from typing import List

from .interfaces import StaticAnalyzer
from .models import DiagnosticRequest, EvidenceInstance, SourceLocation


class HeuristicStaticAnalyzer(StaticAnalyzer):
    """Extract simple evidence patterns from C/C++ code."""

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        evidence: List[EvidenceInstance] = []
        lines = request.source_code.splitlines()
        code = request.source_code

        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()

            if re.search(r"for\s*\([^;]+;[^;]*<=\s*\w+\s*;", stripped):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.loop.boundary.le_length",
                    source="ASTInspection",
                    confidence=0.78,
                    description="Loop condition appears to use <= with an upper bound.",
                    location=SourceLocation(request.file_path, line_no, line_no),
                ))

            if re.search(r"for\s*\(\s*(?:int\s+)?\w+\s*=\s*1\s*;", stripped):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.loop.boundary.starts_one",
                    source="ASTInspection",
                    confidence=0.62,
                    description="Loop starts at 1, which may be suspicious for zero-indexed traversal.",
                    location=SourceLocation(request.file_path, line_no, line_no),
                ))

            if re.search(r"\w+\s*\[\s*\w+\.size\s*\(\s*\)\s*\]", stripped) or re.search(r"\w+\s*\[\s*\w+\s*\]", stripped) and "<=" in code:
                evidence.append(EvidenceInstance(
                    evidence_id="ev.array.index.size_access",
                    source="ASTInspection",
                    confidence=0.58,
                    description="Index expression may reach the size or upper bound of an array/container.",
                    location=SourceLocation(request.file_path, line_no, line_no),
                ))

            if re.search(r"\*\s*\w+", stripped) and "nullptr" not in code and "NULL" not in code:
                evidence.append(EvidenceInstance(
                    evidence_id="ev.pointer.null_check_missing",
                    source="ASTInspection",
                    confidence=0.55,
                    description="Pointer dereference appears without an obvious null guard.",
                    location=SourceLocation(request.file_path, line_no, line_no),
                ))

            if re.search(r"free\s*\(", stripped) or re.search(r"delete\s+", stripped):
                if self._has_later_pointer_use(lines, line_no):
                    evidence.append(EvidenceInstance(
                        evidence_id="ev.memory.release_then_use",
                        source="DataFlowInspection",
                        confidence=0.70,
                        description="A resource is released and a later use may still occur.",
                        location=SourceLocation(request.file_path, line_no, line_no),
                    ))

        if self._non_void_function_may_miss_return(code):
            evidence.append(EvidenceInstance(
                evidence_id="ev.function.warn_nonvoid",
                source="CompilerWarning",
                confidence=0.80,
                description="A non-void function may reach the end without returning a value.",
                location=SourceLocation(request.file_path, None, None),
            ))

        if self._recursive_call_without_progress(code):
            evidence.append(EvidenceInstance(
                evidence_id="ev.recursion.no_progress",
                source="ASTInspection",
                confidence=0.76,
                description="Recursive call may not reduce the problem size.",
                location=SourceLocation(request.file_path, None, None),
            ))

        return evidence

    def _has_later_pointer_use(self, lines: List[str], release_line: int) -> bool:
        tail = "\n".join(lines[release_line: release_line + 5])
        return "*" in tail or "->" in tail

    def _non_void_function_may_miss_return(self, code: str) -> bool:
        has_non_void = bool(re.search(r"\b(int|double|float|bool|char|long|short|size_t|string|std::string)\s+\w+\s*\([^)]*\)\s*\{", code))
        return has_non_void and "return" not in code

    def _recursive_call_without_progress(self, code: str) -> bool:
        match = re.search(r"\b(?:int|void|long|double|float|bool)\s+(\w+)\s*\([^)]*\)\s*\{", code)
        if not match:
            return False
        name = match.group(1)
        return bool(re.search(rf"\b{name}\s*\(\s*\w+\s*\)", code))
