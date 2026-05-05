import json
from datetime import datetime
from pathlib import Path

from app.services.evaluation import evaluate_result
from app.services.pipeline import run_pipeline


BASE_DIR = Path(__file__).resolve().parent
SAMPLES_FILE = BASE_DIR / "synthetic_logs.json"
REPORT_FILE = BASE_DIR / "eval_report.json"


def run_eval():
    samples = json.loads(SAMPLES_FILE.read_text(encoding="utf-8"))
    cases = []

    for sample in samples:
        result = run_pipeline(
            sample["log"],
            create_github_issue=False,
            record_memory=False,
        )
        evaluation = evaluate_result(result, sample["expected"])
        report = result.get("final_report", {})

        cases.append(
            {
                "id": sample["id"],
                "expected": sample["expected"],
                "actual": {
                    "title": report.get("title"),
                    "error_type": report.get("error_type"),
                    "classification": report.get("classification"),
                    "analysis_source": report.get("analysis_source"),
                },
                "evaluation": evaluation,
            }
        )

    total = len(cases)
    title_matches = sum(1 for case in cases if case["evaluation"].get("title_match"))
    classification_matches = sum(
        1 for case in cases if case["evaluation"].get("classification_match")
    )
    perfect_matches = sum(1 for case in cases if case["evaluation"].get("score") == 1)

    report = {
        "generated_at": datetime.now().isoformat(),
        "total_samples": total,
        "metrics": {
            "title_precision": round(title_matches / total, 3),
            "classification_precision": round(classification_matches / total, 3),
            "exact_case_precision": round(perfect_matches / total, 3),
        },
        "cases": cases,
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(run_eval(), indent=2))
