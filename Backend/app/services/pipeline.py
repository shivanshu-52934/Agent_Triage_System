from app.agents.log_parser import LogParserAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.bug_report_agent import BugReportAgent
from app.agents.github_agent import GitHubAgent
from app.agents.tagging_agent import TaggingAgent

from app.services.memory_store import (
    update_error_group,
    attach_issue,
    get_error_group
)

from app.services.evaluation import evaluate_result

import time
from datetime import datetime


# 🔥 STRONG RULE-BASED CLASSIFIER
def classify_error(log_text):
    text = log_text.lower()

    if "500" in text or "internal server error" in text:
        return "Backend Error", "Critical Bug"

    if "timeout" in text:
        return "Performance Issue", "Warning"

    if "database" in text:
        return "Database Issue", "Critical Bug"

    if "memory" in text or "cuda" in text:
        return "Memory Error", "Critical Bug"

    return "Unknown", "Info"


def safe_run(agent, input_data):
    try:
        start = time.time()
        output = agent.run(input_data)
        duration = round(time.time() - start, 2)

        return {
            "agent": agent.__class__.__name__,
            "status": "success",
            "duration": duration,
            "output": output,
        }

    except Exception as e:
        print(f"🔥 ERROR in {agent.__class__.__name__}: {str(e)}")
        return {
            "agent": agent.__class__.__name__,
            "status": "failed",
            "error": str(e),
            "output": {}
        }


def run_pipeline(log_text: str):
    trace = []

    if not log_text.strip():
        return {"status": "error", "message": "Empty log"}

    # 🔥 STEP 0 — RULE CLASSIFICATION (NEW)
    error_type, classification = classify_error(log_text)

    # STEP 1 — PARSER
    parser = LogParserAgent()
    parsed = safe_run(parser, log_text)
    trace.append(parsed)

    # STEP 2 — ROOT CAUSE (OPTIONAL)
    root_agent = RootCauseAgent()
    root = safe_run(root_agent, parsed.get("output", {}))
    trace.append(root)

    root_data = root.get("output", {}).get("analysis", {})

    # 🔥 FALLBACK IF LLM FAILS
    root_cause = root_data.get("root_cause") or log_text[:200]

    # STEP 3 — BUG REPORT
    bug_agent = BugReportAgent()
    report = safe_run(bug_agent, {"analysis": root_data})
    trace.append(report)

    final_report = report.get("output", {})

    final_report["classification"] = classification
    final_report["error_type"] = error_type
    final_report["root_cause"] = root_cause
    final_report["fix_steps"] = root_data.get("fix_steps", [])

    # STEP 4 — TAGGING
    tagger = TaggingAgent()
    try:
        final_report["tags"] = tagger.run(root_data)
    except:
        final_report["tags"] = []

    # STEP 5 — GROUPING (FIXED)
    key, group = update_error_group(error_type, root_cause)

    final_report["group"] = key
    final_report["occurrences"] = group["count"]

    # STEP 6 — GITHUB (FIXED)
    github = GitHubAgent()
    latest_group = get_error_group(key)

    if classification == "Critical Bug":

        if not latest_group.get("issue_url"):
            print("🆕 Creating issue")

            issue_url = github.create_issue(
                title=f"[{error_type}] Error detected",
                body=f"Error Type: {error_type}\n\nRoot Cause:\n{root_cause}"
            )

            attach_issue(key, issue_url)

            latest_group = get_error_group(key)

        else:
            print("📌 Reusing existing issue")

        final_report["issue_url"] = latest_group.get("issue_url")

    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "trace": trace,
        "final_report": final_report
    }