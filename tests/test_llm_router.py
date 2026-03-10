import pytest

from backend.summarizer.router import LLMRouter, TaskType
from shared.config import settings


class DummyProvider:
    def __init__(self, name):
        self._name = name

    def generate(self, prompt, system_prompt=None):
        return f"{self._name}: {prompt}"

    def name(self):
        return self._name


def _set_keys(monkeypatch, gemini=None, openai=None, claude=None, provider="auto"):
    monkeypatch.setattr(settings, "gemini_api_key", gemini)
    monkeypatch.setattr(settings, "openai_api_key", openai)
    monkeypatch.setattr(settings, "anthropic_api_key", claude)
    monkeypatch.setattr(settings, "llm_provider", provider)


def test_router_init_without_keys_does_not_raise(monkeypatch):
    _set_keys(monkeypatch, gemini=None, openai=None, claude=None)
    LLMRouter()  # Should not raise without API keys


def test_generate_raises_without_any_provider(monkeypatch):
    _set_keys(monkeypatch, gemini=None, openai=None, claude=None)
    router = LLMRouter()
    with pytest.raises(ValueError):
        router.generate("hello")


def test_preferred_provider_used(monkeypatch):
    _set_keys(monkeypatch, openai="ok", provider="openai")
    router = LLMRouter()
    created = []

    def _create_provider(name):
        created.append(name)
        return DummyProvider(name)

    monkeypatch.setattr(router, "_create_provider", _create_provider)
    provider = router.get_provider_for_task(TaskType.GENERAL)
    assert provider.name() == "openai"
    assert created == ["openai"]


def test_auto_prefers_claude_for_complex(monkeypatch):
    _set_keys(monkeypatch, gemini="ok", claude="ok", provider="auto")
    router = LLMRouter()
    created = []

    def _create_provider(name):
        created.append(name)
        return DummyProvider(name)

    monkeypatch.setattr(router, "_create_provider", _create_provider)
    provider = router.get_provider_for_task(TaskType.COMPLEX_LOGIC)
    assert provider.name() == "claude"
    assert created == ["claude"]


def test_auto_uses_gemini_for_general_when_available(monkeypatch):
    _set_keys(monkeypatch, gemini="ok", openai=None, claude=None, provider="auto")
    router = LLMRouter()
    created = []

    def _create_provider(name):
        created.append(name)
        return DummyProvider(name)

    monkeypatch.setattr(router, "_create_provider", _create_provider)
    provider = router.get_provider_for_task(TaskType.GENERAL)
    assert provider.name() == "gemini"
    assert created == ["gemini"]
