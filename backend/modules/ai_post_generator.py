"""
AI Post Generator using OpenAI GPT-4
"""

import os
import openai
from typing import List, Dict
import json

class AIPostGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key

    def generate_post_from_commits(self, commits: List[Dict], pillar: str = "project_breakdown") -> Dict:
        """Generate LinkedIn post from GitHub commits"""

        # Create context from commits
        commit_summary = "\n".join([
            f"- {c['message']} ({c['date'][:10]})"
            for c in commits[:5]  # Top 5 commits
        ])

        pillar_prompts = {
            "project_breakdown": "Share a technical breakdown of what you built",
            "debugging_story": "Tell a relatable debugging story",
            "learning_reflection": "Reflect on what you learned",
            "how_to": "Create a helpful how-to guide",
            "hot_take": "Share a controversial but insightful opinion"
        }

        prompt = f"""You are a LinkedIn content expert. Create an engaging LinkedIn post based on these GitHub commits:

{commit_summary}

Post Type: {pillar_prompts.get(pillar, "Share technical insights")}

Requirements:
1. Write in first person, authentic voice
2. Start with a HOOK that grabs attention
3. Keep it under 200 words
4. Include specific technical details
5. End with a call-to-action question
6. Make it relatable and engaging

Return ONLY a JSON object with this structure:
{{
    "hooks": ["Hook option 1", "Hook option 2", "Hook option 3"],
    "body": "Main post content",
    "cta": "Call to action question",
    "hashtags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn content creator who writes authentic, engaging posts for developers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            post_data = json.loads(content.strip())

            return {
                "hooks": post_data.get("hooks", ["Check out what I built!"]),
                "body": post_data.get("body", ""),
                "cta": post_data.get("cta", "What do you think?"),
                "hashtags": post_data.get("hashtags", ["coding", "webdev"]),
                "pillar": pillar,
                "source": f"GitHub commits: {len(commits)} commits analyzed"
            }

        except Exception as e:
            print(f"Error generating post: {e}")
            # Return fallback post
            return self._create_fallback_post(commits, pillar)

    def _create_fallback_post(self, commits: List[Dict], pillar: str) -> Dict:
        """Create a basic post if AI fails"""
        return {
            "hooks": [
                f"Just pushed {len(commits)} commits this week!",
                "Here's what I've been building lately...",
                "Quick update on my latest project:"
            ],
            "body": f"""I've been working hard on my latest project this week.

Key updates:
{chr(10).join([f'• {c["message"][:50]}' for c in commits[:3]])}

The journey continues, and I'm learning something new every day.

What are you working on?""",
            "cta": "What are you working on?",
            "hashtags": ["coding", "webdev", "programming", "developer", "tech"],
            "pillar": pillar,
            "source": f"{len(commits)} GitHub commits"
        }

    def improve_hook(self, current_hook: str) -> List[str]:
        """Generate alternative hooks for a post"""
        prompt = f"""Given this LinkedIn post hook:
"{current_hook}"

Generate 3 alternative hooks that are:
1. More attention-grabbing
2. Use different angles (curiosity, controversy, storytelling)
3. Keep under 100 characters

Return ONLY a JSON array of strings: ["hook1", "hook2", "hook3"]
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()
            hooks = json.loads(content)
            return hooks

        except Exception as e:
            print(f"Error improving hook: {e}")
            return [current_hook]
