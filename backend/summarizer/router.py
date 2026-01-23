from enum import Enum
from typing import Optional, Dict
from .base import LLMProvider
from ..config import settings

class TaskType(Enum):
    GENERAL = "general"
    COMPLEX_LOGIC = "complex_logic"
    PROVENANCE_ANALYSIS = "provenance_analysis"

class LLMRouter:
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}

    def _provider_available(self, name: str) -> bool:
        if name == "gemini":
            return bool(settings.gemini_api_key)
        if name == "openai":
            return bool(settings.openai_api_key)
        if name == "claude":
            return bool(settings.anthropic_api_key)
        return False

    def _create_provider(self, name: str) -> LLMProvider:
        if name == "gemini":
            from .gemini import GeminiProvider
            return GeminiProvider()
        if name == "openai":
            from .openai import OpenAIProvider
            return OpenAIProvider()
        if name == "claude":
            from .claude import ClaudeProvider
            return ClaudeProvider()
        raise ValueError(f"Unknown LLM provider: {name}")

    def _resolve_provider_name(self, task: TaskType) -> str:
        preferred = (settings.llm_provider or "auto").lower()
        if preferred != "auto":
            if not self._provider_available(preferred):
                raise ValueError(f"{preferred.upper()}_API_KEY not configured.")
            return preferred

        if task in [TaskType.COMPLEX_LOGIC, TaskType.PROVENANCE_ANALYSIS]:
            for name in ("claude", "openai", "gemini"):
                if self._provider_available(name):
                    return name
        else:
            for name in ("gemini", "openai", "claude"):
                if self._provider_available(name):
                    return name

        raise ValueError("No LLM provider available. Configure GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY.")

    def get_provider_for_task(self, task: TaskType) -> LLMProvider:
        name = self._resolve_provider_name(task)
        if name not in self._providers:
            self._providers[name] = self._create_provider(name)
        return self._providers[name]

    def generate(self, prompt: str, task: TaskType = TaskType.GENERAL, system_prompt: Optional[str] = None) -> str:
        provider = self.get_provider_for_task(task)
        return provider.generate(prompt, system_prompt=system_prompt)
