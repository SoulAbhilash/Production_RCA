"""Environment-driven LLM configuration (Google Gemini via Gen AI SDK only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bootstrap_dotenv() -> None:
    """Load optional `agent/.env` for local dev. OS env always wins (override=False)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    explicit = os.environ.get("RCA_AGENT_ENV_FILE", "").strip()
    if explicit:
        load_dotenv(explicit, override=False)
        return
    agent_dir = Path(__file__).resolve().parent.parent
    candidate = agent_dir / ".env"
    if candidate.is_file():
        load_dotenv(candidate, override=False)


_bootstrap_dotenv()


def _truthy(name: str, default: bool = True) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class LLMConfig:
    """Resolved Gemini backend."""

    mode: str  # "gemini" | "disabled"
    gemini_api_key: str | None
    gemini_model: str
    tls_verify: bool | str
    max_retries: int
    retry_delay_s: float


def load_llm_config() -> LLMConfig:
    max_retries = max(1, int(os.environ.get("GEMINI_MAX_RETRIES", "3")))
    retry_delay_s = float(os.environ.get("GEMINI_RETRY_DELAY_S", "5"))

    gkey = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    ).strip()
    gmodel = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"

    if not gkey:
        return LLMConfig(
            mode="disabled",
            gemini_api_key=None,
            gemini_model=gmodel,
            tls_verify=True,
            max_retries=max_retries,
            retry_delay_s=retry_delay_s,
        )

    # httpx `verify` (used by google-genai): True, False, or path to PEM bundle (corporate TLS inspection).
    ca = os.environ.get("GEMINI_TLS_CA_BUNDLE", "").strip()
    if ca:
        gemini_tls: bool | str = ca
    elif _truthy("GEMINI_TLS_VERIFY", default=True):
        gemini_tls = True
    else:
        gemini_tls = False

    return LLMConfig(
        mode="gemini",
        gemini_api_key=gkey,
        gemini_model=gmodel,
        tls_verify=gemini_tls,
        max_retries=max_retries,
        retry_delay_s=retry_delay_s,
    )
