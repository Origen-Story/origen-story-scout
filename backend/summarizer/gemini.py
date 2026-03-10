from google import genai
from typing import Optional
from .base import LLMProvider
from shared.config import settings

class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            full_context = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_context,
            )
            return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            raise e

    def name(self) -> str:
        return "Gemini"
