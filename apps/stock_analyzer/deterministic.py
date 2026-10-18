"""App #1 — stock-analyzer: DETERMINISTIC BASELINE (no LLM).

Given a list of closing prices (oldest -> newest), compute reproducible
trend stats. Same input -> same output, every time. This is the ground truth
the LLM layer + reconciler will later be checked against.

No network, no API key, no randomness.
"""
from __future__ import annotations
import math
import statistics
from dataclasses import dataclass, asdict


@dataclass
class Analysis:
    last_price: float
    sma_20: float | None
    sma_50: float | None
    momentum_10d_pct: float | None
    volatility_annualized_pct: float | None
    signal: str  # BULLISH | BEARISH | NEUTRAL
    reasons: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _sma(prices: list[float], window: int) -> float | None:
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window


def _momentum(prices: list[float], lookback: int = 10) -> float | None:
    if len(prices) <= lookback:
        return None
    base = prices[-lookback - 1]
    if base == 0:
        return None
    return (prices[-1] / base - 1.0) * 100.0


def _volatility(prices: list[float]) -> float | None:
    if len(prices) < 2:
        return None
    rets = [prices[i] / prices[i - 1] - 1.0 for i in range(1, len(prices)) if prices[i - 1] != 0]
    if len(rets) < 2:
        return None
    return statistics.pstdev(rets) * math.sqrt(252) * 100.0


def analyze(prices: list[float]) -> Analysis:
    if not prices:
        raise ValueError("prices must be non-empty")
    if any(p <= 0 for p in prices):
        raise ValueError("prices must be positive")
    if len(prices) < 2:
        raise ValueError("need at least 2 prices")

    sma20 = _sma(prices, 20)
    sma50 = _sma(prices, 50)
    mom = _momentum(prices, 10)
    vol = _volatility(prices)

    reasons: list[str] = []
    score = 0  # + bullish, - bearish; signal from score, not vibes

    if sma20 is not None and sma50 is not None:
        if sma20 > sma50:
            score += 1
            reasons.append(f"SMA-20 ({sma20:.2f}) above SMA-50 ({sma50:.2f})")
        elif sma20 < sma50:
            score -= 1
            reasons.append(f"SMA-20 ({sma20:.2f}) below SMA-50 ({sma50:.2f})")
    if mom is not None:
        if mom > 2.0:
            score += 1
            reasons.append(f"10-day momentum +{mom:.2f}%")
        elif mom < -2.0:
            score -= 1
            reasons.append(f"10-day momentum {mom:.2f}%")
        else:
            reasons.append(f"10-day momentum {mom:+.2f}% (flat)")
    if vol is not None:
        reasons.append(f"Annualized volatility {vol:.1f}%")
    if not reasons:
        reasons.append("Not enough data for trend signals")

    signal = "BULLISH" if score > 0 else "BEARISH" if score < 0 else "NEUTRAL"
    return Analysis(
        last_price=prices[-1],
        sma_20=sma20,
        sma_50=sma50,
        momentum_10d_pct=mom,
        volatility_annualized_pct=vol,
        signal=signal,
        reasons=reasons,
    )
