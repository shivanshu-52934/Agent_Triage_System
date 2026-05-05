ERROR_TYPE_ALIASES = {
    "Backend Error": [
        "backend",
        "http 500",
        "500",
        "internal server",
        "server error",
        "upstream server",
    ],
    "Performance Issue": [
        "performance",
        "timeout",
        "timed out",
        "slow",
        "latency",
    ],
    "Database Issue": [
        "database",
        "postgres",
        "sql",
        "constraint",
        "duplicate key",
        "serialization",
        "connection pool",
    ],
    "Memory Error": [
        "memory",
        "cuda",
        "out of memory",
        "heap",
        "allocation",
    ],
    "Dependency Import Error": [
        "dependency",
        "import",
        "modulenotfound",
        "module not found",
        "missing dependency",
        "unavailable export",
    ],
    "Service Connection Failure": [
        "connection failure",
        "connection refused",
        "service connection",
        "connectionerror",
    ],
    "Test Assertion Failure": [
        "assertion",
        "assertionerror",
        "test assertion",
    ],
    "Authentication Issue": [
        "auth",
        "authentication",
        "unauthorized",
        "permission denied",
        "token",
        "signature",
    ],
    "Routing Error": [
        "routing",
        "404",
        "not found",
        "resource not found",
    ],
    "Syntax Error": [
        "syntax",
        "syntaxerror",
    ],
    "Type Error": [
        "type",
        "typeerror",
        "type mismatch",
    ],
    "Value Error": [
        "value",
        "valueerror",
        "invalid literal",
        "invalid type conversion",
    ],
    "Unknown": [
        "unknown",
        "normal operation",
        "info",
    ],
}


def _matches_error_type(actual: str, expected: str) -> bool:
    text = (actual or "").lower()
    expected_text = expected.lower()

    if expected_text in text:
        return True

    aliases = ERROR_TYPE_ALIASES.get(expected, [])
    return any(alias in text for alias in aliases)


def evaluate_result(result: dict, expected: dict = None):
    report = result.get("final_report", {})
    confidence = report.get("confidence", 0)

    if confidence >= 0.8:
        quality = "high"
    elif confidence >= 0.6:
        quality = "medium"
    else:
        quality = "low"

    evaluation = {
        "confidence": confidence,
        "quality": quality,
    }

    if expected:
        title = report.get("title", "")
        error_type = report.get("error_type", "")
        classification = report.get("classification", "")
        actual_text = f"{title} {error_type}"

        title_match = _matches_error_type(actual_text, expected["error_type"])
        classification_match = classification == expected["classification"]

        evaluation.update(
            {
                "title_match": title_match,
                "classification_match": classification_match,
                "score": round((int(title_match) + int(classification_match)) / 2, 2),
            }
        )

    return evaluation
