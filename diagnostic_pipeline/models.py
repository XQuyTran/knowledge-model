from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SourceLocation:
    file_path: str = "main.cpp"
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    column_start: Optional[int] = None
    column_end: Optional[int] = None


@dataclass
class TestCase:
    name: str
    input_data: str = ""
    expected_output: str = ""
    timeout_seconds: float = 2.0


@dataclass
class ProblemKnowledge:
    problem_id: str
    title: str
    description: str
    category: str
    algorithm: str
    data_structures: List[str]
    difficulty: str
    common_bugs: List[str]
    correct_code: str
    expected_output: str
    source: str

    @property
    def algorithm_key(self) -> str:
        return f"algorithm.{self.algorithm.lower().replace(' ', '_')}"

    @property
    def category_key(self) -> str:
        return f"category.{self.category.lower().replace(' ', '_')}"

    def matches_statement(self, statement: str) -> float:
        score = 0.0
        s_lower = statement.lower()
        for keyword in [self.algorithm, self.category] + self.data_structures:
            if keyword.lower() in s_lower:
                score += 0.25
        title_words = set(self.title.lower().split())
        statement_words = set(s_lower.split())
        common = title_words & statement_words
        if common:
            score += 0.1 * len(common)
        return min(1.0, score)


@dataclass
class DiagnosticRequest:
    problem_statement: str
    source_code: str
    language: str = "cpp"
    file_path: str = "main.cpp"
    test_cases: List[TestCase] = field(default_factory=list)
    compiler_flags: List[str] = field(default_factory=list)
    enable_sanitizers: bool = True
    problem_id: Optional[str] = None


@dataclass
class ToolResult:
    tool_name: str
    available: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceInstance:
    evidence_id: str
    source: str
    confidence: float
    description: str
    location: Optional[SourceLocation] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SemanticNote:
    claim: str
    confidence: float
    supporting_lines: List[int] = field(default_factory=list)
    causal_chain: List[str] = field(default_factory=list)


@dataclass
class RuleHit:
    rule_id: str
    bug_ids: List[str]
    matched_evidence_ids: List[str]
    matched_concept_ids: List[str]
    confidence: float


@dataclass
class BugCandidate:
    bug_id: str
    score: float
    rule_hits: List[RuleHit] = field(default_factory=list)
    evidence: List[EvidenceInstance] = field(default_factory=list)


@dataclass
class ExplanationStep:
    name: str
    text: str
    step_kind: str = "repair"


@dataclass
class ExplanationSelection:
    template_id: str
    name: str
    steps: List[ExplanationStep]


@dataclass
class RepairStep:
    step_id: str
    name: str
    description: str
    order: int
    location: Optional[SourceLocation] = None


@dataclass
class RepairPlanSelection:
    plan_id: str
    name: str
    steps: List[RepairStep]
    actions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass
class DiagnosticReport:
    top_bug: Optional[BugCandidate]
    alternatives: List[BugCandidate]
    explanation: Optional[ExplanationSelection]
    repair_plan: Optional[RepairPlanSelection]
    natural_language_feedback: str
    evidence: List[EvidenceInstance]
    semantic_notes: List[SemanticNote]
    matched_problems: List[ProblemKnowledge] = field(default_factory=list)
    debug: Dict[str, Any] = field(default_factory=dict)
