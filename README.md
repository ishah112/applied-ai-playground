# applied-ai-playground

One repo, 25+ mini-apps, one Postgres, one infra setup. Each app is isolated at the DB level (its own schema), so a new idea reuses the same infra instead of starting from scratch.

This is the interview story too: "Here's one repo I build on. Each app is small, has a deterministic baseline, an LLM layer, a reconciler, and evals."

## Stack (default, transferable)

Python + Postgres + Docker Compose. If a target company is Go/Java-heavy, the pattern transfers — the structure matters more than the language.

## Layout

```
applied-ai-playground/
  docker-compose.yml          # single Postgres for everything
  shared/                     # reused by every app
    db/                       # connection + schema-per-app helper
    llm_client/               # one LLM interface, fake for tests
    evals/                    # shared eval harness
    guardrails/               # prompt-injection + output validation
    observability/            # structured logging
  apps/
    stock-analyzer/           # App #1 — deterministic baseline first
    llm-router/               # App #2 (next)
    mcp-server/               # App #3 (next)
    ...                       # App #4+ — one folder + one schema each
```

## Rules

1. **One DB, schema per app.** `shared/db` creates `SET search_path TO <app_schema>`. Apps never share tables.
2. **Deterministic baseline first.** Every app ships a no-LLM version that works, is tested, and has evals. LLM is a layer on top, never a replacement.
3. **Reconciler, not blind trust.** When LLM output exists, a reconciler checks it against the deterministic result and either accepts, corrects, or rejects it — with a reason logged.
4. **Evals before polish.** Each app has golden cases in `evals/` that run in CI / `make evals`.
5. **Guardrails at the boundary.** User input is screened for prompt injection; LLM output is validated (schema + ranges) before it is used or stored.

## Quickstart

```bash
cp .env.example .env
docker compose up -d          # Postgres on localhost:5432
make test                     # deterministic tests + evals, no LLM key needed
make run-analyzer              # runs App #1 on sample data
```

No LLM key is needed for the baseline. The LLM layer is stubbed with a fake client until you add a key.

## App #1 — stock-analyzer

Status: deterministic baseline + LLM + reconciler + evals DONE. Next: persist to Postgres.

`apps/stock_analyzer/` takes a CSV of `date,close` prices and returns a reproducible trend analysis: SMA-20 / SMA-50, 10-day momentum, annualized volatility, and a BULLISH / BEARISH / NEUTRAL signal with reasons. Same input → same output, every time.

See `apps/stock_analyzer/README.md` for the CLI and the interview talking points.

## Adding App #N

```bash
mkdir -p apps/<new-app>/tests apps/<new-app>/evals
# 1. copy apps/stock_analyzer/schema.sql -> rename schema
# 2. write deterministic.py first, then llm.py + reconciler.py
# 3. add golden cases to evals/, tests to tests/
# 4. register the schema in shared/db/schema.py
```

## Push to GitHub

```bash
cd applied-ai-playground
git init -b main
git add . && git commit -m "Scaffold: shared infra + stock-analyzer deterministic baseline"
gh repo create applied-ai-playground --public --source=. --push
# or: create the repo on github.com, then:
# git remote add origin git@github.com:<you>/applied-ai-playground.git
# git push -u origin main
```

Never commit `.env` (it holds secrets). `.env.example` is the template.
