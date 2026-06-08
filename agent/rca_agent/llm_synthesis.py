"""Structured RCA JSON from evidence + incident context."""

from __future__ import annotations

import json
import logging
from typing import Any

from rca_agent.config import LLMConfig
from rca_agent.llm_client import chat_completion_content
from rca_agent.models import IncidentPayload

log = logging.getLogger("rca-agent")


def _disabled_rca(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "hypothesis": "LLM disabled (set gateway env AISH_* / LLM_GATEWAY_* or OPENAI_API_KEY); review evidence manually.",
        "confidence": 0.2,
        "evidence": [{"source": "agent", "quote": evidence["logs_summary"][:500]}],
        "next_checks": [
            "Configure AISH_LLM_API_URL + AISH_LLMGTW_KEY + AISH_LLM_MODEL or OPENAI_API_KEY",
            "Run Logs Insights on pod logs",
        ],
        "blast_radius": "unknown",
        "mitigations": ["Rollback recent change", "Scale pods / fix dependency"],
    }


def _failed_rca(exc: BaseException) -> dict[str, Any]:
    return {
        "hypothesis": f"LLM call failed: {exc}",
        "confidence": 0.0,
        "evidence": [],
        "next_checks": ["Retry with smaller window", "Check API key, gateway URL, and egress"],
        "blast_radius": "unknown",
        "mitigations": [],
    }


def synthesize_rca(evidence: dict[str, Any], payload: IncidentPayload, cfg: LLMConfig) -> dict[str, Any]:
    if cfg.mode == "disabled":
        return _disabled_rca(evidence)

    system = (
        "You are an SRE assistant. Respond with JSON only, keys: "
        "hypothesis, confidence (0-1), evidence (array of {source, quote}), "
        "next_checks (array of strings), blast_radius (string), mitigations (array of strings). "
        "Ground answers in the provided evidence; do not invent log lines."
    )
    user = json.dumps({"incident": payload.model_dump(), "evidence": evidence}, default=str)
    try:
        content = chat_completion_content(
            cfg,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        return json.loads(content)
    except Exception as e:
        log.exception("llm_failed")
        return _failed_rca(e)
