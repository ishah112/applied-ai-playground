# App #1 — stock-analyzer

Status: **deterministic baseline + LLM + reconciler DONE**. Next: persist to Postgres.

## What it does

Takes `date,close` prices → reproducible trend analysis:
SMA-20 / SMA-50, 10-day momentum, annualized volatility, and a
BULLISH / BEARISH / NEUTRAL signal with reasons.

With `--llm`, the LLM proposes a signal from those same numbers, guardrails
validate it, and the reconciler decides what to trust.

## Run it

```bash
python3 -m apps.stock_analyzer.cli --sample
python3 -m apps.stock_analyzer.cli --sample --llm        # fake LLM, no key needed
python3 -m apps.stock_analyzer.cli --csv prices.csv --llm --symbol AAPL
python3 -m apps.stock_analyzer.cli --evals               # golden cases + reconciler eval
python3 -m pytest apps/stock_analyzer/tests -q
```

## How the LLM layer works

1. **Deterministic first** (`deterministic.py`): the math. Same input → same output.
2. **LLM proposes** (`llm.py`): prompt carries only the computed numbers +
   an optional user context string. System prompt forces JSON-only output
   with `signal / confidence / reason`, and forbids inventing prices/news.
3. **Guardrails** (`shared/guardrails`): user context is screened for prompt
   injection before it reaches the LLM; LLM output must parse as JSON with
   the required keys, a valid signal, and confidence in [0, 1].
4. **Reconciler** (`reconciler.py`): the only place that decides.
   - LLM invalid → keep deterministic, `llm_invalid`
   - LLM agrees → accept, `agreed`, source `reconciled`
   - LLM disagrees → keep deterministic, `llm_rejected_disagreement`

   No silent override: a disagreement needs a *verifiable fact* (e.g. a
   checked earnings date), not just a confident tone. That fact channel
   doesn't exist yet, so disagreements always keep the math for now.

## Interview talking point

"I built the deterministic version first so the LLM has something to be
checked against. The reconciler is the trust boundary — the LLM adds
narrative, it never overrides the math silently, and every decision is
logged with a reason."

## Next step

**Persist**: store deterministic + reconciled rows in
`stock_analyzer.analyses` with `source` set accordingly
(`deterministic` vs `reconciled`). Schema is already in `schema.sql`.

## Golden cases

`evals/golden_cases.json` — uptrend → BULLISH, downtrend → BEARISH,
flat → NEUTRAL. Plus a reconciler eval: fake LLM says NEUTRAL on a clear
uptrend → final must stay BULLISH.
