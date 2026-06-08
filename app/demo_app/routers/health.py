"""Liveness and readiness."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..db import get_engine
from ..injection import db_slow_sleep
from ..logging_config import log

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    log.info("health_ok", extra={"extra_fields": {"http.route": "/health"}})
    return {"status": "ok"}


@router.get("/ready", response_model=None)
def ready() -> dict[str, Any] | JSONResponse:
    route = "/ready"
    t0 = time.perf_counter()
    try:
        db_slow_sleep()
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        ms = (time.perf_counter() - t0) * 1000
        log.info("ready_ok", extra={"extra_fields": {"http.route": route, "db.latency_ms": round(ms, 2)}})
        return {"ready": True, "db.latency_ms": round(ms, 2)}
    except SQLAlchemyError as e:
        ms = (time.perf_counter() - t0) * 1000
        log.error(
            "ready_fail",
            extra={"extra_fields": {"http.route": route, "db.latency_ms": round(ms, 2), "error": str(e)}},
        )
        return JSONResponse(status_code=503, content={"ready": False, "error": str(e)})
