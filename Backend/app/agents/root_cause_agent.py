from anthropic import Anthropic
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class RootCauseAgent:
    def run(self, parsed_log: dict):
        try:
            log_message = parsed_log.get("message", "")

            if not log_message or not log_message.strip():
                return {
                    "agent": "root_cause",
                    "analysis": {
                        "classification": "Info",
                        "error_type": "Empty Log",
                        "root_cause": "No log provided",
                        "fix_steps": []
                    }
                }

            # 🔥 STRONG PROMPT (forces structure)
            prompt = f"""
You are a senior software debugging expert.

Analyze the following error log and return ONLY valid JSON.

Log:
{log_message}

Rules:
- No explanation outside JSON
- Keep answers concise and practical
- Fix steps must be actionable

Return format:
{{
  "classification": "Critical Bug | Warning | Info",
  "error_type": "short label",
  "root_cause": "clear explanation",
  "fix_steps": ["step1", "step2", "step3"]
}}
"""

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            raw = response.content[0].text.strip()
            print("🧠 LLM RAW:", raw)

            # 🔥 TRY DIRECT JSON
            try:
                parsed = json.loads(raw)
                return {"agent": "root_cause", "analysis": parsed}
            except:
                pass

            # 🔥 TRY EXTRACT JSON FROM TEXT
            try:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    return {"agent": "root_cause", "analysis": parsed}
            except:
                pass

            # 🔥 SMART FALLBACK (NOT EMPTY)
            return {
                "agent": "root_cause",
                "analysis": {
                    "classification": "Critical Bug" if "error" in log_message.lower() or "500" in log_message else "Warning",
                    "error_type": "Unknown Error",
                    "root_cause": raw,
                    "fix_steps": [
                        "Check logs for full stack trace",
                        "Verify service dependencies",
                        "Restart affected service"
                    ]
                }
            }

        except Exception as e:
            print("🔥 RootCauseAgent ERROR:", str(e))

            return {
                "agent": "root_cause",
                "analysis": {
                    "classification": "Critical Bug",
                    "error_type": "System Error",
                    "root_cause": str(e),
                    "fix_steps": [
                        "Check API key",
                        "Verify Anthropic model access",
                        "Check network connectivity"
                    ]
                }
            }