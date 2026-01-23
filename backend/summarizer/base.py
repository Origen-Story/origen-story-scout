from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """General text generation"""
        pass

    @abstractmethod
    def name(self) -> str:
        pass
