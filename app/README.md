# Demo app (`demo-app`)

FastAPI service used in the RCA POC. Endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness (DB ping) |
| GET | `/items` | DB read |
| GET | `/expensive` | CPU-heavy path for load tests |
| GET | `/upstream-mock` | Mock outbound dependency (`INJECT_UPSTREAM_TIMEOUT`) |
| GET | `/buggy` | Throws `RuntimeError` for error logs |

Injection environment variables are documented in [../docs/RCA_POC_PLAYBOOK.md](../docs/RCA_POC_PLAYBOOK.md) Phase A.

## Local Docker build

```bash
docker build -t demo-app:local .
docker run --rm -p 8000:8000 -e DATABASE_URL=postgresql+psycopg://... demo-app:local
```

### Corporate TLS (pip / PyPI during `docker build`)

The image runs `pip` against **PyPI** in the `deps` stage. If your network does HTTPS inspection, copy the same PEM root(s) you trust on your laptop into **`app/docker-certs/`** as `*.crt`, `*.cer`, or `*.pem` (with `-----BEGIN CERTIFICATE-----`). They are **gitignored**; only `app/docker-certs/.gitkeep` stays in the repo.

Then build from the `app/` directory (or `docker compose` from the repo root as usual). The Dockerfile installs those files into the system trust store **before** `pip install`.

**Vagrant:** `vagrant provision demo` (or `vagrant provision` for all VMs) copies `vagrant/certs/*` into `app/docker-certs/` inside the **`demo`** VM workspace automatically before `docker compose build`.

## Vagrant (two Linux VMs: demo + agent)

From the **repository root** (where `docker-compose.yml` lives), with [Vagrant](https://developer.hashicorp.com/vagrant) and VirtualBox installed:

```bash
vagrant up                 # demo + agent
vagrant up demo            # app + Postgres only (host 8000, 5433)
vagrant up agent           # RCA agent only (host 18080 → guest 8080)
```

- **`demo`** (primary): Ubuntu 22.04, 1 vCPU, 2 GiB RAM. Installs Docker, copies the project off the VirtualBox shared folder, runs `docker compose up -d --build`, then checks `/health` and `/ready`.
- **`agent`**: separate VM, 1 vCPU, 1.5 GiB RAM. Builds `agent/Dockerfile` and runs `docker run` with **`--env-file`** on `agent/.env` when that file exists on the host (synced via `/vagrant`, then copied into the VM workspace). If it is missing, the container still starts in LLM-stub mode until you add `agent/.env` and run `vagrant provision agent`.

**Corporate firewall / TLS inspection:** put your organisation’s root CA PEM as `*.crt` or `*.pem` under **`vagrant/certs/`** (see [`vagrant/certs/README.md`](../vagrant/certs/README.md)), then run `vagrant provision demo` (and `vagrant provision agent` if you use that VM) again. Optional: set `HTTP_PROXY` / `HTTPS_PROXY` on the host before `vagrant up` so the VM can reach the internet.

On your host: **http://127.0.0.1:8000/health** (demo app), **http://127.0.0.1:18080/health** (RCA agent). Postgres in the **demo** VM is reachable from the host at **127.0.0.1:5433** (mapped to guest `5432` so it does not conflict with a local Postgres on **5432**).

After changing `app/` or `docker-compose.yml` on the host:

```bash
vagrant provision demo
```

After changing `agent/`:

```bash
vagrant provision agent
```
