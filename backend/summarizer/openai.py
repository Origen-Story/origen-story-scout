from typing import Optional
from openai import OpenAI
from .base import LLMProvider
from ..config import settings


class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: Optional[str] = None):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = model_name or settings.openai_model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content or ""

    def name(self) -> str:
        return f"OpenAI ({self.model_name})"
