"""Shared DB connection. One Postgres, schema-per-app isolation.

Usage:
    conn = get_connection("stock_analyzer")  # sets search_path to that schema
No connection is made at import time, so unit tests run without Postgres.
"""
import os


def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://playground:playground@localhost:5432/playground",
    )


def get_connection(schema: str):
    """Return a psycopg connection pinned to `schema`. Requires psycopg (pip install '.[db]')."""
    try:
        import psycopg
    except ImportError as exc:  # pragma: no cover - only when db extra missing
        raise RuntimeError("Install the db extra: pip install '.[db]'") from exc
    conn = psycopg.connect(database_url(), autocommit=True)
    # Identifiers are validated by schema.py; schema names here are internal constants.
    with conn.cursor() as cur:
        cur.execute(f'SET search_path TO "{schema}", public')
    return conn
