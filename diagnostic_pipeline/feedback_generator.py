"""Feedback generation wrapper."""



from typing import List

from .interfaces import FeedbackLLM
from .models import DiagnosticRequest, EvidenceInstance, ExplanationSelection, RepairPlanSelection, SemanticNote


class FeedbackGenerator:
    def __init__(self, llm: FeedbackLLM):
        self.llm = llm

    def generate(
        self,
        request: DiagnosticRequest,
        bug_id: str | None,
        evidence: List[EvidenceInstance],
        explanation: ExplanationSelection | None,
        repair_plan: RepairPlanSelection | None,
        semantic_notes: List[SemanticNote],
    ) -> str:
        return self.llm.generate_feedback(
            request=request,
            bug_id=bug_id,
            evidence=evidence,
            explanation=explanation,
            repair_plan=repair_plan,
            semantic_notes=semantic_notes,
        )
