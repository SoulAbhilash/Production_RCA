"""Run with: python -m rca_agent (from agent/ on PYTHONPATH)."""

from __future__ import annotations

import uvicorn

if __name__ == "__main__":
    uvicorn.run("rca_agent.app:app", host="0.0.0.0", port=8080)
