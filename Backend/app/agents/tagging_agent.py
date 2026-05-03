from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class TaggingAgent:
    def run(self, root_data):
        try:
            prompt = f"""
Classify this bug into tags:

{root_data}

Possible tags:
- backend
- frontend
- database
- infrastructure
- api
- performance

Return comma separated tags only.
"""

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )

            tags = response.content[0].text.strip()
            return [t.strip() for t in tags.split(",")]

        except:
            return ["general"]