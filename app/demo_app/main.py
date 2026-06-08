"""FastAPI application factory and ASGI entry."""

from __future__ import annotations

from fastapi import FastAPI

from .db import init_db
from .logging_config import log
from .middleware import tracing_and_inject
from .routers import health, items, workload

app = FastAPI(title="RCA Demo App", version="0.1.0")

app.middleware("http")(tracing_and_inject)

app.include_router(health.router)
app.include_router(items.router)
app.include_router(workload.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    log.info("startup_complete", extra={"extra_fields": {"http.route": "/startup"}})
