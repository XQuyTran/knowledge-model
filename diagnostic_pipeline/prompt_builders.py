
import json
from typing import List

from .models import DiagnosticRequest, EvidenceInstance, ExplanationSelection, RepairPlanSelection

COMMON_SYSTEM_PROMPT = (
    "You are an ontology-grounded programming diagnostic expert. "
    "Your task is to diagnose a student's programming submission using only the provided context. "
    "STRICT RULES: "
    "1. Use only supplied evidence, concepts, candidate bugs, explanation steps, and repair steps. "
    "2. Never invent compiler warnings, runtime failures, bug IDs, concepts, or fixes that are not present in the provided context. "
    "3. If evidence is insufficient, explicitly say that confidence is limited. "
    "4. Explain the causal chain when possible. "
    "5. Keep the explanation educational and concrete. "
    "6. Return JSON only. "
    "Reasoning chain: "
    "Evidence -> Concept -> Diagnostic Rule -> Bug -> Consequence -> Repair Action."
)


def build_semantic_analysis_prompts(
    request: DiagnosticRequest,
    evidence: List[EvidenceInstance],
    candidate_bugs: List[str],
    concept_ids: List[str],
):
    system_prompt = COMMON_SYSTEM_PROMPT + (
        "Task: "
        "Analyze the semantic mismatch between the problem requirement and the source code. "
        "Use evidence to explain why the candidate bugs may or may not be supported."
    )
    user_payload = {
        'problem_statement': request.problem_statement,
        'source_code': request.source_code,
        'evidence': [
            {
                'evidence_id': e.evidence_id,
                'source': e.source,
                'description': e.description,
                'line_start': e.location.line_start if e.location else None,
            }
            for e in evidence
        ],
        'candidate_bugs': candidate_bugs,
        'concept_ids': concept_ids,
    }
    schema_hint = json.dumps(
        {
            'semantic_notes': [
                {
                    'claim': 'string',
                    'confidence': 0.0,
                    'supporting_lines': [1, 2],
                    'causal_chain': [
                        'Evidence statement',
                        'Concept statement',
                        'Bug consequence statement',
                    ],
                }
            ]
        },
        indent=2,
    )
    return system_prompt, json.dumps(user_payload, indent=2), schema_hint


def build_feedback_prompts(
    request: DiagnosticRequest,
    bug_id: str | None,
    evidence: List[EvidenceInstance],
    explanation: ExplanationSelection | None,
    repair_plan: RepairPlanSelection | None,
    semantic_notes,
):
    system_prompt = COMMON_SYSTEM_PROMPT + (
        "Task: "
        "Generate concise, educational feedback for the student. "
        "Explain what is wrong, why it happens, what consequence it has, and what repair step should come next."
    )
    user_payload = {
        'problem_statement': request.problem_statement,
        'bug_id': bug_id,
        'evidence': [
            {
                'description': e.description,
                'line_start': e.location.line_start if e.location else None,
                'source': e.source,
            }
            for e in evidence
        ],
        'semantic_notes': [note.__dict__ for note in semantic_notes],
        'explanation_steps': [step.__dict__ for step in (explanation.steps if explanation else [])],
        'repair_steps': [
            {
                'order': step.order,
                'description': step.description,
                'line_start': step.location.line_start if step.location else None,
            }
            for step in (repair_plan.steps if repair_plan else [])
        ],
        'repair_actions': repair_plan.actions if repair_plan else [],
    }
    schema_hint = json.dumps(
        {
            'diagnosis': 'string',
            'why_wrong': 'string',
            'consequence': 'string',
            'next_repair_step': 'string',
            'repair_actions': ['string'],
        },
        indent=2,
    )
    return system_prompt, json.dumps(user_payload, indent=2), schema_hint
