"""Anthropic Claude integration"""
from anthropic import AsyncAnthropic
import os

class ClaudeService:
    """Claude API wrapper"""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def generate(self, prompt: str, max_tokens: int = 500):
        """Generate text with Claude"""
        try:
            message = await self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            tokens = message.usage.input_tokens + message.usage.output_tokens

            return {
                'text': message.content[0].text,
                'tokens': tokens,
                'cost': (tokens / 1000) * 0.015
            }
        except Exception as e:
            raise Exception(f"Claude error: {str(e)}")
