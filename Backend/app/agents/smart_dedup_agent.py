import os
import requests
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class SmartDedupAgent:

    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_issues(self):
        url = f"https://api.github.com/repos/{REPO}/issues"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else []

    def is_duplicate(self, new_title, new_root_cause):
        issues = self.get_issues()

        for issue in issues:
            existing_title = issue.get("title", "")
            existing_body = issue.get("body", "")

            prompt = f"""
Are these two issues describing the same bug? Answer ONLY YES or NO.

Bug A:
{new_title}
{new_root_cause}

Bug B:
{existing_title}
{existing_body}
"""

            try:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=5,
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.content[0].text.strip().lower()

                if "yes" in answer:
                    return True, issue

            except Exception as e:
                print("Dedup error:", e)

        return False, None

    def comment_duplicate(self, issue_number, title):
        url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/comments"

        requests.post(url, headers=self.headers, json={
            "body": f"🔁 Duplicate detected for: {title}"
        })

    def close_issue(self, issue_number):
        url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}"

        res = requests.patch(url, headers=self.headers, json={
            "state": "closed"
        })

        return res.status_code == 200