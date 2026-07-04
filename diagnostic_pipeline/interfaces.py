from abc import ABC, abstractmethod
from typing import List

from .models import DiagnosticRequest, EvidenceInstance, ExplanationSelection, RepairPlanSelection, RuleHit, SemanticNote


class Analyzer(ABC):
    @abstractmethod
    def analyze(self, request: DiagnosticRequest) -> List[EvidenceInstance]:
        raise NotImplementedError


class SemanticAnalyzer(ABC):
    @abstractmethod
    def analyze(self, request: DiagnosticRequest, evidence: List[EvidenceInstance], candidate_bugs: List[str], concept_ids: List[str]) -> List[SemanticNote]:
        raise NotImplementedError


class GraphRepository(ABC):
    @abstractmethod
    def match_rules(self, evidence_ids: List[str], concept_ids: List[str]) -> List[RuleHit]:
        raise NotImplementedError

    @abstractmethod
    def select_explanation(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> ExplanationSelection | None:
        raise NotImplementedError

    @abstractmethod
    def select_repair_plan(self, bug_id: str, rule_ids: List[str], concept_ids: List[str]) -> RepairPlanSelection | None:
        raise NotImplementedError


class LLMClient(ABC):
    @abstractmethod
    def complete_json(self, system_prompt: str, user_prompt: str, schema_hint: str) -> dict:
        raise NotImplementedError


class FeedbackLLM(ABC):
    @abstractmethod
    def generate_feedback(self, request, bug_id, evidence, explanation, repair_plan, semantic_notes) -> str:
        raise NotImplementedError
