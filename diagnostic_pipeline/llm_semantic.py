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
    )
    if not model:
        raise RuntimeError(
            "Missing LLM model/deployment configuration. "
            "Set AZURE_OPENAI_DEPLOYMENT for Azure or OPENAI_MODEL/LLM_MODEL for OpenAI."
        )
    return model


def _parse_json_object(content: str) -> dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Model response is not valid JSON: {content[:500]}")


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
        )
        payload = _parse_json_object(response.output_text or "{}")
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
        )
        payload = _parse_json_object(response.output_text or "{}")
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
        text = "".join(lines)
        logger.info(
            "llm.feedback.generated",
            extra={"chars": len(text), "has_bug": bug_id is not None},
        )
        return text
