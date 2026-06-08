"""OpenAI-compatible chat completions via direct OpenAI or corporate gateway (AISH-style headers)."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from rca_agent.config import LLMConfig

log = logging.getLogger("rca-agent.llm")


def chat_completion_content(
    cfg: LLMConfig,
    *,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    response_format: dict[str, str] | None = None,
) -> str:
    if cfg.mode == "disabled":
        raise RuntimeError("LLM is not configured")

    body: dict[str, Any] = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        body["response_format"] = response_format

    if cfg.mode == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        body["model"] = cfg.openai_model
        headers = {
            "Authorization": f"Bearer {cfg.openai_api_key}",
            "Content-Type": "application/json",
        }
        verify: bool | str = True
        timeout = 60.0
    else:
        url = f"{cfg.gateway_base_url}/v1/chat/completions"
        body["model"] = cfg.gateway_model
        headers = {
            "Content-Type": "application/json",
            "apikey": cfg.gateway_api_key or "",
            "model": cfg.gateway_model or "",
        }
        verify = cfg.tls_verify
        timeout = 120.0

    last_err: BaseException | None = None
    for attempt in range(cfg.max_retries):
        try:
            with httpx.Client(timeout=timeout, verify=verify) as client:
                r = client.post(url, headers=headers, json=body)
                r.raise_for_status()
                data = r.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    return content
        except BaseException as e:
            last_err = e
            log.warning("llm_attempt_failed attempt=%s err=%s", attempt + 1, e)
        if attempt < cfg.max_retries - 1:
            time.sleep(cfg.retry_delay_s)

    raise RuntimeError(f"LLM failed after {cfg.max_retries} attempts") from last_err
