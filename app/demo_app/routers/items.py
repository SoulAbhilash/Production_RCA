"""Primary DB-backed API."""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter
from sqlalchemy import text

from ..db import get_engine
from ..injection import db_slow_sleep
from ..logging_config import log

router = APIRouter(tags=["items"])


@router.get("/items")
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
