import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO")


class GitHubAgent:

    def __init__(self):
        self.headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _configured(self):
        return bool(GITHUB_TOKEN and REPO)

    def create_issue(self, title, body):
        if not self._configured():
            print("CREATE ISSUE SKIPPED: GITHUB_TOKEN or GITHUB_REPO is not configured")
            return None

        url = f"https://api.github.com/repos/{REPO}/issues"

        response = requests.post(
            url,
            headers=self.headers,
            json={
                "title": title,
                "body": body
            }
        )

        if response.status_code == 201:
            return response.json().get("html_url")

        print("CREATE ISSUE ERROR:", response.status_code, response.text)
        return None

    def get_open_issues(self):
        if not self._configured():
            return []

        url = f"https://api.github.com/repos/{REPO}/issues?state=open"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print("FETCH ERROR:", response.text)
            return []

        issues = response.json()

        cleaned = []
        for issue in issues:
            cleaned.append({
                "number": issue["number"],
                "title": issue["title"],
                "body": issue.get("body", ""),
                "url": issue["html_url"]
            })

        return cleaned

    def close_issue(self, issue_number):
        if not self._configured():
            return False

        url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}"

        response = requests.patch(
            url,
            headers=self.headers,
            json={"state": "closed"}
        )

        print("CLOSE RESPONSE:", response.status_code, response.text)

        return response.status_code == 200
