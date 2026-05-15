"""
Multi-AI Provider Support
Support for OpenAI, DeepSeek, and Google Gemini
Based on GodsScion's approach
"""

import os
from typing import Dict, Optional, List
from openai import OpenAI
import google.generativeai as genai


class AIProvider:
    """Base AI provider interface"""

    def generate_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate text completion"""
        raise NotImplementedError

    def generate_chat_completion(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate chat completion"""
        raise NotImplementedError


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def generate_chat_completion(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def get_client(self):
        """Get raw OpenAI client for backwards compatibility"""
        return self.client


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider (OpenAI-compatible API)"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = model

    def generate_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return None

    def generate_chat_completion(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return None

    def get_client(self):
        """Get raw OpenAI-compatible client"""
        return self.client


class GeminiProvider(AIProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model

    def generate_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def generate_chat_completion(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            # Convert OpenAI format messages to Gemini format
            prompt_parts = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')

                if role == 'system':
                    prompt_parts.append(f"System: {content}")
                elif role == 'user':
                    prompt_parts.append(f"User: {content}")
                elif role == 'assistant':
                    prompt_parts.append(f"Assistant: {content}")

            combined_prompt = "\n\n".join(prompt_parts)

            generation_config = genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            response = self.model.generate_content(
                combined_prompt,
                generation_config=generation_config
            )

            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def get_client(self):
        """Get Gemini model"""
        return self.model


class GroqProvider(AIProvider):
    """Groq provider (OpenAI-compatible API, fast inference, free tier)"""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self.model = model

    def generate_completion(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            return None

    def generate_chat_completion(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API error: {e}")
            return None

    def get_client(self):
        return self.client


class AIProviderManager:
    """Manage multiple AI providers with fallback"""

    def __init__(self, config: Dict = None):
        """
        Initialize AI provider manager

        Args:
            config: Dictionary with provider configurations
                {
                    'primary_provider': 'openai' | 'deepseek' | 'gemini' | 'groq',
                    'fallback_providers': ['groq', 'openai', 'deepseek', 'gemini'],
                    'openai_api_key': str,
                    'openai_model': str,
                    'deepseek_api_key': str,
                    'deepseek_model': str,
                    'gemini_api_key': str,
                    'gemini_model': str
                }
        """
        self.config = config or {}
        self.providers = {}
        self._initialize_providers()

        # Set primary provider
        primary = self.config.get('primary_provider', 'groq')
        self.primary_provider_name = primary
        self.primary_provider = self.providers.get(primary)

        # Set fallback order (Groq first - free tier, then OpenAI)
        fallback_order = self.config.get('fallback_providers', ['groq', 'openai', 'deepseek', 'gemini'])
        self.fallback_providers = [self.providers.get(name) for name in fallback_order if self.providers.get(name)]

    def _initialize_providers(self):
        """Initialize available AI providers based on config"""

        # OpenAI
        openai_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        if openai_key:
            model = self.config.get('openai_model', 'gpt-4o-mini')
            try:
                self.providers['openai'] = OpenAIProvider(openai_key, model)
                print("[OK] OpenAI provider initialized")
            except Exception as e:
                print(f"[ERROR] OpenAI provider failed: {e}")

        # Groq (free tier, fast inference)
        groq_key = self.config.get('groq_api_key') or os.getenv('GROQ_API_KEY')
        if groq_key:
            model = self.config.get('groq_model', 'llama-3.3-70b-versatile')
            try:
                self.providers['groq'] = GroqProvider(groq_key, model)
                print("[OK] Groq provider initialized (llama-3.3-70b)")
            except Exception as e:
                print(f"[ERROR] Groq provider failed: {e}")

        # DeepSeek
        deepseek_key = self.config.get('deepseek_api_key') or os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            model = self.config.get('deepseek_model', 'deepseek-chat')
            try:
                self.providers['deepseek'] = DeepSeekProvider(deepseek_key, model)
                print("[OK] DeepSeek provider initialized")
            except Exception as e:
                print(f"[ERROR] DeepSeek provider failed: {e}")

        # Gemini
        gemini_key = self.config.get('gemini_api_key') or os.getenv('GEMINI_API_KEY')
        if gemini_key:
            model = self.config.get('gemini_model', 'gemini-1.5-flash')
            try:
                self.providers['gemini'] = GeminiProvider(gemini_key, model)
                print("[OK] Gemini provider initialized")
            except Exception as e:
                print(f"[ERROR] Gemini provider failed: {e}")

        if not self.providers:
            print("[WARN] No AI providers initialized. Check API keys.")

    def generate(self, prompt: str, max_tokens: int = 150, temperature: float = 0.7, use_fallback: bool = True) -> Optional[str]:
        """
        Generate completion with automatic fallback

        Args:
            prompt: Text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            use_fallback: Whether to use fallback providers on failure

        Returns:
            Generated text or None
        """
        # Try primary provider first
        if self.primary_provider:
            print(f"🤖 Using {self.primary_provider_name} (primary)")
            result = self.primary_provider.generate_completion(prompt, max_tokens, temperature)
            if result:
                return result
            print(f"[WARN] {self.primary_provider_name} failed")

        # Try fallback providers
        if use_fallback:
            for provider in self.fallback_providers:
                if provider != self.primary_provider:
                    provider_name = self._get_provider_name(provider)
                    print(f"🔄 Trying fallback: {provider_name}")
                    result = provider.generate_completion(prompt, max_tokens, temperature)
                    if result:
                        print(f"[OK] {provider_name} succeeded")
                        return result
                    print(f"[WARN] {provider_name} failed")

        print("[FAILED] All AI providers failed")
        return None

    def generate_chat(self, messages: List[Dict], max_tokens: int = 150, temperature: float = 0.7, use_fallback: bool = True) -> Optional[str]:
        """Generate chat completion with automatic fallback"""

        # Try primary provider first
        if self.primary_provider:
            print(f"🤖 Using {self.primary_provider_name} (primary)")
            result = self.primary_provider.generate_chat_completion(messages, max_tokens, temperature)
            if result:
                return result
            print(f"[WARN] {self.primary_provider_name} failed")

        # Try fallback providers
        if use_fallback:
            for provider in self.fallback_providers:
                if provider != self.primary_provider:
                    provider_name = self._get_provider_name(provider)
                    print(f"🔄 Trying fallback: {provider_name}")
                    result = provider.generate_chat_completion(messages, max_tokens, temperature)
                    if result:
                        print(f"[OK] {provider_name} succeeded")
                        return result
                    print(f"[WARN] {provider_name} failed")

        print("[FAILED] All AI providers failed")
        return None

    def get_provider(self, provider_name: str = None) -> Optional[AIProvider]:
        """Get specific provider or primary provider"""
        if provider_name:
            return self.providers.get(provider_name)
        return self.primary_provider

    def get_raw_client(self, provider_name: str = None):
        """Get raw API client for specific provider"""
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_client()
        return None

    def _get_provider_name(self, provider: AIProvider) -> str:
        """Get name of provider instance"""
        for name, p in self.providers.items():
            if p == provider:
                return name
        return "unknown"

    def list_available_providers(self) -> List[str]:
        """List all available providers"""
        return list(self.providers.keys())

    def is_available(self, provider_name: str) -> bool:
        """Check if provider is available"""
        return provider_name in self.providers


# Convenience function for backwards compatibility
def get_openai_client(api_key: str = None):
    """Get OpenAI client (backwards compatible)"""
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if api_key:
        provider = OpenAIProvider(api_key)
        return provider.get_client()
    return None
