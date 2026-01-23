from enum import Enum
from typing import Optional
from .gemini import GeminiProvider
from .claude import ClaudeProvider
from .base import LLMProvider

class TaskType(Enum):
    GENERAL = "general"
    COMPLEX_LOGIC = "complex_logic"
    PROVENANCE_ANALYSIS = "provenance_analysis"

class LLMRouter:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.claude = ClaudeProvider()

    def get_provider_for_task(self, task: TaskType) -> LLMProvider:
        # Route logic: Claude Opus for high complexity or provenance
        if task in [TaskType.COMPLEX_LOGIC, TaskType.PROVENANCE_ANALYSIS]:
            # Fallback to Gemini if Claude key is missing
            if self.claude.client:
                return self.claude
            else:
                print("Warning: Claude Opus requested but key not set. Falling back to Gemini.")
        
        return self.gemini

    def generate(self, prompt: str, task: TaskType = TaskType.GENERAL, system_prompt: Optional[str] = None) -> str:
        provider = self.get_provider_for_task(task)
        return provider.generate(prompt, system_prompt=system_prompt)
