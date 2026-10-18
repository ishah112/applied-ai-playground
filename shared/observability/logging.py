"""Structured logging: one JSON line per event, so runs are comparable."""
import json
import sys
import time


def log(event: str, **fields) -> None:
    record = {"ts": time.time(), "event": event, **fields}
    print(json.dumps(record, sort_keys=True), file=sys.stderr)
