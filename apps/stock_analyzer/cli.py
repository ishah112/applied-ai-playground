"""CLI for App #1. Deterministic baseline by default; --llm adds LLM + reconciler.

    python3 -m apps.stock_analyzer.cli --sample
    python3 -m apps.stock_analyzer.cli --sample --llm
    python3 -m apps.stock_analyzer.cli --csv prices.csv --llm --symbol AAPL
    python3 -m apps.stock_analyzer.cli --evals
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

from apps.stock_analyzer.deterministic import analyze
from apps.stock_analyzer.llm import get_llm_analysis
from apps.stock_analyzer.reconciler import reconcile
from shared.observability import log


def sample_prices() -> list[float]:
    prices = [100.0]
    for _ in range(59):
        prices.append(round(prices[-1] * 1.004, 2))
    return prices


def load_csv(path: str) -> list[float]:
    prices: list[float] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "close" not in reader.fieldnames:
            raise ValueError("CSV must have a 'close' column (date,close)")
        for row in reader:
            prices.append(float(row["close"]))
    return prices


def run_evals() -> int:
    from shared.evals import run_evals, summarize
    from shared.llm_client import FakeLLMClient

    golden_path = Path(__file__).parent / "evals" / "golden_cases.json"
    cases = json.loads(golden_path.read_text())

    def check(case: dict):
        result = analyze([float(p) for p in case["prices"]])
        ok = result.signal == case["expected_signal"]
        return ok, f"got={result.signal} expected={case['expected_signal']}"

    results = run_evals(cases, check)
    print(summarize(results))

    # Reconciler eval: fake LLM says NEUTRAL on a clear uptrend -> must keep BULLISH.
    det = analyze([100.0 + i for i in range(60)])
    llm = get_llm_analysis(det, client=FakeLLMClient())
    rec = reconcile(det, llm)
    rec_ok = rec.final_signal == "BULLISH" and rec.decision == "llm_rejected_disagreement"
    print(f"  {'PASS' if rec_ok else 'FAIL'} reconciler-keeps-deterministic-on-disagreement final={rec.final_signal} decision={rec.decision}")
    return 0 if all(r.passed for r in results) and rec_ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Stock analyzer — deterministic baseline + optional LLM")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sample", action="store_true")
    group.add_argument("--csv", type=str, help="CSV with date,close columns")
    group.add_argument("--evals", action="store_true")
    parser.add_argument("--llm", action="store_true", help="Add LLM proposal + reconciler (fake client unless LLM_API_KEY set)")
    parser.add_argument("--symbol", type=str, default="SAMPLE")
    parser.add_argument("--context", type=str, default="", help="Extra context, screened for prompt injection")
    args = parser.parse_args()

    if args.evals:
        return run_evals()
    prices = sample_prices() if args.sample else load_csv(args.csv)
    det = analyze(prices)
    if not args.llm:
        print(json.dumps(det.to_dict(), indent=2))
        return 0

    llm = get_llm_analysis(det, symbol=args.symbol, context=args.context)
    rec = reconcile(det, llm)
    log("stock_analyzer_reconciled", symbol=args.symbol, decision=rec.decision,
        deterministic=det.signal, llm=llm.signal, final=rec.final_signal)
    print(json.dumps({
        "deterministic": det.to_dict(),
        "llm": llm.to_dict(),
        "reconciled": rec.to_dict(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
