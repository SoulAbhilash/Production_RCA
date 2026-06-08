"""CPU, upstream mock, and explicit error paths for demos."""

from __future__ import annotations

import json
import os
import time
from typing import Any

from fastapi import APIRouter, Response

from ..logging_config import log

router = APIRouter(tags=["workload"])


@router.get("/expensive")
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


@router.get("/upstream-mock", response_model=None)
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


@router.get("/buggy")
def buggy() -> dict[str, str]:
    """Explicit exception path for software-bug class demos."""
    log.error("buggy_route_called", extra={"extra_fields": {"http.route": "/buggy"}})
    raise RuntimeError("injected_bug_for_rca_demo")
