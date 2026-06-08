"""Structured JSON logging and trace correlation."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from typing import Any

from .config import LOG_LEVEL, SERVICE_NAME

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": SERVICE_NAME,
            "logger": record.name,
            "trace_id": trace_id_var.get(""),
        }
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)  # type: ignore[attr-defined]
        return json.dumps(payload, default=str)


def setup_logging() -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(LOG_LEVEL)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter())
    root.addHandler(h)


setup_logging()
log = logging.getLogger("demo-app")
