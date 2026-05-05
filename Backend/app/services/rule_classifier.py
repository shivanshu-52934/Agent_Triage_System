def classify_error(log_text: str):
    text = (log_text or "").lower()

    if "assertionerror" in text or "assert " in text:
        return "Test Assertion Failure", "Critical Bug"

    if "modulenotfounderror" in text or "importerror" in text:
        return "Dependency Import Error", "Critical Bug"

    if "connection refused" in text or "connectionerror" in text:
        return "Service Connection Failure", "Critical Bug"

    if "500" in text or "internal server error" in text:
        return "Backend Error", "Critical Bug"

    if "timeout" in text or "timed out" in text:
        return "Performance Issue", "Warning"

    if "database" in text or "sql" in text or "postgres" in text:
        return "Database Issue", "Critical Bug"

    if "memory" in text or "cuda" in text or "outofmemory" in text:
        return "Memory Error", "Critical Bug"

    if "permission denied" in text or "unauthorized" in text or "403" in text:
        return "Authentication Issue", "Critical Bug"

    if "404" in text or "not found" in text:
        return "Routing Error", "Warning"

    if "syntaxerror" in text:
        return "Syntax Error", "Critical Bug"

    if "typeerror" in text:
        return "Type Error", "Critical Bug"

    if "valueerror" in text:
        return "Value Error", "Critical Bug"

    return "Unknown", "Info"


def fallback_analysis(log_text: str, reason: str = "LLM unavailable"):
    error_type, classification = classify_error(log_text)
    root_cause = (
        f"Rule-based fallback detected {error_type.lower()} because {reason}. "
        "Review the failing stack trace and the component named in the log."
    )

    return {
        "classification": classification,
        "error_type": error_type,
        "root_cause": root_cause,
        "fix_steps": [
            "Open the first application stack frame in the failure log",
            "Reproduce the failing path locally with the same input",
            "Patch the failing component and add a regression test",
        ],
        "source": "rule_based_fallback",
    }
