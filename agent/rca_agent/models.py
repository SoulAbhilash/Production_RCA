"""API payload models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IncidentPayload(BaseModel):
    incident_id: str
    source: str = Field(description="alertmanager|cloudwatch|manual")
    severity: str = "warning"
    window_start: str
    window_end: str
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
