"""Google Gemini integration"""
import google.generativeai as genai
import os

class GeminiService:
    """Gemini API wrapper"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate(self, prompt: str, max_tokens: int = 500):
        """Generate text with Gemini"""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7
                )
            )

            # Rough token estimate
            tokens = len(prompt.split()) + len(response.text.split())

            return {
                'text': response.text,
                'tokens': tokens,
                'cost': (tokens / 1000) * 0.0005  # Gemini is very cheap
            }
        except Exception as e:
            raise Exception(f"Gemini error: {str(e)}")
