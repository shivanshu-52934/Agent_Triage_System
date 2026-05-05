import json
import os
import re
from typing import Dict, Tuple

from anthropic import Anthropic
from dotenv import load_dotenv

from app.services.rule_classifier import fallback_analysis

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
REQUIRED_FIELDS = ("classification", "error_type", "root_cause", "fix_steps")
ALLOWED_CLASSIFICATIONS = {"Critical Bug", "Warning", "Info"}


class RootCauseAgent:
    def run(self, parsed_log: dict):
        log_message = parsed_log.get("message", "")

        if not log_message or not log_message.strip():
            return {
                "agent": "root_cause",
                "analysis": {
                    "classification": "Info",
                    "error_type": "Empty Log",
                    "root_cause": "No log provided",
                    "fix_steps": [],
                    "source": "empty_input",
                },
                "retry_count": 0,
                "recovered": False,
            }

        retry_count = 0
        try:
            raw = self._call_llm(self._primary_prompt(log_message), max_tokens=300)
            parsed, error = self._parse_and_validate(raw)
            if parsed:
                parsed["source"] = "llm"
                return self._response(parsed, retry_count, recovered=False)

            retry_count = 1
            raw = self._call_llm(self._simplified_prompt(log_message, error), max_tokens=220)
            parsed, error = self._parse_and_validate(raw)
            if parsed:
                parsed["source"] = "llm_retry"
                return self._response(parsed, retry_count, recovered=True)

            fallback = fallback_analysis(log_message, error)
            return self._response(fallback, retry_count, recovered=True)

        except Exception as exc:
            fallback = fallback_analysis(log_message, str(exc))
            return self._response(fallback, retry_count, recovered=True)

    def _response(self, analysis: Dict, retry_count: int, recovered: bool):
        return {
            "agent": "root_cause",
            "analysis": analysis,
            "retry_count": retry_count,
            "recovered": recovered,
        }

    def _call_llm(self, prompt: str, max_tokens: int):
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    def _parse_and_validate(self, raw: str) -> Tuple[Dict, str]:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not match:
                return {}, "LLM response did not contain JSON"
            try:
                parsed = json.loads(match.group())
            except json.JSONDecodeError as exc:
                return {}, f"LLM JSON parse failed: {exc}"

        if not isinstance(parsed, dict):
            return {}, "LLM JSON was not an object"

        missing = [field for field in REQUIRED_FIELDS if field not in parsed]
        if missing:
            return {}, f"LLM JSON missing fields: {', '.join(missing)}"

        if parsed["classification"] not in ALLOWED_CLASSIFICATIONS:
            return {}, "LLM classification was outside the allowed enum"

        if not isinstance(parsed["fix_steps"], list):
            return {}, "LLM fix_steps was not a list"

        parsed["error_type"] = str(parsed["error_type"]).strip() or "Unknown"
        parsed["root_cause"] = str(parsed["root_cause"]).strip() or "Not available"
        parsed["fix_steps"] = [str(step).strip() for step in parsed["fix_steps"] if str(step).strip()]

        return parsed, ""

    def _primary_prompt(self, log_message: str):
        return f"""
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

    def _simplified_prompt(self, log_message: str, validation_error: str):
        return f"""
Return one strict JSON object for this log. The previous answer failed because: {validation_error}

Log:
{log_message[:2000]}

Use exactly these keys:
classification, error_type, root_cause, fix_steps

classification must be one of: Critical Bug, Warning, Info.
fix_steps must be a JSON array of short strings.
"""
