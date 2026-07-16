import re
import tempfile
from pathlib import Path
from typing import List, Optional

from .interfaces import Analyzer
from .models import DiagnosticRequest, EvidenceInstance, SourceLocation
from .tooling import ToolRunner


class ClangASTAnalyzer(Analyzer):
    """AST-backed and source-pattern analyzer for C/C++ submissions.

    Design goals:
    - Keep the AST dump as a lightweight syntax/availability gate.
    - Prefer relation-aware heuristics over whole-file token scans.
    - Emit algorithm/context evidence where it improves downstream ranking.
    - Stay conservative: avoid strong bug evidence unless the source pattern is specific.
    """

    FOR_HEADER_RE = re.compile(
        r"for\s*\((?P<init>[^;]*);(?P<cond>[^;]*);(?P<step>[^)]*)\)",
        re.MULTILINE,
    )
    WHILE_HEADER_RE = re.compile(r"while\s*\((?P<cond>[^)]*)\)", re.MULTILINE)

    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=6.0)

    def _find_line(self, request: DiagnosticRequest, token: str) -> SourceLocation:
        for idx, line in enumerate(request.source_code.splitlines(), start=1):
            if token in line:
                return SourceLocation(request.file_path, idx, idx)
        return SourceLocation(request.file_path)

    def _line_from_offset(self, request: DiagnosticRequest, offset: int) -> SourceLocation:
        line_no = request.source_code.count("\n", 0, max(offset, 0)) + 1
        return SourceLocation(request.file_path, line_no, line_no)

    def _strip_comments(self, code: str) -> str:
        return re.sub(r"//.*", "", re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL))

    def _normalize_code(self, code: str) -> str:
        return re.sub(r"\s+", " ", self._strip_comments(code)).strip()

    def _extract_balanced_block(self, code: str, open_brace_offset: int) -> str:
        if open_brace_offset < 0 or open_brace_offset >= len(code):
            return ""
        depth = 0
        body_chars: list[str] = []
        for ch in code[open_brace_offset:]:
            if ch == "{":
                depth += 1
                if depth == 1:
                    continue
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            if depth >= 1:
                body_chars.append(ch)
        return "".join(body_chars)

    def _extract_statement_or_block_after_header(self, code: str, header_end: int) -> str:
        idx = header_end
        while idx < len(code) and code[idx].isspace():
            idx += 1
        if idx < len(code) and code[idx] == "{":
            return self._extract_balanced_block(code, idx)
        semi = code.find(";", idx)
        if semi == -1:
            return code[idx:]
        return code[idx : semi + 1]

    def _extract_for_headers(self, code: str) -> list[tuple[int, re.Match[str]]]:
        return [(m.start(), m) for m in self.FOR_HEADER_RE.finditer(code)]

    def _extract_while_headers(self, code: str) -> list[tuple[int, re.Match[str]]]:
        return [(m.start(), m) for m in self.WHILE_HEADER_RE.finditer(code)]

    def _extract_control_variable(self, condition: str) -> Optional[str]:
        match = re.search(r"\b([A-Za-z_]\w*)\b\s*(?:<=|>=|<|>|!=|==)", condition)
        if match:
            return match.group(1)
        return None

    def _has_update_for_var(self, body: str, var_name: str) -> bool:
        v = re.escape(var_name)
        update_re = re.compile(
            rf"(?:\+\+\s*{v}|{v}\s*\+\+|--\s*{v}|{v}\s*--|{v}\s*(?:\+=|-=|\*=|/=|=))"
        )
        return bool(update_re.search(body))

    def _has_new_without_delete(self, code: str) -> bool:
        no_comment = self._strip_comments(code)
        return bool(re.search(r"\bnew\b", no_comment) and not re.search(r"\bdelete\b", no_comment))

    def _has_missing_return(self, code: str) -> bool:
        no_comment = self._strip_comments(code)
        func_pattern = re.compile(
            r"(?:int|float|double|char|bool|long|short|unsigned|size_t|void\s*\*|std::\w+)\s+"
            r"(\w+)\s*\([^)]*\)\s*\{"
        )
        for match in func_pattern.finditer(no_comment):
            func_name = match.group(1)
            if func_name == "main":
                continue
            body = self._extract_balanced_block(no_comment, match.end() - 1)
            if not re.search(r"\breturn\b", body):
                return True
        return False

    def _detect_loop_boundary_issues(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        evidence: List[EvidenceInstance] = []
        if "ForStmt" not in ast:
            return evidence
        for offset, match in self._extract_for_headers(request.source_code):
            cond = match.group("cond").strip()
            if "<=" in cond and re.search(r"\b\w+\s*\[", request.source_code):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.loop.boundary.le_length",
                    source="ClangAST",
                    confidence=0.82,
                    description="A for-loop condition uses an inclusive upper bound near array-style indexing; verify the valid range.",
                    location=self._line_from_offset(request, offset),
                    metadata={"tool": "clang++ -ast-dump", "condition": cond},
                ))
        return evidence

    def _detect_array_index_issues(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        evidence: List[EvidenceInstance] = []
        if "ArraySubscriptExpr" not in ast:
            return evidence
        for offset, match in self._extract_for_headers(request.source_code):
            cond = match.group("cond").strip()
            body = self._extract_statement_or_block_after_header(request.source_code, match.end())
            if "<=" in cond and re.search(r"\w+\s*\[", body):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.array.index.size_access",
                    source="ClangAST",
                    confidence=0.74,
                    description="Array indexing appears inside a loop with an inclusive upper-bound condition.",
                    location=self._line_from_offset(request, offset),
                    metadata={"tool": "clang++ -ast-dump", "condition": cond},
                ))
        return evidence

    def _detect_pointer_issues(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        no_comment = self._strip_comments(request.source_code)
        deref_pattern = re.compile(r"(?:\b\w+\s*->\s*\w+|(?<![\w:])\*\s*[A-Za-z_]\w*)")
        if not deref_pattern.search(no_comment):
            return []
        if "nullptr" in no_comment or "NULL" in no_comment:
            return []
        return [EvidenceInstance(
            evidence_id="ev.pointer.null_check_missing",
            source="ClangAST",
            confidence=0.58,
            description="A pointer dereference or member access was found without an obvious null guard in the source text.",
            location=self._find_line(request, "->" if "->" in request.source_code else "*"),
            metadata={"tool": "clang++ -ast-dump"},
        )]

    def _detect_memory_issues(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not self._has_new_without_delete(request.source_code):
            return []
        return [EvidenceInstance(
            evidence_id="ev.memory.alloc_without_release",
            source="ClangAST",
            confidence=0.80,
            description="Code uses 'new' without a matching 'delete', suggesting a possible memory leak.",
            location=self._find_line(request, "new"),
            metadata={"tool": "clang++ -ast-dump"},
        )]

    def _detect_return_issues(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        if not self._has_missing_return(request.source_code):
            return []
        return [EvidenceInstance(
            evidence_id="ev.function.warn_nonvoid",
            source="ClangAST",
            confidence=0.82,
            description="A non-void function body appears to lack a return statement on at least one path.",
            location=self._find_line(request, "{"),
            metadata={"tool": "clang++ -ast-dump"},
        )]

    def _detect_while_progress_issues(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        evidence: List[EvidenceInstance] = []
        if "WhileStmt" not in ast:
            return evidence
        for offset, match in self._extract_while_headers(request.source_code):
            cond = match.group("cond").strip()
            control_var = self._extract_control_variable(cond)
            if not control_var:
                continue
            body = self._extract_statement_or_block_after_header(request.source_code, match.end())
            if not self._has_update_for_var(body, control_var):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.loop.no_progress",
                    source="ClangAST",
                    confidence=0.75,
                    description=f"A while loop does not appear to update its control variable '{control_var}'.",
                    location=self._line_from_offset(request, offset),
                    metadata={"tool": "clang++ -ast-dump", "condition": cond, "control_var": control_var},
                ))
        return evidence

    def _detect_recursion_issues(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        no_comment = self._strip_comments(request.source_code)
        func_pattern = re.compile(
            r"(?:int|long\s+long|float|double|char|bool|long|short|unsigned|size_t|void\s*\*|std::\w+)\s+"
            r"(\w+)\s*\([^)]*\)\s*\{"
        )
        evidence: List[EvidenceInstance] = []
        for match in func_pattern.finditer(no_comment):
            func_name = match.group(1)
            if func_name == "main":
                continue
            body = self._extract_balanced_block(no_comment, match.end() - 1)
            if re.search(rf"\b{re.escape(func_name)}\s*\(", body) and not re.search(r"\b(if|switch)\b", body):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.recursion.no_progress",
                    source="ClangAST",
                    confidence=0.78,
                    description=f"Function '{func_name}' calls itself recursively without an obvious base-case guard.",
                    location=self._find_line(request, func_name),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
        return evidence

    def _detect_insertion_sort_pattern(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        if "WhileStmt" not in ast or "ArraySubscriptExpr" not in ast:
            return []
        code = self._normalize_code(request.source_code)
        signals = [
            re.search(r"for\s*\(\s*(?:int\s+)?\w+\s*=\s*1\s*;\s*\w+\s*<\s*\w+\s*;", code),
            re.search(r"(?:int|auto)\s+\w+\s*=\s*\w+\s*\[\s*\w+\s*\]\s*;", code),
            re.search(r"(?:int|auto)\s+\w+\s*=\s*\w+\s*-\s*1\s*;", code),
            re.search(r"while\s*\(\s*\w+\s*>=\s*0\s*&&\s*\w+\s*\[\s*\w+\s*\]\s*>\s*\w+\s*\)", code),
            re.search(r"\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*=\s*\w+\s*\[\s*\w+\s*\]\s*;", code),
            re.search(r"\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*=\s*\w+\s*;", code),
        ]
        if sum(bool(x) for x in signals) < 5:
            return []
        return [EvidenceInstance(
            evidence_id="ev.sort.insertion.pattern",
            source="ClangAST",
            confidence=0.88,
            description="Source matches the canonical insertion-sort pattern: key extraction, left scan, right shift, and key insertion.",
            location=self._find_line(request, "while"),
            metadata={"tool": "clang++ -ast-dump", "pattern": "insertion_sort"},
        )]

    def _detect_insertion_sort_bugs(self, request: DiagnosticRequest, ast: str) -> List[EvidenceInstance]:
        if "WhileStmt" not in ast:
            return []
        evidence: List[EvidenceInstance] = []
        code = self._normalize_code(request.source_code)
        if re.search(r"while\s*\(\s*\w+\s*>\s*0\s*&&", code):
            evidence.append(EvidenceInstance(
                evidence_id="ev.sort.insertion.missed_zero_index",
                source="ClangAST",
                confidence=0.84,
                description="Insertion-sort inner loop uses '> 0' instead of '>= 0', which can skip index 0.",
                location=self._find_line(request, "while"),
                metadata={"tool": "clang++ -ast-dump", "pattern": "j > 0"},
            ))
        wrong_insert_match = re.search(r"\w+\s*\[\s*\w+\s*\]\s*=\s*\w+\s*;", code)
        has_shift = re.search(r"\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*=\s*\w+\s*\[\s*\w+\s*\]\s*;", code)
        has_correct_insert = re.search(r"\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*=\s*\w+\s*;", code)
        if has_shift and wrong_insert_match and not has_correct_insert:
            evidence.append(EvidenceInstance(
                evidence_id="ev.sort.insertion.wrong_insert_position",
                source="ClangAST",
                confidence=0.80,
                description="Insertion sort appears to write the key back to a[j] instead of a[j + 1].",
                location=self._find_line(request, "key"),
                metadata={"tool": "clang++ -ast-dump", "pattern": "a[j] = key"},
            ))
        for offset, match in self._extract_while_headers(request.source_code):
            cond = match.group("cond").strip()
            if ">= 0" not in cond and ">0" not in cond.replace(" ", ""):
                continue
            control_var = self._extract_control_variable(cond)
            if not control_var:
                continue
            body = self._extract_statement_or_block_after_header(request.source_code, match.end())
            if re.search(r"\w+\s*\[.*\]\s*=\s*\w+\s*\[.*\]", body) and not self._has_update_for_var(body, control_var):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.sort.insertion.missing_decrement",
                    source="ClangAST",
                    confidence=0.86,
                    description=f"Insertion-sort shift loop does not appear to decrement '{control_var}'.",
                    location=self._line_from_offset(request, offset),
                    metadata={"tool": "clang++ -ast-dump", "condition": cond, "control_var": control_var},
                ))
        return evidence

    def _detect_bubble_sort_pattern(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        code = self._normalize_code(request.source_code)
        signals = [
            re.search(r"for\s*\(\s*(?:int\s+)?\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\s*-\s*1\s*;", code),
            re.search(r"for\s*\(\s*(?:int\s+)?\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\s*-\s*1\s*-\s*\w+\s*;", code),
            re.search(r"if\s*\(\s*\w+\s*\[\s*\w+\s*\]\s*[<>]\s*\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*\)", code),
            re.search(r"\w+\s*\[\s*\w+\s*\]\s*=\s*\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*;", code),
            re.search(r"\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*=\s*\w+\s*;", code),
        ]
        if sum(bool(x) for x in signals) < 4:
            return []
        ev = [EvidenceInstance(
            evidence_id="ev.sort.bubble.pattern",
            source="ClangAST",
            confidence=0.84,
            description="Source matches a canonical bubble-sort pattern with adjacent comparisons and swaps.",
            location=self._find_line(request, "for"),
            metadata={"tool": "clang++ -ast-dump", "pattern": "bubble_sort"},
        )]
        if re.search(r"if\s*\(\s*\w+\s*\[\s*\w+\s*\]\s*<\s*\w+\s*\[\s*\w+\s*\+\s*1\s*\]\s*\)", code):
            ev.append(EvidenceInstance(
                evidence_id="ev.sort.bubble.wrong_order",
                source="ClangAST",
                confidence=0.82,
                description="Bubble sort swaps when the left element is smaller than the right one, which typically produces descending order.",
                location=self._find_line(request, "if"),
                metadata={"tool": "clang++ -ast-dump", "pattern": "descending_swap"},
            ))
        return ev

    def _detect_binary_search_pattern(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        code = self._normalize_code(request.source_code)
        signals = [
            re.search(r"while\s*\(\s*\w+\s*<=\s*\w+\s*\)", code),
            re.search(r"(?:int|auto)\s+\w+\s*=\s*\w+\s*\+\s*\(\s*\w+\s*-\s*\w+\s*\)\s*/\s*2\s*;", code),
            re.search(r"\w+\s*\[\s*\w+\s*\]\s*==\s*\w+", code),
            re.search(r"\w+\s*=\s*\w+\s*\+\s*1\s*;", code),
            re.search(r"\w+\s*=\s*\w+\s*-\s*1\s*;", code),
        ]
        if sum(bool(x) for x in signals) < 4:
            return []
        return [EvidenceInstance(
            evidence_id="ev.search.binary.pattern",
            source="ClangAST",
            confidence=0.84,
            description="Source matches an iterative binary-search pattern with low/high bounds and midpoint updates.",
            location=self._find_line(request, "while"),
            metadata={"tool": "clang++ -ast-dump", "pattern": "binary_search"},
        )]

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
            ast = result.stdout + result.stderr
            if result.exit_code != 0:
                return evidence
            evidence.extend(self._detect_loop_boundary_issues(request, ast))
            evidence.extend(self._detect_array_index_issues(request, ast))
            evidence.extend(self._detect_pointer_issues(request, ast))
            evidence.extend(self._detect_memory_issues(request))
            evidence.extend(self._detect_return_issues(request))
            evidence.extend(self._detect_while_progress_issues(request, ast))
            evidence.extend(self._detect_recursion_issues(request, ast))
            evidence.extend(self._detect_insertion_sort_pattern(request, ast))
            evidence.extend(self._detect_insertion_sort_bugs(request, ast))
            evidence.extend(self._detect_bubble_sort_pattern(request))
            evidence.extend(self._detect_binary_search_pattern(request))
            return evidence


class ClangStaticAnalyzer(Analyzer):
    STATIC_WARNING_MAP = [
        (re.compile(r"Dereference of null pointer|null dereference|member access within null pointer", re.I), "ev.pointer.clang_null", "Static analyzer reports a possible null dereference.", 0.96),
        (re.compile(r"Use of memory after it is freed|use-after-free", re.I), "ev.memory.release_then_use", "Static analyzer reports use after release.", 0.96),
        (re.compile(r"Potential leak|leak of", re.I), "ev.memory.static_leak", "Static analyzer reports a possible resource leak.", 0.92),
        (re.compile(r"Assigned value is garbage|uninitialized", re.I), "ev.uninitialized.value", "Static analyzer reports possible uninitialized value use.", 0.80),
        (re.compile(r"missing return|control reaches end|does not return", re.I), "ev.function.warn_nonvoid", "Compiler warns about missing return in non-void function.", 0.90),
    ]

    COMPILER_WARNING_MAP = [
        (re.compile(r"control reaches end of non-void function|non-void function does not return", re.I), "ev.function.warn_nonvoid", "Compiler warns about missing return in a non-void function.", 0.92),
        (re.compile(r"variable .* is uninitialized|uninitialized", re.I), "ev.uninitialized.value", "Compiler warns about possible uninitialized value use.", 0.78),
        (re.compile(r"array index .* is past the end|array index .* out of bounds", re.I), "ev.array.index.size_access", "Compiler warns about a possible out-of-bounds array index.", 0.88),
    ]

    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=10.0)

    def _parse_location(self, request: DiagnosticRequest, output: str) -> SourceLocation:
        match = re.search(r":(\d+):(\d+):\s+(?:warning|error):", output)
        if match:
            return SourceLocation(request.file_path, int(match.group(1)), int(match.group(1)), int(match.group(2)), int(match.group(2)))
        return SourceLocation(request.file_path)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            src.write_text(request.source_code, encoding="utf-8")
            commands = [
                ("clang++ --analyze", ["clang++", "--analyze", "-std=c++23", str(src)] + request.compiler_flags, self.STATIC_WARNING_MAP),
                ("clang++ compiler warnings", ["clang++", "-std=c++23", "-Wall", "-Wextra", "-Wpedantic", "-fsyntax-only", str(src)] + request.compiler_flags, self.COMPILER_WARNING_MAP),
            ]
            evidence: List[EvidenceInstance] = []
            seen: set[tuple[str, object, object]] = set()
            for tool_name, command, warning_map in commands:
                result = self.runner.run(command, cwd=workdir, timeout_seconds=10.0)
                if not result.available:
                    continue
                output = result.stdout + result.stderr
                for regex, evidence_id, description, confidence in warning_map:
                    if regex.search(output):
                        loc = self._parse_location(request, output)
                        dedupe_key = (evidence_id, getattr(loc, "start_line", None), getattr(loc, "start_col", None))
                        if dedupe_key in seen:
                            continue
                        seen.add(dedupe_key)
                        evidence.append(EvidenceInstance(
                            evidence_id=evidence_id,
                            source="ClangStaticAnalyzer",
                            confidence=confidence,
                            description=description,
                            location=loc,
                            metadata={"tool": tool_name, "raw": output[-2000:]},
                        ))
            return evidence


class ClangTidyAnalyzer(Analyzer):
    CHECKS = "-*,bugprone-*,cppcoreguidelines-*,clang-analyzer-*"

    def __init__(self, runner: ToolRunner | None = None) -> None:
        self.runner = runner or ToolRunner(timeout_seconds=10.0)

    def _parse_location(self, request: DiagnosticRequest, output: str) -> SourceLocation:
        match = re.search(r":(\d+):(\d+):\s+(?:warning|error):", output)
        if match:
            return SourceLocation(request.file_path, int(match.group(1)), int(match.group(1)), int(match.group(2)), int(match.group(2)))
        return SourceLocation(request.file_path)

    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp)
            src = workdir / request.file_path
            src.write_text(request.source_code, encoding="utf-8")
            command = [
                "clang-tidy",
                str(src),
                f"-checks={self.CHECKS}",
                "--",
                "-std=c++23",
            ] + request.compiler_flags
            result = self.runner.run(command, cwd=workdir, timeout_seconds=10.0)
            if not result.available:
                return []
            output = result.stdout + result.stderr
            evidence: List[EvidenceInstance] = []
            if re.search(r"bugprone-[\w-]*use-after-move|use after move", output, re.I):
                evidence.append(EvidenceInstance("ev.move.use_after_move", "clang-tidy", 0.86, "clang-tidy reports possible use after move.", self._parse_location(request, output), {"raw": output[-2000:]}))
            if re.search(r"cppcoreguidelines-[\w-]*virtual[\w-]*destructor|virtual destructor", output, re.I):
                evidence.append(EvidenceInstance("ev.oop.delete_base_no_virtual", "clang-tidy", 0.88, "clang-tidy reports a polymorphic base class without virtual destructor.", self._parse_location(request, output), {"raw": output[-2000:]}))
            if re.search(r"bugprone-[\w-]*format|clang-diagnostic-format|format string|printf format", output, re.I):
                evidence.append(EvidenceInstance("ev.format.printf_type_mismatch", "clang-tidy", 0.82, "clang-tidy reports possible format string issue.", self._parse_location(request, output), {"raw": output[-2000:]}))
            return evidence
