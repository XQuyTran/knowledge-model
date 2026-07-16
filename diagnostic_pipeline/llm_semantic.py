import json
import logging
import os
import re
from typing import Any, List

from openai import OpenAI

from .interfaces import FeedbackLLM, SemanticAnalyzer
from .models import DiagnosticRequest, EvidenceInstance, SemanticNote
from .prompt_builders import build_feedback_prompts, build_semantic_analysis_prompts

logger = logging.getLogger("diagnostic_pipeline.llm")


def _resolve_model_name() -> str:
    model = (
        os.getenv("AZURE_OPENAI_DEPLOYMENT")
        or os.getenv("OPENAI_MODEL")
        or os.getenv("LLM_MODEL")
        or os.getenv("CLAUDE_LOCAL_MODEL")
    )
    if model:
        return model
    # Local `claude` CLI picks its own default model; return a harmless placeholder
    # (ClaudeCLIClient only forwards --model for real claude-* names).
    if os.getenv("USE_CLAUDE_LOCAL", "false").lower() in {"1", "true", "yes"}:
        return "claude-local"
    raise RuntimeError(
        "Missing LLM model/deployment configuration. "
        "Set AZURE_OPENAI_DEPLOYMENT for Azure or OPENAI_MODEL/LLM_MODEL for OpenAI."
    )


def _max_output_tokens() -> int:
    # Responses default (64k) both wastes budget and 402s on metered/free tiers for a
    # response that is only a small JSON object. Cap it; override via env if ever needed.
    return int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "2000"))


def _parse_json_object(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Model response is not valid JSON: {content[:500]}")


def _notes_from_payload(payload: dict[str, Any]) -> List[SemanticNote]:
    notes: List[SemanticNote] = []
    for item in payload.get("semantic_notes", []):
        notes.append(
            SemanticNote(
                claim=str(item.get("claim", "")),
                confidence=float(item.get("confidence", 0.0)),
                supporting_lines=[
                    int(x) for x in item.get("supporting_lines", []) if isinstance(x, (int, float))
                ],
            )
        )
    return notes


def _feedback_text_from_payload(payload: dict[str, Any]) -> str:
    lines = [
        "Diagnosis: ", payload.get("diagnosis", ""), "\n",
        "Why this is wrong: ", payload.get("why_wrong", ""), "\n",
        "Consequence: ", payload.get("consequence", ""), "\n",
        "Next repair step: ", payload.get("next_repair_step", ""),
    ]
    actions = payload.get("repair_actions", [])
    if actions:
        lines.extend(["", "Candidate actions"])
        lines.extend([f"- {action}" for action in actions])
    return "".join(lines)


def analyze_and_generate_feedback(
    llm_client,
    request: DiagnosticRequest,
    evidence: List[EvidenceInstance],
    candidate_bugs: List[str],
    concept_ids: List[str],
    bug_id,
    feedback_evidence: List[EvidenceInstance],
    explanation,
    repair_plan,
) -> tuple[List[SemanticNote], str]:
    """Single LLM round-trip returning (semantic_notes, feedback_text).

    Merges the former semantic + feedback calls. `feedback_evidence` is the
    evidence set the feedback stage would have used (top_bug's evidence, or all
    evidence when there is no confident bug); it's unioned with the analysis
    evidence so the model sees both.
    """
    from .prompt_builders import build_combined_prompts

    merged_evidence = list({e.evidence_id: e for e in [*evidence, *feedback_evidence]}.values())
    system_prompt, user_prompt, schema_hint = build_combined_prompts(
        request, bug_id, merged_evidence, candidate_bugs, concept_ids, explanation, repair_plan
    )
    response = llm_client.responses.create(
        model=_resolve_model_name(),
        instructions=system_prompt + "\nReturn strictly valid JSON that follows this schema hint:\n" + schema_hint,
        input=user_prompt,
        max_output_tokens=_max_output_tokens(),
    )
    payload = _parse_json_object(response.output_text or "{}")
    return _notes_from_payload(payload), _feedback_text_from_payload(payload)


class BoundedLLMSemanticAnalyzer(SemanticAnalyzer):
    """Semantic analyzer backed directly by the official OpenAI client.

    This version intentionally removes the old project-specific LLMClient wrapper
    dependency and does not use heuristic fallback notes. If the LLM call fails,
    the exception is propagated to the caller so the pipeline can decide how to
    handle it.
    """

    def __init__(self, llm_client: OpenAI):
        if llm_client is None:
            raise ValueError("BoundedLLMSemanticAnalyzer requires a direct OpenAI client instance.")
        self.llm_client = llm_client

    def analyze(
        self,
        request: DiagnosticRequest,
        evidence: List[EvidenceInstance],
        candidate_bugs: List[str],
        concept_ids: List[str],
    ) -> List[SemanticNote]:
        system_prompt, user_prompt, schema_hint = build_semantic_analysis_prompts(
            request, evidence, candidate_bugs, concept_ids
        )
        response = self.llm_client.responses.create(
            model=_resolve_model_name(),
            instructions=system_prompt + "\nReturn strictly valid JSON that follows this schema hint:\n" + schema_hint,
            input=user_prompt,
            max_output_tokens=_max_output_tokens(),
        )
        payload = _parse_json_object(response.output_text or "{}")
        notes = _notes_from_payload(payload)
        logger.info(
            "llm.semantic.notes_generated",
            extra={"note_count": len(notes), "candidate_count": len(candidate_bugs)},
        )
        return notes


class EvidenceBoundFeedbackLLM(FeedbackLLM):
    """Feedback generator backed directly by the official OpenAI client.

    This version intentionally removes the old project-specific LLMClient wrapper
    dependency and does not use the legacy text fallback.
    """

    def __init__(self, llm_client: OpenAI):
        if llm_client is None:
            raise ValueError("EvidenceBoundFeedbackLLM requires a direct OpenAI client instance.")
        self.llm_client = llm_client

    def generate_feedback(self, request, bug_id, evidence, explanation, repair_plan, semantic_notes) -> str:
        system_prompt, user_prompt, schema_hint = build_feedback_prompts(
            request, bug_id, evidence, explanation, repair_plan, semantic_notes
        )
        response = self.llm_client.responses.create(
            model=_resolve_model_name(),
            instructions=system_prompt + "\nReturn strictly valid JSON that follows this schema hint:\n" + schema_hint,
            input=user_prompt,
            max_output_tokens=_max_output_tokens(),
        )
        payload = _parse_json_object(response.output_text or "{}")
        text = _feedback_text_from_payload(payload)
        logger.info(
            "llm.feedback.generated",
            extra={"chars": len(text), "has_bug": bug_id is not None},
        )
        return text
