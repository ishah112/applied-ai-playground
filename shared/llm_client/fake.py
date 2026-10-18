"""Deterministic fake LLM for tests/evals. Same prompt -> same output."""
from .client import LLMClient, LLMResponse


class FakeLLMClient(LLMClient):
    def complete(self, prompt: str, *, system: str = "", temperature: float = 0.0) -> LLMResponse:
        # Deliberately boring: evals assert the reconciler does NOT blindly trust this.
        return LLMResponse(text='{"signal": "NEUTRAL", "confidence": 0.5, "reason": "fake-llm placeholder"}')
