"""Redaction helpers for logs and evidence strings."""

from __future__ import annotations

import re

REDACT_PATTERNS = [
    re.compile(r"(?i)(password|token|authorization|secret)\s*[:=]\s*\S+"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def redact(text: str) -> str:
    out = text
    for pat in REDACT_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out
