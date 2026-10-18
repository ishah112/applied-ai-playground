"""Reconciler: decides what to trust when deterministic + LLM disagree.

Rule (deliberate, interview-defensible):
- LLM output invalid -> keep deterministic, log llm_invalid.
- LLM agrees with deterministic -> accept, source = reconciled.
- LLM disagrees -> keep deterministic, log llm_rejected_disagreement.

Why not let a high-confidence LLM override? Because this version has no
verifiable fact channel (no earnings date, no news source the code can
check). An override needs a fact the reconciler can verify, not just a
confident tone. When that channel exists, add it here — and only here —
so the override policy stays in one place.
"""
from __future__ import annotations
from dataclasses import dataclass

from .deterministic import Analysis
from .llm import LLMAnalysis


@dataclass
class Reconciled:
    final_signal: str
    final_source: str  # deterministic | reconciled
    deterministic_signal: str
    llm_signal: str | None
    decision: str  # agreed | llm_invalid | llm_rejected_disagreement
    reason: str

    def to_dict(self) -> dict:
        return {
            "final_signal": self.final_signal,
            "final_source": self.final_source,
            "deterministic_signal": self.deterministic_signal,
            "llm_signal": self.llm_signal,
            "decision": self.decision,
            "reason": self.reason,
        }


def reconcile(det: Analysis, llm: LLMAnalysis) -> Reconciled:
    if not llm.valid:
        return Reconciled(
            final_signal=det.signal,
            final_source="deterministic",
            deterministic_signal=det.signal,
            llm_signal=None,
            decision="llm_invalid",
            reason=f"LLM output invalid ({llm.error}); keeping deterministic signal.",
        )
    if llm.signal == det.signal:
        return Reconciled(
            final_signal=det.signal,
            final_source="reconciled",
            deterministic_signal=det.signal,
            llm_signal=llm.signal,
            decision="agreed",
            reason="LLM agrees with deterministic signal.",
        )
    return Reconciled(
        final_signal=det.signal,
        final_source="deterministic",
        deterministic_signal=det.signal,
        llm_signal=llm.signal,
        decision="llm_rejected_disagreement",
        reason=(
            f"LLM said {llm.signal} (confidence {llm.confidence}) but deterministic "
            f"says {det.signal} from SMA/momentum; no verifiable fact to override "
            "the math, so keeping deterministic."
        ),
    )
