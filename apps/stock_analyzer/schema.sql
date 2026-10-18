-- App #1 — stock_analyzer schema. Isolated: no other app reads/writes here.
CREATE SCHEMA IF NOT EXISTS stock_analyzer;

CREATE TABLE IF NOT EXISTS stock_analyzer.analyses (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  as_of DATE NOT NULL,
  last_price DOUBLE PRECISION NOT NULL,
  sma_20 DOUBLE PRECISION,
  sma_50 DOUBLE PRECISION,
  momentum_10d_pct DOUBLE PRECISION,
  volatility_annualized_pct DOUBLE PRECISION,
  signal TEXT NOT NULL CHECK (signal IN ('BULLISH', 'BEARISH', 'NEUTRAL')),
  reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
  source TEXT NOT NULL DEFAULT 'deterministic', -- deterministic | llm | reconciled
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (symbol, as_of, source)
);
