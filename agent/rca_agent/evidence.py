"""Evidence collection (stubs until CloudWatch / K8s / GitLab are wired)."""

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
        "gitlab_summary": "Set GITLAB_TOKEN + GITLAB_PROJECT_ID to pull commits for window.",
    }
