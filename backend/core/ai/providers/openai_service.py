"""OpenAI GPT integration"""
from openai import AsyncOpenAI
import os

class OpenAIService:
    """OpenAI API wrapper"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate(self, prompt: str, model: str = "gpt-4", max_tokens: int = 500):
        """Generate text with GPT"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return {
                'text': response.choices[0].message.content,
                'tokens': response.usage.total_tokens,
                'cost': self._calculate_cost(model, response.usage.total_tokens)
            }
        except Exception as e:
            raise Exception(f"OpenAI error: {str(e)}")

    def _calculate_cost(self, model: str, tokens: int):
        """Calculate API cost"""
        costs_per_1k = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002
        }
        return (tokens / 1000) * costs_per_1k.get(model, 0.01)
