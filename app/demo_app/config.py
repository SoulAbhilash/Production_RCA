"""Environment-backed settings."""

from __future__ import annotations

import os

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
SERVICE_NAME = os.environ.get("SERVICE_NAME", "demo-app")

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://app:app@localhost:5432/app",
)
