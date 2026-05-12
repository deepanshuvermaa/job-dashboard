"""
AI Content Generator - Create LinkedIn posts from keywords and GitHub commits
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Optional
import requests

# Load environment variables from project root
# Go up 3 levels: ai_content_generator.py -> modules -> backend -> project_root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"[OK] Loaded .env from {env_path}")
else:
    # Fallback: try current directory
    load_dotenv()
    print("[WARNING] Loading .env from current directory")

class AIContentGenerator:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print(f"ERROR: OPENAI_API_KEY not found!")
            print(f"Checked: {env_path}")
            print("Please ensure OPENAI_API_KEY is set in .env file")
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.openai_client = OpenAI(api_key=api_key)
        self.github_token = os.getenv('GITHUB_TOKEN')
        print("[OK] AI Content Generator initialized successfully")

    def generate_post_from_keywords(
        self,
        keywords: str,
        tone: str = "professional",
        length: str = "medium",
        include_hashtags: bool = True,
        include_emoji: bool = False
    ) -> str:
        """Generate LinkedIn post from keywords"""

        # Define length targets
        length_guide = {
            "short": "2-3 sentences (100-150 words)",
            "medium": "1-2 paragraphs (150-250 words)",
            "long": "3-4 paragraphs (250-400 words)"
        }

        # Define tone characteristics
        tone_guide = {
            "professional": "formal, business-oriented, clear and concise",
            "casual": "friendly, conversational, relatable",
            "technical": "detailed, technical terms, educational",
            "inspirational": "motivational, encouraging, story-driven"
        }

        prompt = f"""Create a LinkedIn post based on these keywords: {keywords}

Tone: {tone_guide.get(tone, 'professional')}
Length: {length_guide.get(length, 'medium')}
{'Include relevant hashtags at the end' if include_hashtags else 'No hashtags'}
{'You can use emojis tastefully' if include_emoji else 'No emojis'}

Requirements:
- Make it engaging and authentic
- Start with a hook that grabs attention
- Include actionable insights or value
- End with a call-to-action or thought-provoking question
- Use line breaks for readability
- Sound human, not corporate

Write ONLY the post content, no explanations or meta-commentary."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert LinkedIn content creator who writes engaging, authentic posts that get high engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            post_content = response.choices[0].message.content.strip()
            return post_content

        except Exception as e:
            print(f"Error generating post from keywords: {e}")
            return f"🚀 Excited to share insights on {keywords}!\n\nWhat are your thoughts on this topic?\n\n#LinkedIn #Technology #Development"

    def fetch_readme(self, repo_name: str) -> str:
        """Fetch README content from GitHub repository"""
        if not self.github_token:
            return ""

        try:
            # Try to get README
            url = f"https://api.github.com/repos/{repo_name}/readme"
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3.raw"
            }
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Limit README to first 1500 characters to avoid token limits
                readme = response.text[:1500]
                return readme
            return ""
        except Exception as e:
            print(f"Error fetching README for {repo_name}: {e}")
            return ""

    def generate_post_from_commits(
        self,
        repo_name: str,
        commits: List[Dict],
        include_readme: bool = True
    ) -> str:
        """Generate LinkedIn post from GitHub commits + README analysis"""

        if not commits:
            return None

        # Fetch README if requested
        readme = ""
        if include_readme:
            readme = self.fetch_readme(repo_name)

        # Build commit summary
        commit_summary = []
        for commit in commits[:5]:  # Use up to 5 most recent commits
            days_text = "today" if commit['days_ago'] == 0 else f"{commit['days_ago']} days ago"
            commit_summary.append(f"- {commit['message']} ({days_text})")

        commit_text = "\n".join(commit_summary)

        # Create comprehensive prompt
        prompt = f"""Create an engaging LinkedIn post about the GitHub repository "{repo_name}" and its recent development progress.

{'PROJECT CONTEXT (from README):' if readme else ''}
{readme[:800] if readme else ''}

RECENT COMMITS (last 5):
{commit_text}

Requirements:
- Start with an attention-grabbing hook about what the project does or what you've accomplished
- If README is available, briefly explain what the project is about
- Highlight 2-3 key improvements or features from the recent commits
- Show the impact or value of these changes
- Make it sound exciting but authentic (no hype or exaggeration)
- Keep it concise: 150-250 words
- Use 2-3 line breaks for readability
- End with a question or call-to-action to drive engagement
- Include 3-5 relevant hashtags based on the tech stack
- Sound like a real developer sharing their work, not a corporate announcement

Write ONLY the post content, no meta-commentary."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a developer sharing your project progress on LinkedIn. Write authentic, engaging posts that showcase your work and invite discussion."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            post_content = response.choices[0].message.content.strip()
            return post_content

        except Exception as e:
            print(f"Error generating post from commits: {e}")
            return None

    def generate_weekly_summary_post(
        self,
        repos: List[Dict]
    ) -> str:
        """Generate a weekly summary post from multiple repositories"""

        prompt = f"""Create an engaging LinkedIn post summarizing this week's development work across {len(repos)} projects.

Projects worked on:
{', '.join([r['repo_name'] for r in repos])}

Requirements:
- Start with a strong hook about productivity or progress
- Mention the variety of projects worked on
- Keep it humble yet proud
- Use 2-3 line breaks for readability
- Include a reflection or lesson learned
- End with a question to encourage discussion
- Include relevant hashtags (#Developer #GitHub #Coding etc.)
- 150-250 words
- Sound authentic and personal

Write ONLY the post content, no explanations."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a developer sharing your weekly progress on LinkedIn in an authentic, engaging way."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            post_content = response.choices[0].message.content.strip()
            return post_content

        except Exception as e:
            print(f"Error generating weekly summary: {e}")
            return None
