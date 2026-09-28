"""CP1 - Structured logging.

One event = one line = one JSON object, so cloud tooling can filter and count.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Current time in ISO-8601, UTC timezone."""
    return datetime.now(timezone.utc).isoformat()


def log_event(event: str, level: str = "info", **fields) -> str:
    """Write a single-line JSON log to stdout and return the line."""
    record = {"event": event, "level": level.lower(), "timestamp": utc_now_iso()}
    record.update(fields)
    line = json.dumps(record, ensure_ascii=False)
    print(line, file=sys.stdout)
    return line
