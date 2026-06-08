# RCA agent

FastAPI webhook: `POST /incidents` returns stub evidence plus optional LLM-backed RCA JSON.

## Corporate TLS (`docker build` / pip)

The image runs `pip` against **PyPI** in the `deps` stage. If your network does HTTPS inspection, add PEM root(s) with `-----BEGIN CERTIFICATE-----` as `*.crt`, `*.cer`, or `*.pem` under **`agent/docker-certs/`** (gitignored except `.gitkeep`), same as [`../app/README.md`](../app/README.md).

**Vagrant:** `vagrant provision agent` copies `vagrant/certs/*` into `agent/docker-certs/` in the VM workspace before `docker build`, matching the demo VM behavior.

## Layout

| Path | Role |
|------|------|
| `rca_agent/app.py` | FastAPI routes |
| `rca_agent/models.py` | Pydantic payloads |
| `rca_agent/evidence.py` | Evidence collectors (stubs today) |
| `rca_agent/llm_client.py` | `POST …/v1/chat/completions` (OpenAI or gateway) |
| `rca_agent/llm_synthesis.py` | RCA prompt + JSON parse |
| `rca_agent/config.py` | Env → `LLMConfig` |
| `rca_agent/security.py` | Redaction helpers |

## LLM configuration

**Gateway (OpenAI-compatible, AISH-style headers)** — used when all of the following are set (aliases in parentheses):

- `AISH_LLM_API_URL` (`LLM_GATEWAY_BASE_URL`) — base URL only (no `/v1/chat/completions` suffix). You may include or omit a trailing `/v1`; the agent normalizes so the request path is not doubled.
- `AISH_LLMGTW_KEY` (`LLM_GATEWAY_API_KEY`)
- `AISH_LLM_MODEL` (`LLM_GATEWAY_MODEL`)

Optional:

- `LLM_TLS_VERIFY` — default `true`; set `false` only if your gateway uses TLS your image cannot verify (prefer `LLM_TLS_CA_BUNDLE` instead)
- `LLM_TLS_CA_BUNDLE` — path to a PEM CA bundle for custom roots
- `LLM_MAX_RETRIES` — default `3`
- `LLM_RETRY_DELAY_S` — default `5`

**OpenAI** — if gateway vars are not all set and `OPENAI_API_KEY` is present:

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default `gpt-4o-mini`)

**Disabled** — if neither gateway triple nor `OPENAI_API_KEY` is set, the handler returns a manual-review RCA stub.

### Local `agent/.env` (optional)

For development on your machine you can keep secrets in a **separate** file next to the agent:

1. Copy `agent/.env.example` → `agent/.env` and fill in values (root `.gitignore` already ignores `.env` everywhere).
2. Start the app from anywhere; on first import the agent loads `agent/.env` if that file exists.

Rules:

- **Existing OS environment variables always win** over keys in `.env` (`override=False`). That way Docker `-e` / Kubernetes `env` still override local files when you deploy.
- **`RCA_AGENT_ENV_FILE`**: if set in the real environment, that path is loaded instead of `agent/.env` (useful if you keep secrets outside the repo).

Do **not** bake `.env` into production images; use Docker `--env-file` only for lab containers if you want, and prefer Kubernetes Secrets + `env` / `envFrom` in clusters.

### Vagrant (`agent` VM)

The repo’s **`agent`** Vagrant machine builds this image and runs:

`docker run ... --env-file /home/vagrant/agent-run/agent/.env ...`

when `agent/.env` exists on your **host** (it is copied with the rest of the repo into the VM). From the host: **http://127.0.0.1:18080/health** (port **18080** is forwarded to guest **8080**). See [`../app/README.md`](../app/README.md) (Vagrant section).

## Run locally

From this directory (so `rca_agent` is importable):

```bash
pip install -r requirements.txt
uvicorn rca_agent.app:app --reload --port 8080
```

Or:

```bash
python -m rca_agent
```
