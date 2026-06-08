"""HTTP middleware: trace IDs and injection hooks."""

from __future__ import annotations

import uuid

from fastapi import Request, Response

from .injection import maybe_crash, maybe_error_response
from .logging_config import trace_id_var


async def tracing_and_inject(request: Request, call_next):
    tid = request.headers.get("x-trace-id") or str(uuid.uuid4())
    trace_id_var.set(tid)
    maybe_crash()
    bad = maybe_error_response(request.url.path)
    if bad is not None:
        return bad
    response: Response = await call_next(request)
    response.headers["x-trace-id"] = tid
    return response
