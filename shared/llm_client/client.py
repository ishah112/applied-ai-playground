"""One LLM interface for every app.

The deterministic baseline never calls this. The LLM layer calls it, and the
reconciler checks the result. Tests use FakeLLMClient (fake.py) — no key, no network.
"""
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str = "fake"
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMClient:
    """Minimal interface. Real providers implement complete()."""

    def complete(self, prompt: str, *, system: str = "", temperature: float = 0.0) -> LLMResponse:
        raise NotImplementedError


def default_client() -> LLMClient:
    """Fake unless LLM_API_KEY is set — keeps baseline + tests key-free."""
    if os.environ.get("LLM_API_KEY"):
        raise RuntimeError(
            "Real provider not wired yet — this is the next step after the baseline. "
            "Use FakeLLMClient for now."
        )
    from .fake import FakeLLMClient

    return FakeLLMClient()
