class BugReportAgent:
    def run(self, root_result: dict):
        try:
            # 🔥 Read normalized input
            root_data = root_result.get("analysis", {})

            classification = root_data.get("classification", "Info")
            error_type = root_data.get("error_type", "Unknown")
            root_cause = root_data.get("root_cause", "Not available")
            fix_steps = root_data.get("fix_steps", [])

            # 🔥 Priority logic
            if classification == "Critical Bug":
                priority = "High"
                confidence = 0.9
                status = "HIGH"
            elif classification == "Warning":
                priority = "Medium"
                confidence = 0.6
                status = "MEDIUM"
            else:
                priority = "Low"
                confidence = 0.4
                status = "LOW"

            # 🔥 Clean fix steps formatting
            fix_text = ""
            if isinstance(fix_steps, list) and fix_steps:
                fix_text = "\n".join([f"- {step}" for step in fix_steps])

            description = f"""
Error Type:
{error_type}

Root Cause:
{root_cause}

Fix Steps:
{fix_text}
"""

            return {
                "agent": "bug_report",
                "title": f"{classification}: {error_type}",
                "description": description.strip(),
                "priority": priority,
                "confidence": confidence,
                "status": status,
            }

        except Exception as e:
            print("🔥 BugReportAgent ERROR:", str(e))

            return {
                "agent": "bug_report",
                "title": "Bug Report Failed",
                "description": str(e),
                "priority": "Low",
                "confidence": 0.0,
                "status": "LOW",
            }