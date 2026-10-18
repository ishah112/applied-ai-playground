"""Guardrails at the boundary: screen input, validate LLM output."""
import json
import re

_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|above|prior) instructions",
    r"system prompt",
    r"you are now",
    r"disregard .*instructions",
    r"jailbreak",
    r"do anything now",
]


def check_input(text: str) -> tuple[bool, str]:
    """Return (ok, reason). False = block this input."""
    lowered = text.lower()
    for pat in _INJECTION_PATTERNS:
        if re.search(pat, lowered):
            return False, f"blocked: matched injection pattern {pat!r}"
    return True, "ok"


def validate_json_output(text: str, required_keys: list[str]) -> tuple[bool, dict | str]:
    """Parse LLM JSON and check required keys. Returns (ok, parsed_or_error)."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return False, "output is not a JSON object"
    missing = [k for k in required_keys if k not in data]
    if missing:
        return False, f"missing keys: {missing}"
    return True, data
