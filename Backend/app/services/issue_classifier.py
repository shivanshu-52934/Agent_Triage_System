import os
import json
import re
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CACHE = {}

ALLOWED = [
    "Backend Error",
    "Database Issue",
    "API Failure",
    "Performance Issue",
    "Authentication Issue",
    "Infrastructure Issue",
    "Memory Error",
    "Other"
]


def group_issues_llm(issues):
    if not issues:
        return {}

    uncached = []
    index_map = {}

    # 🔥 separate cached + uncached
    for i, issue in enumerate(issues):
        title = issue["title"]

        if title in CACHE:
            continue

        index_map[len(uncached)] = i
        uncached.append(issue)

    # 🔥 batch classify uncached
    if uncached:
        prompt = f"""
You are a senior backend engineer.

Classify each issue STRICTLY into ONE of these categories:

{", ".join(ALLOWED)}

Rules:
- Return ONLY JSON
- No explanation
- No extra text

Format:
[
  {{"id": 1, "category": "Backend Error"}}
]

Issues:
"""

        for i, issue in enumerate(uncached):
            prompt += f"{i+1}. {issue['title']}\n"

        try:
            res = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            raw = res.content[0].text.strip()
            print("LLM RAW:", raw)

            # 🔥 SAFE JSON extraction
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if not match:
                raise Exception("Invalid JSON from LLM")

            parsed = json.loads(match.group(0))

            for item in parsed:
                idx = item["id"] - 1
                category = item["category"]

                original_index = index_map[idx]
                issue_title = issues[original_index]["title"]

                # normalize
                for cat in ALLOWED:
                    if cat.lower() in category.lower():
                        category = cat
                        break
                else:
                    category = "Other"

                CACHE[issue_title] = category

        except Exception as e:
            print("LLM FAILED:", e)

            for issue in uncached:
                CACHE[issue["title"]] = "Other"

    # 🔥 group issues
    grouped = {}

    for issue in issues:
        category = CACHE.get(issue["title"], "Other")

        if category not in grouped:
            grouped[category] = []

        grouped[category].append(issue)

    return grouped