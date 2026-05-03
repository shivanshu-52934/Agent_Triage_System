class LogParserAgent:
    def run(self, log_text: str):
        if not log_text or not log_text.strip():
            return {
                "agent": "log_parser",
                "message": "No log provided"
            }

        # 🔥 Minimal responsibility: just clean input
        cleaned_log = log_text.strip()

        return {
            "agent": "log_parser",
            "message": cleaned_log
        }