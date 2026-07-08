import logging
import time
from typing import List

from openai import OpenAI

from .clang_analyzers import ClangASTAnalyzer, ClangStaticAnalyzer, ClangTidyAnalyzer
from .evidence_builder import EvidenceBuilder
from .exercise_knowledge_base import get_problem_by_id, find_matching_problems
from .graph_repository import InMemoryGraphRepository
from .interfaces import Analyzer, GraphRepository, SemanticAnalyzer
from .llm_client import build_llm_client_from_env
from .llm_semantic import BoundedLLMSemanticAnalyzer, EvidenceBoundFeedbackLLM
from .local_sandbox import LocalSandboxRunner, SanitizerRunner
from .models import DiagnosticReport, DiagnosticRequest
from .ranking import BugRankingEngine

logger = logging.getLogger("diagnostic_pipeline")


class DiagnosticPipeline:
    def __init__(
        self,
        analyzers: List[Analyzer] | None = None,
        semantic_analyzer: SemanticAnalyzer | None = None,
        graph_repository: GraphRepository | None = None,
        feedback_llm: EvidenceBoundFeedbackLLM | None = None,
        llm_client: OpenAI | None = None,
        min_confidence: float = 0.45,
    ) -> None:
        llm_client = llm_client or build_llm_client_from_env()
        if llm_client is None:
            raise RuntimeError(
                "DiagnosticPipeline now requires a direct OpenAI client configuration. "
                "Set Azure OpenAI or OpenAI environment variables before startup."
            )
        self.llm_client = llm_client
        self.analyzers = analyzers or [
            ClangASTAnalyzer(),
            ClangStaticAnalyzer(),
            ClangTidyAnalyzer(),
            LocalSandboxRunner(),
            SanitizerRunner(),
        ]
        self.semantic_analyzer = semantic_analyzer or BoundedLLMSemanticAnalyzer(llm_client=llm_client)
        self.graph_repository = graph_repository or InMemoryGraphRepository()
        self.feedback_llm = feedback_llm or EvidenceBoundFeedbackLLM(llm_client=llm_client)
        self.evidence_builder = EvidenceBuilder()
        self.ranking_engine = BugRankingEngine()
        self.min_confidence = min_confidence

    def diagnose(self, request: DiagnosticRequest) -> DiagnosticReport:
        pipeline_start = time.time()
        logger.info("pipeline.start", extra={"problem_id": request.problem_id, "has_tests": bool(request.test_cases)})

        matched_problems = find_matching_problems(request.problem_statement, top_n=3)
        problem_rules: List = []
        matched_problem_ids = []
        for p in matched_problems:
            matched_problem_ids.append(p.problem_id)
            problem_rules.extend(self.graph_repository.match_problem_rules(p.problem_id))
        if request.problem_id:
            specific = get_problem_by_id(request.problem_id)
            if specific and specific.problem_id not in matched_problem_ids:
                matched_problems.insert(0, specific)
                problem_rules.extend(self.graph_repository.match_problem_rules(request.problem_id))

        evidence_sets = []
        analyzer_debug = []
        for analyzer in self.analyzers:
            start = time.time()
            logger.info("analyzer.start", extra={"analyzer": analyzer.__class__.__name__})
            try:
                result = analyzer.analyze(request)
                duration_ms = int((time.time() - start) * 1000)
                evidence_sets.append(result)
                analyzer_debug.append({"analyzer": analyzer.__class__.__name__, "evidence_count": len(result), "duration_ms": duration_ms})
                logger.info("analyzer.finish", extra={"analyzer": analyzer.__class__.__name__, "evidence_count": len(result), "duration_ms": duration_ms})
            except Exception as exc:
                duration_ms = int((time.time() - start) * 1000)
                analyzer_debug.append({"analyzer": analyzer.__class__.__name__, "error": str(exc), "duration_ms": duration_ms})
                logger.exception("analyzer.error", extra={"analyzer": analyzer.__class__.__name__, "duration_ms": duration_ms})

        evidence = self.evidence_builder.merge(evidence_sets)
        concepts = self.evidence_builder.infer_concepts(evidence)
        evidence_ids = sorted({item.evidence_id for item in evidence})
        logger.info("pipeline.evidence", extra={"total_evidence": len(evidence), "distinct_ids": len(evidence_ids)})

        rule_hits = self.graph_repository.match_rules(evidence_ids, concepts)
        rule_hits.extend(problem_rules)
        logger.info("pipeline.rules", extra={"rule_hits": len(rule_hits)})

        ranked = self.ranking_engine.rank(rule_hits, evidence)
        top_bug = ranked[0] if ranked and ranked[0].score >= self.min_confidence else None
        candidate_bugs = [candidate.bug_id for candidate in ranked[:5]]
        logger.info("pipeline.ranking", extra={"top_bug": top_bug.bug_id if top_bug else None, "score": top_bug.score if top_bug else None})

        # LLM steps run AFTER detection (top_bug) is complete and are used only for
        # narrative output. A flaky/malformed LLM response must not discard a valid
        # diagnosis, so failures degrade gracefully instead of aborting the pipeline.
        t0 = time.time()
        logger.info("llm.semantic.start", extra={"candidates": candidate_bugs})
        try:
            semantic_notes = self.semantic_analyzer.analyze(request, evidence, candidate_bugs, concepts)
            logger.info("llm.semantic.finish", extra={"duration_ms": int((time.time() - t0) * 1000), "notes": len(semantic_notes)})
        except Exception:
            semantic_notes = []
            logger.exception("llm.semantic.error", extra={"duration_ms": int((time.time() - t0) * 1000)})

        explanation = None
        repair_plan = None
        if top_bug:
            rule_ids = [hit.rule_id for hit in top_bug.rule_hits]
            explanation = self.graph_repository.select_explanation(top_bug.bug_id, rule_ids, concepts)
            repair_plan = self.graph_repository.select_repair_plan(top_bug.bug_id, rule_ids, concepts)
            if repair_plan:
                repair_plan = self._attach_locations(repair_plan, top_bug.evidence)

        t1 = time.time()
        logger.info("llm.feedback.start", extra={"top_bug": top_bug.bug_id if top_bug else None})
        try:
            feedback = self.feedback_llm.generate_feedback(
                request,
                top_bug.bug_id if top_bug else None,
                top_bug.evidence if top_bug else evidence,
                explanation,
                repair_plan,
                semantic_notes,
            )
            logger.info("llm.feedback.finish", extra={"duration_ms": int((time.time() - t1) * 1000), "chars": len(feedback) if feedback else 0})
        except Exception:
            feedback = (
                f"Detected: {top_bug.bug_id}" if top_bug else "No high-confidence bug detected."
            ) + " (LLM feedback unavailable.)"
            logger.exception("llm.feedback.error", extra={"duration_ms": int((time.time() - t1) * 1000)})

        logger.info("pipeline.finish", extra={"duration_ms": int((time.time() - pipeline_start) * 1000), "top_bug": top_bug.bug_id if top_bug else None})
        return DiagnosticReport(
            top_bug=top_bug,
            alternatives=ranked[1:5],
            explanation=explanation,
            repair_plan=repair_plan,
            natural_language_feedback=feedback,
            evidence=evidence,
            semantic_notes=semantic_notes,
            matched_problems=matched_problems,
            debug={
                'analyzers': analyzer_debug,
                'evidence_ids': evidence_ids,
                'concept_ids': concepts,
                'rule_hit_count': len(rule_hits),
                'matched_problems': [p.problem_id for p in matched_problems],
                'llm_client_type': self.llm_client.__class__.__name__,
            },
        )

    def _attach_locations(self, repair_plan, evidence):
        first_location = next((item.location for item in evidence if item.location and item.location.line_start), None)
        if first_location:
            for step in repair_plan.steps:
                if step.location is None:
                    step.location = first_location
        return repair_plan
