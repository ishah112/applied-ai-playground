"""Registry of app schemas. One schema per app, nothing shared across apps."""
import re

APP_SCHEMAS = {
    "stock_analyzer": "apps/stock_analyzer/schema.sql",
    # "llm_router": "apps/llm_router/schema.sql",
    # "mcp_server": "apps/mcp_server/schema.sql",
}

_SCHEMA_RE = re.compile(r"^[a-z][a-z0-9_]{0,62}$")


def validate_schema(name: str) -> str:
    if not _SCHEMA_RE.match(name):
        raise ValueError(f"Invalid schema name: {name!r}")
    if name not in APP_SCHEMAS:
        raise ValueError(f"Unknown app schema: {name!r}. Register it in APP_SCHEMAS.")
    return name
