"""Deterministic failure / latency injection for RCA demos."""

from __future__ import annotations

import json
import os
import random
import threading
import time

from fastapi import Response

from .logging_config import log

_request_count = 0
_crash_lock = threading.Lock()


def db_slow_sleep() -> None:
    ms = int(os.environ.get("INJECT_DB_SLOW_MS", "0") or "0")
    if ms > 0:
        time.sleep(ms / 1000.0)


def maybe_crash() -> None:
    limit = int(os.environ.get("INJECT_CRASH_AFTER_REQUESTS", "0") or "0")
    if limit <= 0:
        return
    global _request_count
    with _crash_lock:
        _request_count += 1
        if _request_count >= limit:
            log.warning(
                "inject_fatal_exit",
                extra={"extra_fields": {"inject": "INJECT_CRASH_AFTER_REQUESTS", "count": _request_count}},
            )
            os._exit(1)


def maybe_error_response(path: str) -> Response | None:
    if path != "/items":
        return None
    pct = int(os.environ.get("INJECT_ERROR_RATE_PERCENT", "0") or "0")
    if pct <= 0:
        return None
    if random.randint(1, 100) <= pct:
        return Response(status_code=500, content=json.dumps({"detail": "injected_error"}))
    return None
