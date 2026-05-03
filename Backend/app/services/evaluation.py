def evaluate_result(result: dict):
    report = result.get("final_report", {})

    confidence = report.get("confidence", 0)

    if confidence >= 0.8:
        quality = "high"
    elif confidence >= 0.6:
        quality = "medium"
    else:
        quality = "low"

    return {
        "confidence": confidence,
        "quality": quality
    }