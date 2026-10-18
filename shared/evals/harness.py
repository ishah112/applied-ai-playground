"""Tiny shared eval harness: run cases, compare with tolerance, report pass/fail."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EvalResult:
    name: str
    passed: bool
    detail: str = ""


def run_evals(cases, fn) -> list[EvalResult]:
    """cases: iterable of dicts with 'name' + inputs. fn(case) -> (passed: bool, detail: str)."""
    results = []
    for case in cases:
        try:
            passed, detail = fn(case)
        except Exception as exc:  # evals must report, not crash
            passed, detail = False, f"exception: {exc}"
        results.append(EvalResult(name=case.get("name", "?"), passed=passed, detail=detail))
    return results


def summarize(results: list[EvalResult]) -> str:
    passed = sum(r.passed for r in results)
    lines = [f"{passed}/{len(results)} evals passed"]
    for r in results:
        lines.append(f"  {'PASS' if r.passed else 'FAIL'} {r.name} {r.detail}")
    return "\n".join(lines)
