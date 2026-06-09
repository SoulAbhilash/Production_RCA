"""Environment-driven LLM configuration (Gemini via Google Gen AI SDK, optional gateway, optional OpenAI)."""

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
    """Resolved LLM backend. Gemini wins when an API key is set.

    ``tls_verify`` is used for Gemini (google-genai / httpx) when ``mode == "gemini"``,
    and for the OpenAI-compatible gateway when ``mode == "gateway"``.
    """

    mode: str  # "gemini" | "gateway" | "openai" | "disabled"
    gemini_api_key: str | None
    gemini_model: str
    openai_api_key: str | None
    openai_model: str
    gateway_base_url: str | None
    gateway_api_key: str | None
    gateway_model: str | None
    tls_verify: bool | str
    max_retries: int
    retry_delay_s: float


def load_llm_config() -> LLMConfig:
    max_retries = max(1, int(os.environ.get("LLM_MAX_RETRIES", "3")))
    retry_delay_s = float(os.environ.get("LLM_RETRY_DELAY_S", "5"))

    gkey = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or ""
    ).strip()
    gmodel = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip() or "gemini-2.0-flash"

    if gkey:
        # httpx `verify`: True, False, or path to PEM bundle (corporate TLS inspection).
        ca = (
            os.environ.get("GEMINI_TLS_CA_BUNDLE", "").strip()
            or os.environ.get("LLM_TLS_CA_BUNDLE", "").strip()
        )
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
            openai_api_key=None,
            openai_model="gpt-4o-mini",
            gateway_base_url=None,
            gateway_api_key=None,
            gateway_model=None,
            tls_verify=gemini_tls,
            max_retries=max_retries,
            retry_delay_s=retry_delay_s,
        )

    base = (os.environ.get("LLM_GATEWAY_BASE_URL") or "").strip().rstrip("/")
    if base.endswith("/v1"):
        base = base[:-3].rstrip("/")
    gw_key = (os.environ.get("LLM_GATEWAY_API_KEY") or "").strip()
    gw_model = (os.environ.get("LLM_GATEWAY_MODEL") or "").strip()

    if base and gw_key and gw_model:
        ca = os.environ.get("LLM_TLS_CA_BUNDLE", "").strip()
        if ca:
            tls: bool | str = ca
        elif _truthy("LLM_TLS_VERIFY", default=True):
            tls = True
        else:
            tls = False
        return LLMConfig(
            mode="gateway",
            gemini_api_key=None,
            gemini_model=gmodel,
            openai_api_key=None,
            openai_model="gpt-4o-mini",
            gateway_base_url=base,
            gateway_api_key=gw_key,
            gateway_model=gw_model,
            tls_verify=tls,
            max_retries=max_retries,
            retry_delay_s=retry_delay_s,
        )

    okey = os.environ.get("OPENAI_API_KEY", "").strip()
    if okey:
        return LLMConfig(
            mode="openai",
            gemini_api_key=None,
            gemini_model=gmodel,
            openai_api_key=okey,
            openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            gateway_base_url=None,
            gateway_api_key=None,
            gateway_model=None,
            tls_verify=True,
            max_retries=max_retries,
            retry_delay_s=retry_delay_s,
        )

    return LLMConfig(
        mode="disabled",
        gemini_api_key=None,
        gemini_model=gmodel,
        openai_api_key=None,
        openai_model="gpt-4o-mini",
        gateway_base_url=None,
        gateway_api_key=None,
        gateway_model=None,
        tls_verify=True,
        max_retries=max_retries,
        retry_delay_s=retry_delay_s,
    )
