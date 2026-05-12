"""Smart AI router that selects best/cheapest LLM for task"""
from typing import Optional
from .providers.openai_service import OpenAIService
from .providers.gemini_service import GeminiService
from .providers.claude_service import ClaudeService

class LLMRouter:
    """Route AI requests to optimal provider"""

    def __init__(self):
        self.openai = OpenAIService()
        self.gemini = GeminiService()
        self.claude = ClaudeService()

        # Costs per 1K tokens (approximate)
        self.costs = {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002,
            "gemini-pro": 0.0005,
            "claude-3-sonnet": 0.015
        }

    async def generate(
        self,
        prompt: str,
        purpose: str = "general",
        max_tokens: int = 500,
        prefer_quality: bool = False
    ) -> dict:
        """
        Generate text with optimal model

        Args:
            prompt: The prompt
            purpose: 'content_generation', 'job_answer', 'analysis'
            max_tokens: Max response length
            prefer_quality: If True, use best model regardless of cost

        Returns:
            {
                'text': str,
                'provider': str,
                'model': str,
                'tokens': int,
                'cost': float
            }
        """

        # Select model based on purpose
        if purpose == "content_generation" or prefer_quality:
            # Use best quality
            try:
                result = await self.claude.generate(prompt, max_tokens)
                return {**result, 'provider': 'claude', 'model': 'claude-3-sonnet'}
            except:
                # Fallback to GPT-4
                result = await self.openai.generate(prompt, "gpt-4", max_tokens)
                return {**result, 'provider': 'openai', 'model': 'gpt-4'}

        elif purpose == "job_answer":
            # Use fast and cheap
            try:
                result = await self.gemini.generate(prompt, max_tokens)
                return {**result, 'provider': 'gemini', 'model': 'gemini-pro'}
            except:
                # Fallback to GPT-3.5
                result = await self.openai.generate(prompt, "gpt-3.5-turbo", max_tokens)
                return {**result, 'provider': 'openai', 'model': 'gpt-3.5-turbo'}

        else:
            # Default: use cheapest
            try:
                result = await self.gemini.generate(prompt, max_tokens)
                return {**result, 'provider': 'gemini', 'model': 'gemini-pro'}
            except:
                result = await self.openai.generate(prompt, "gpt-3.5-turbo", max_tokens)
                return {**result, 'provider': 'openai', 'model': 'gpt-3.5-turbo'}

# Global router instance
llm_router = LLMRouter()
