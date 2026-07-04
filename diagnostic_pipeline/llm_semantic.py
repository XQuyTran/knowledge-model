from __future__ import annotations

from typing import List

from .interfaces import FeedbackLLM, LLMClient, SemanticAnalyzer
from .models import DiagnosticRequest, EvidenceInstance, SemanticNote
from .prompt_builders import build_feedback_prompts, build_semantic_analysis_prompts


class BoundedLLMSemanticAnalyzer(SemanticAnalyzer):
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client

    def analyze(self, request: DiagnosticRequest, evidence: List[EvidenceInstance], candidate_bugs: List[str], concept_ids: List[str]) -> List[SemanticNote]:
        if self.llm_client is None:
            return self._fallback(evidence)
        try:
            system_prompt, user_prompt, schema_hint = build_semantic_analysis_prompts(
                request, evidence, candidate_bugs, concept_ids
            )
            response = self.llm_client.complete_json(system_prompt, user_prompt, schema_hint)
            notes = []
            for item in response.get('semantic_notes', []):
                notes.append(
                    SemanticNote(
                        claim=str(item.get('claim', '')),
                        confidence=float(item.get('confidence', 0.0)),
                        supporting_lines=[
                            int(x) for x in item.get('supporting_lines', []) if isinstance(x, (int, float))
                        ],
                    )
                )
            return notes if notes else self._fallback(evidence)
        except Exception:
            return self._fallback(evidence)

    def _fallback(self, evidence: List[EvidenceInstance]) -> List[SemanticNote]:
        notes: List[SemanticNote] = []
        evidence_ids = {e.evidence_id for e in evidence}
        if {'ev.loop.boundary.le_length', 'ev.array.index.size_access'} & evidence_ids:
            notes.append(
                SemanticNote(
                    'The loop and index expression are likely inconsistent with the valid range of the sequence.',
                    0.72,
                )
            )
        if {'ev.pointer.clang_null', 'ev.pointer.null_check_missing'} & evidence_ids:
            notes.append(
                SemanticNote(
                    'The code appears to use a pointer before proving that it refers to a valid object.',
                    0.70,
                )
            )
        if {'ev.memory.sanitizer_uaf', 'ev.memory.release_then_use'} & evidence_ids:
            notes.append(
                SemanticNote(
                    'The code likely continues using a resource after its lifetime has ended.',
                    0.78,
                )
            )
        return notes


class EvidenceBoundFeedbackLLM(FeedbackLLM):
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm_client = llm_client

    def generate_feedback(self, request, bug_id, evidence, explanation, repair_plan, semantic_notes) -> str:
        if self.llm_client is None:
            return self._fallback(bug_id, evidence, explanation, repair_plan, semantic_notes)
        try:
            system_prompt, user_prompt, schema_hint = build_feedback_prompts(
                request, bug_id, evidence, explanation, repair_plan, semantic_notes
            )
            response = self.llm_client.complete_json(system_prompt, user_prompt, schema_hint)
            lines = [
                'Diagnosis',
                response.get('diagnosis', ''),
                '',
                'Why this is wrong',
                response.get('why_wrong', ''),
                '',
                'Consequence',
                response.get('consequence', ''),
                '',
                'Next repair step',
                response.get('next_repair_step', ''),
            ]
            actions = response.get('repair_actions', [])
            if actions:
                lines.extend(['', 'Candidate actions'])
                lines.extend([f'- {action}' for action in actions])
            return ''.join(lines)
        except Exception:
            return self._fallback(bug_id, evidence, explanation, repair_plan, semantic_notes)

    def _fallback(self, bug_id, evidence, explanation, repair_plan, semantic_notes) -> str:
        if not bug_id:
            return 'No high-confidence diagnosis was found. Add focused tests or inspect the reported compiler/runtime evidence.'
        lines = ['Diagnosis', f'Most likely bug: {bug_id}', '', 'Evidence']
        for item in evidence:
            location = ''
            if item.location and item.location.line_start:
                location = f' at line {item.location.line_start}'
            lines.append(f'- {item.description}{location}')
        if semantic_notes:
            lines.extend(['', 'Semantic analysis'])
            for note in semantic_notes:
                lines.append(f'- {note.claim}')
        if explanation:
            lines.extend(['', 'Why this is wrong'])
            for step in explanation.steps:
                lines.append(f'- {step.text}')
        if repair_plan:
            lines.extend(['', 'Next repair step'])
            for step in sorted(repair_plan.steps, key=lambda s: s.order):
                location = ''
                if step.location and step.location.line_start:
                    location = f' at line {step.location.line_start}'
                lines.append(f'{step.order}. {step.description}{location}')
            if repair_plan.actions:
                lines.extend(['', 'Candidate actions'])
                for action in repair_plan.actions:
                    lines.append(f'- {action}')
        return ''.join(lines)
