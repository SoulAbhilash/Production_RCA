"""
Demo API for RCA POC: structured JSON logs, Postgres, deterministic injection toggles.
"""

from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
SERVICE_NAME = os.environ.get("SERVICE_NAME", "demo-app")


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

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/app",
)

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=5)
    return _engine


def db_slow_sleep() -> None:
    ms = int(os.environ.get("INJECT_DB_SLOW_MS", "0") or "0")
    if ms > 0:
        time.sleep(ms / 1000.0)


_request_count = 0
_crash_lock = __import__("threading").Lock()


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


app = FastAPI(title="RCA Demo App", version="0.1.0")


@app.middleware("http")
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


@app.on_event("startup")
def on_startup() -> None:
    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                );
                """
            )
        )
        row = conn.execute(text("SELECT COUNT(*) AS c FROM items")).mappings().first()
        if row and int(row["c"]) == 0:
            conn.execute(
                text("INSERT INTO items (name) VALUES ('widget'), ('gadget'), ('sprocket')")
            )
    log.info("startup_complete", extra={"extra_fields": {"http.route": "/startup"}})


@app.get("/health")
def health() -> dict[str, str]:
    log.info("health_ok", extra={"extra_fields": {"http.route": "/health"}})
    return {"status": "ok"}


@app.get("/ready", response_model=None)
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


@app.get("/items")
def list_items() -> dict[str, Any]:
    route = "/items"
    t0 = time.perf_counter()
    db_slow_sleep()
    with get_engine().connect() as conn:
        rows = conn.execute(text("SELECT id, name FROM items ORDER BY id")).mappings().all()
    ms = (time.perf_counter() - t0) * 1000
    log.info(
        "items_list",
        extra={"extra_fields": {"http.route": route, "db.latency_ms": round(ms, 2), "row_count": len(rows)}},
    )
    return {"items": [dict(r) for r in rows]}


@app.get("/expensive")
def expensive() -> dict[str, str]:
    """CPU-ish work for overload demos."""
    route = "/expensive"
    t0 = time.perf_counter()
    x = 0
    for i in range(2_000_000):
        x += i % 997
    elapsed = time.perf_counter() - t0
    log.info(
        "expensive_done",
        extra={"extra_fields": {"http.route": route, "cpu.work_seconds": round(elapsed, 3), "checksum": x}},
    )
    return {"status": "done", "work_seconds": str(round(elapsed, 3))}


@app.get("/upstream-mock", response_model=None)
def upstream_mock() -> dict[str, Any] | Response:
    route = "/upstream-mock"
    if os.environ.get("INJECT_UPSTREAM_TIMEOUT", "").lower() in ("1", "true", "yes"):
        log.error(
            "upstream_timeout_injected",
            extra={"extra_fields": {"http.route": route, "dependency": "third_party_mock"}},
        )
        return Response(
            status_code=504,
            content=json.dumps({"detail": "upstream_timeout", "dependency": "third_party_mock"}),
            media_type="application/json",
        )
    time.sleep(0.05)
    log.info("upstream_ok", extra={"extra_fields": {"http.route": route}})
    return {"upstream": "ok"}


@app.get("/buggy")
def buggy() -> dict[str, str]:
    """Explicit exception path for software-bug class demos."""
    log.error("buggy_route_called", extra={"extra_fields": {"http.route": "/buggy"}})
    raise RuntimeError("injected_bug_for_rca_demo")
