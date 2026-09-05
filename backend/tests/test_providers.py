import pytest

from app.api.chat import get_provider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider


def test_get_provider_defaults_to_ollama():
    provider = get_provider("ollama")
    assert isinstance(provider, OllamaProvider)


def test_get_provider_returns_claude_when_key_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    from app.config import get_settings

    get_settings.cache_clear()
    provider = get_provider("claude")
    assert isinstance(provider, ClaudeProvider)


def test_claude_provider_raises_without_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(ValueError):
        ClaudeProvider(api_key=None)
