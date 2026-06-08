"""FastAPI application: health + incident webhook."""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from typing import Any

from fastapi import FastAPI

from rca_agent.config import load_llm_config
from rca_agent.evidence import stub_evidence
from rca_agent.llm_synthesis import synthesize_rca
from rca_agent.models import IncidentPayload

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("rca-agent")

app = FastAPI(title="RCA Agent", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/incidents")
def incidents(payload: IncidentPayload) -> dict[str, Any]:
    t0 = time.perf_counter()
    evidence = stub_evidence(payload)
    cfg = load_llm_config()
    rca = synthesize_rca(evidence, payload, cfg)
    elapsed = time.perf_counter() - t0
    out = {
        "incident_id": payload.incident_id,
        "processing_seconds": round(elapsed, 3),
        "rca": rca,
        "raw_evidence": evidence,
    }
    log.info("incident_processed %s", json.dumps({"incident_id": payload.incident_id, "seconds": elapsed}))
    return out
