class TestGenerationAgent:
    def run(self, root_data: dict):
        error_type = root_data.get("error_type", "Unknown")
        classification = root_data.get("classification", "Info")
        root_cause = root_data.get("root_cause", "No root cause available")

        if classification == "Info":
            return {
                "agent": "test_generation",
                "should_add_test": False,
                "test_name": "test_no_regression_needed_for_informational_log",
                "test_code": "",
                "notes": "Informational logs do not need a regression test by default.",
            }

        slug = (
            error_type.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )

        test_code = f'''def test_{slug}_regression():
    """
    Regression test placeholder generated from Sentinel triage.
    Root cause: {root_cause[:180]}
    """
    log = "sample failing log for {error_type}"

    result = analyze_log_for_test(log)

    assert result["final_report"]["error_type"] == "{error_type}"
    assert result["final_report"]["classification"] == "{classification}"
'''

        return {
            "agent": "test_generation",
            "should_add_test": True,
            "test_name": f"test_{slug}_regression",
            "test_code": test_code,
            "notes": "Adapt analyze_log_for_test to your app test client or service boundary.",
        }
