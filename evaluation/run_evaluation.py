#!/usr/bin/env python3
"""
So sánh hiệu quả giữa:
  A) Hệ thống hybrid (Rule-based + LLM)  — DiagnosticPipeline
  B) LLM-only                             — Gọi LLM trực tiếp để chẩn đoán

Kết quả xuất ra terminal + file JSON + Markdown report.
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from evaluation.benchmark_cases import BENCHMARK_CASES
from diagnostic_pipeline import DiagnosticRequest, TestCase
from diagnostic_pipeline.pipeline import DiagnosticPipeline
from diagnostic_pipeline.llm_client import OpenAICompatibleLLMClient


REPORT_DIR = Path(__file__).parent / "results"


def build_hybrid_report(case: dict) -> dict:
    pipe = DiagnosticPipeline()
    request = DiagnosticRequest(
        problem_statement=case["problem"],
        source_code=case["source_code"],
        test_cases=[TestCase(**tc) for tc in case["test_cases"]],
    )
    start = time.time()
    report = pipe.diagnose(request)
    elapsed = time.time() - start

    detected_bug = report.top_bug.bug_id if report.top_bug else None
    detected = detected_bug == case["expected_bug"] if case["expected_bug"] else detected_bug is None

    return {
        "detected_bug": detected_bug,
        "confidence": round(report.top_bug.score, 3) if report.top_bug else 0,
        "detected": detected,
        "feedback": report.natural_language_feedback[:500],
        "evidence_count": len(report.evidence),
        "elapsed_seconds": round(elapsed, 2),
    }


def build_llm_only_report(case: dict) -> dict:
    try:
        llm = OpenAICompatibleLLMClient.from_env()
    except RuntimeError:
        return {"error": "LLM not configured; set LLM environment variables"}

    prompt = f"""You are a code diagnostic expert. Analyze the following C++ program.

Problem: {case['problem']}

```cpp
{case['source_code']}
```

Identify if there is a bug. Return JSON:
{{"has_bug": bool, "bug_type": "string or null", "diagnosis": "string", "next_step": "string"}}
"""

    start = time.time()
    try:
        response = llm.complete_json("You are a code diagnostic expert. Return JSON only.", prompt, '{"has_bug": bool, "bug_type": "string or null", "diagnosis": "string", "next_step": "string"}')
        elapsed = time.time() - start
        detected_bug = response.get("bug_type")
        detected = detected_bug == case["expected_bug"] if case["expected_bug"] else detected_bug is None
        return {
            "detected_bug": detected_bug,
            "confidence": 0,
            "detected": detected,
            "feedback": response.get("diagnosis", "")[:500],
            "evidence_count": 0,
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(BENCHMARK_CASES)
    hybrid_results = []
    llm_only_results = []

    print(f"=== Chạy đánh giá trên {total} cases ===\n")

    for i, case in enumerate(BENCHMARK_CASES, 1):
        print(f"[{i}/{total}] {case['title']} ... ", end="", flush=True)

        hr = build_hybrid_report(case)
        hybrid_results.append({"case_id": case["id"], **hr})

        lr = build_llm_only_report(case)
        llm_only_results.append({"case_id": case["id"], **lr})

        hr_icon = "✓" if hr["detected"] else "✗"
        lr_icon = "✓" if lr.get("detected") else "✗" if "detected" in lr else "?"
        print(f"Hybrid={hr_icon} LLM-only={lr_icon}")

    # --- Thống kê ---
    hybrid_acc = sum(1 for r in hybrid_results if r.get("detected"))
    llm_acc = sum(1 for r in llm_only_results if r.get("detected"))
    hybrid_avg_time = sum(r["elapsed_seconds"] for r in hybrid_results) / total
    llm_avg_time = sum(r.get("elapsed_seconds", 0) for r in llm_only_results if "elapsed_seconds" in r) / total

    report_md = f"""# Evaluation Report — Hybrid vs LLM-only

## Summary

| Metric | Hybrid (Rule + LLM) | LLM-only |
|--------|--------------------:|---------:|
| Detection Accuracy | {hybrid_acc}/{total} ({100*hybrid_acc/total:.0f}%) | {llm_acc}/{total} ({100*llm_acc/total:.0f}%) |
| Avg Time (s) | {hybrid_avg_time:.2f} | {llm_avg_time:.2f} |

## Per-Case Detail

| Case | Expected | Hybrid | LLM-only |
|------|----------|--------|----------|
"""
    for i, case in enumerate(BENCHMARK_CASES):
        h = hybrid_results[i]
        l = llm_only_results[i]
        report_md += f"| {case['id']} | {case['expected_bug'] or 'None'} | {h['detected_bug'] or 'None'} ({'✓' if h['detected'] else '✗'}) | {l.get('detected_bug') or 'None'} ({'✓' if l.get('detected') else '✗'}) |\n"

    report_md += "\n## Notes\n- LLM-only requires valid LLM environment variables.\n- Hybrid runs fully offline for static analysis.\n"

    print("\n" + "=" * 60)
    print(report_md)

    report_path = REPORT_DIR / "evaluation_report.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"Report saved to {report_path}")

    json_path = REPORT_DIR / "evaluation_results.json"
    json_path.write_text(json.dumps({
        "hybrid": hybrid_results,
        "llm_only": llm_only_results,
        "summary": {
            "hybrid_accuracy": f"{hybrid_acc}/{total}",
            "llm_accuracy": f"{llm_acc}/{total}",
            "hybrid_avg_time_s": hybrid_avg_time,
            "llm_avg_time_s": llm_avg_time,
        }
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to {json_path}")


if __name__ == "__main__":
    main()
