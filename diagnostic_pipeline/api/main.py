
import os
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from diagnostic_pipeline import DiagnosticPipeline, DiagnosticRequest, TestCase
from diagnostic_pipeline.exercise_knowledge_base import EXERCISES, get_problem_by_id
from diagnostic_pipeline.graph_repository import InMemoryGraphRepository, Neo4jGraphRepository
from diagnostic_pipeline.llm_client import build_llm_client_from_env

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None


class TestCasePayload(BaseModel):
    name: str = "sample"
    input_data: str = ""
    expected_output: str = ""
    timeout_seconds: float = Field(default=2.0, ge=0.1, le=30.0)


class DiagnoseRequestPayload(BaseModel):
    problem_statement: str = Field(..., min_length=1)
    source_code: str = Field(..., min_length=1)
    language: str = "cpp"
    file_path: str = "main.cpp"
    compiler_flags: List[str] = Field(default_factory=list)
    enable_sanitizers: bool = True
    test_cases: List[TestCasePayload] = Field(default_factory=list)
    problem_id: Optional[str] = None


class DiagnoseResponsePayload(BaseModel):
    top_bug: Optional[str]
    confidence: Optional[float]
    feedback: str
    evidence: List[dict[str, Any]]
    semantic_notes: List[dict[str, Any]]
    repair_plan: Optional[dict[str, Any]]
    alternatives: List[dict[str, Any]]
    matched_problems: List[dict[str, Any]]
    debug: dict[str, Any]


def build_graph_repository():
    if os.getenv("USE_NEO4J", "true").lower() not in {"1", "true", "yes"}:
        return InMemoryGraphRepository(), None
    if GraphDatabase is None:
        return InMemoryGraphRepository(), None
    try:
        driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "password")),
        )
        return Neo4jGraphRepository(driver=driver, database=os.getenv("NEO4J_DATABASE", "neo4j")), driver
    except Exception:
        return InMemoryGraphRepository(), None


def build_llm_client():
    if os.getenv("USE_CLAUDE_LOCAL", "false").lower() in {"1", "true", "yes"}:
        from diagnostic_pipeline.claude_cli_client import ClaudeCLIClient
        return ClaudeCLIClient()
    return build_llm_client_from_env()


def build_pipeline():
    graph_repository, driver = build_graph_repository()
    pipeline = DiagnosticPipeline(graph_repository=graph_repository, llm_client=build_llm_client())
    return pipeline, driver


pipeline, neo4j_driver = build_pipeline()

app = FastAPI(title="Diagnostic Pipeline API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_path = Path(__file__).resolve().parents[1] / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_path / "index.html")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_mode": type(pipeline.llm_client).__name__,
        "llm_configured": build_llm_client_from_env() is not None,
        "neo4j_mode": os.getenv("USE_NEO4J", "true"),
    }


@app.get("/exercises")
def list_exercises() -> List[dict[str, Any]]:
    return [
        {
            "problem_id": ex.problem_id,
            "title": ex.title,
            "category": ex.category,
            "algorithm": ex.algorithm,
            "data_structures": ex.data_structures,
            "difficulty": ex.difficulty,
            "source": ex.source,
        }
        for ex in EXERCISES
    ]


@app.get("/exercises/{problem_id}")
def get_exercise(problem_id: str) -> Optional[dict[str, Any]]:
    ex = get_problem_by_id(problem_id)
    if not ex:
        return None
    return {
        "problem_id": ex.problem_id,
        "title": ex.title,
        "description": ex.description,
        "category": ex.category,
        "algorithm": ex.algorithm,
        "data_structures": ex.data_structures,
        "difficulty": ex.difficulty,
        "common_bugs": ex.common_bugs,
        "correct_code": ex.correct_code,
        "expected_output": ex.expected_output,
        "source": ex.source,
    }


@app.post("/diagnose", response_model=DiagnoseResponsePayload)
def diagnose(payload: DiagnoseRequestPayload) -> DiagnoseResponsePayload:
    request = DiagnosticRequest(
        problem_statement=payload.problem_statement,
        source_code=payload.source_code,
        language=payload.language,
        file_path=payload.file_path,
        compiler_flags=payload.compiler_flags,
        enable_sanitizers=payload.enable_sanitizers,
        test_cases=[
            TestCase(
                name=item.name,
                input_data=item.input_data,
                expected_output=item.expected_output,
                timeout_seconds=item.timeout_seconds,
            )
            for item in payload.test_cases
        ],
        problem_id=payload.problem_id,
    )
    report = pipeline.diagnose(request)
    return DiagnoseResponsePayload(
        top_bug=report.top_bug.bug_id if report.top_bug else None,
        confidence=report.top_bug.score if report.top_bug else None,
        feedback=report.natural_language_feedback,
        evidence=[
            {
                "evidence_id": e.evidence_id,
                "source": e.source,
                "confidence": e.confidence,
                "description": e.description,
                "location": e.location.__dict__ if e.location else None,
                "metadata": e.metadata,
            }
            for e in report.evidence
        ],
        semantic_notes=[note.__dict__ for note in report.semantic_notes],
        repair_plan=(
            {
                "plan_id": report.repair_plan.plan_id,
                "name": report.repair_plan.name,
                "steps": [step.__dict__ for step in report.repair_plan.steps],
                "actions": report.repair_plan.actions,
                "constraints": report.repair_plan.constraints,
            }
            if report.repair_plan else None
        ),
        alternatives=[{"bug_id": c.bug_id, "score": c.score} for c in report.alternatives],
        matched_problems=[
            {
                "problem_id": p.problem_id,
                "title": p.title,
                "category": p.category,
                "algorithm": p.algorithm,
                "data_structures": p.data_structures,
                "difficulty": p.difficulty,
                "source": p.source,
            }
            for p in report.matched_problems
        ],
        debug=report.debug,
    )


@app.on_event("shutdown")
def shutdown_event() -> None:
    if neo4j_driver is not None:
        neo4j_driver.close()
