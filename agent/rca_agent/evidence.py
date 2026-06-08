"""Evidence collection (stubs until CloudWatch / K8s / GitHub are wired)."""

from __future__ import annotations

import json
from typing import Any

from rca_agent.models import IncidentPayload
from rca_agent.security import redact


def stub_evidence(payload: IncidentPayload) -> dict[str, Any]:
    return {
        "logs_summary": redact(
            f"No CloudWatch query configured. Window {payload.window_start}–{payload.window_end}. "
            f"labels={json.dumps(payload.labels)}"
        ),
        "kubernetes_summary": "In-cluster collector optional: set K8S_NAMESPACE and use ServiceAccount.",
        "github_summary": "Set GITHUB_TOKEN + GITHUB_REPOSITORY (owner/repo) to pull commits/workflows for window.",
    }
