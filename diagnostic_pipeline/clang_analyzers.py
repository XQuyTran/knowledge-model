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

    def _find_line(self, request: DiagnosticRequest, token: str) -> SourceLocation:
        for idx, line in enumerate(request.source_code.splitlines(), start=1):
            if token in line:
                return SourceLocation(request.file_path, idx, idx)
        return SourceLocation(request.file_path)

    def _has_new_without_delete(self, code: str) -> bool:
        if 'new' not in code:
            return False
        no_new = re.sub(r'//.*', '', re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL))
        if re.search(r'\bnew\b', no_new) and not re.search(r'\bdelete\b', no_new):
            return True
        return False

    def _has_missing_return(self, code: str) -> bool:
        no_comment = re.sub(r'//.*', '', re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL))
        func_pattern = re.compile(r'(?:int|float|double|char|bool|long|short|unsigned|size_t|void\s*\*|std::\w+)\s+(\w+)\s*\([^)]*\)\s*\{')
        for match in func_pattern.finditer(no_comment):
            func_name = match.group(1)
            if func_name == 'main':
                continue
            brace_start = match.end() - 1
            rest = no_comment[brace_start:]
            depth = 0
            body = ''
            for ch in rest:
                if ch == '{': depth += 1
                elif ch == '}': depth -= 1
                if depth == 0 and ch == '}': break
                body += ch
            if not re.search(r'\breturn\b', body):
                return True
        return False

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
            if self._has_new_without_delete(request.source_code):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.memory.alloc_without_release",
                    source="ClangAST",
                    confidence=0.80,
                    description="Code uses 'new' without matching 'delete', suggesting a memory leak.",
                    location=self._find_line(request, "new"),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
            if self._has_missing_return(request.source_code):
                evidence.append(EvidenceInstance(
                    evidence_id="ev.function.warn_nonvoid",
                    source="ClangAST",
                    confidence=0.82,
                    description="A non-void function body lacks a return statement, causing undefined behavior.",
                    location=self._find_line(request, "{"),
                    metadata={"tool": "clang++ -ast-dump"},
                ))
            if 'WhileStmt' in ast and re.search(r'\bwhile\s*\(', request.source_code):
                for_token = re.search(r'\bwhile\s*\(([^)]+)\)', request.source_code)
                body_lines = request.source_code.splitlines()
                has_update = any(re.search(r'\+\+|--|\+=|-=|\w+\s*=\s*\w+\s*[-+*/]\s*\w+', line) for line in body_lines)
                if not has_update:
                    evidence.append(EvidenceInstance(
                        evidence_id="ev.loop.no_progress",
                        source="ClangAST",
                        confidence=0.75,
                        description="A while loop lacks any obvious update to its control variable.",
                        location=self._find_line(request, "while"),
                        metadata={"tool": "clang++ -ast-dump"},
                    ))
            if 'CallExpr' in ast:
                func_calls = re.findall(r"CallExpr.*?'(\w+)'", ast)
                func_defs = re.findall(r"FunctionDecl.*?'(\w+)'", ast)
                for func_name in func_defs:
                    if func_name == 'main':
                        continue
                    self_calls = [c for c in func_calls if c == func_name]
                    if len(self_calls) >= 1 and func_name in func_calls:
                        no_comment = re.sub(r'//.*', '', re.sub(r'/\*.*?\*/', '', request.source_code, flags=re.DOTALL))
                        if func_name in no_comment and not re.search(r'\bif\b', no_comment[:no_comment.find(func_name) + no_comment[no_comment.find(func_name):].find('(')]):
                            body_start = no_comment.find(func_name)
                            brace_start = no_comment.find('{', body_start)
                            if brace_start > 0:
                                rest = no_comment[brace_start:]
                                depth = 0
                                body = ''
                                for ch in rest:
                                    if ch == '{': depth += 1
                                    elif ch == '}': depth -= 1
                                    if depth == 0 and ch == '}': break
                                    body += ch
                                if not re.search(r'\bif\b', body):
                                    evidence.append(EvidenceInstance(
                                        evidence_id="ev.recursion.no_progress",
                                        source="ClangAST",
                                        confidence=0.78,
                                        description=f"Function '{func_name}' calls itself recursively without a base-case guard.",
                                        location=self._find_line(request, func_name),
                                        metadata={"tool": "clang++ -ast-dump"},
                                    ))
            return evidence


class ClangStaticAnalyzer(Analyzer):
    WARNING_MAP = [
        (re.compile(r"Dereference of null pointer|null dereference", re.I), "ev.pointer.clang_null", "Static analyzer reports a possible null dereference.", 0.96),
        (re.compile(r"Use of memory after it is freed|use-after-free", re.I), "ev.memory.release_then_use", "Static analyzer reports use after release.", 0.96),
        (re.compile(r"Potential leak|leak of", re.I), "ev.memory.sanitizer_leak", "Static analyzer reports a possible resource leak.", 0.92),
        (re.compile(r"Assigned value is garbage|uninitialized", re.I), "ev.uninitialized.value", "Static analyzer reports possible uninitialized value use.", 0.80),
        (re.compile(r"missing return|control reaches end|does not return", re.I), "ev.function.warn_nonvoid", "Compiler warns about missing return in non-void function.", 0.90),
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
