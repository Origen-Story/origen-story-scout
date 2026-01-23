from anthropic import Anthropic
from typing import Optional
from .base import LLMProvider
from shared.config import settings

class ClaudeProvider(LLMProvider):
    def __init__(self, model_name: str = "claude-3-opus-20240229"):
        if not settings.anthropic_api_key:
            # We don't raise error here because it's optional secondary
            self.client = None
        else:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.client:
            return "Claude API key not configured."
        
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=2000,
            system=system_prompt or "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text

    def name(self) -> str:
        return f"Claude ({self.model_name})"
