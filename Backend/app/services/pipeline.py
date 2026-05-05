from datetime import datetime

from app.agents.bug_report_agent import BugReportAgent
from app.agents.github_agent import GitHubAgent
from app.agents.log_parser import LogParserAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.tagging_agent import TaggingAgent
from app.agents.test_generation_agent import TestGenerationAgent
from app.services.evaluation import evaluate_result
from app.services.memory_store import attach_issue, get_error_group, update_error_group
from app.services.rule_classifier import classify_error
from app.services.tracing import trace_span


def safe_run(agent, input_data):
    agent_name = agent.__class__.__name__
    retry_count = 0

    try:
        with trace_span(agent_name, input_data=input_data) as span:
            output = agent.run(input_data)
            retry_count = int(output.get("retry_count", 0)) if isinstance(output, dict) else 0
            span["retry_count"] = retry_count

        return {
            "agent": agent_name,
            "status": "success",
            "retry_count": retry_count,
            "output": output,
        }

    except Exception as exc:
        return {
            "agent": agent_name,
            "status": "failed",
            "retry_count": retry_count,
            "error": str(exc),
            "output": {},
        }


def run_pipeline(
    log_text: str,
    create_github_issue: bool = True,
    record_memory: bool = True,
):
    trace = []

    if not log_text.strip():
        return {"status": "error", "message": "Empty log"}

    rule_error_type, rule_classification = classify_error(log_text)

    parser = LogParserAgent()
    parsed = safe_run(parser, log_text)
    trace.append(parsed)

    root_agent = RootCauseAgent()
    root = safe_run(root_agent, parsed.get("output", {}))
    trace.append(root)

    root_output = root.get("output", {})
    root_data = root_output.get("analysis", {})
    root_cause = root_data.get("root_cause") or log_text[:200]
    error_type = root_data.get("error_type") or rule_error_type
    classification = root_data.get("classification") or rule_classification

    bug_agent = BugReportAgent()
    report = safe_run(bug_agent, {"analysis": root_data})
    trace.append(report)

    final_report = report.get("output", {})
    final_report["classification"] = classification
    final_report["error_type"] = error_type
    final_report["root_cause"] = root_cause
    final_report["fix_steps"] = root_data.get("fix_steps", [])
    final_report["recovered"] = root_output.get("recovered", False)
    final_report["analysis_source"] = root_data.get("source", "unknown")

    tagger = TaggingAgent()
    tag_result = safe_run(tagger, root_data)
    trace.append(tag_result)
    final_report["tags"] = tag_result.get("output", []) or ["general"]

    test_agent = TestGenerationAgent()
    test_result = safe_run(test_agent, root_data)
    trace.append(test_result)
    final_report["regression_test"] = test_result.get("output", {})

    if record_memory:
        key, group = update_error_group(error_type, root_cause)
        final_report["group"] = key
        final_report["occurrences"] = group["count"]
    else:
        key = None
        final_report["group"] = None
        final_report["occurrences"] = 0

    if record_memory and create_github_issue and classification == "Critical Bug":
        github = GitHubAgent()
        latest_group = get_error_group(key)

        if not latest_group.get("issue_url"):
            with trace_span("GitHubAgent.create_issue", input_data=final_report):
                issue_url = github.create_issue(
                    title=f"[{error_type}] Error detected",
                    body=f"Error Type: {error_type}\n\nRoot Cause:\n{root_cause}",
                )
            attach_issue(key, issue_url)
            latest_group = get_error_group(key)

        final_report["issue_url"] = latest_group.get("issue_url")

    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "trace": trace,
        "final_report": final_report,
    }
    result["evaluation"] = evaluate_result(result)
    return result
