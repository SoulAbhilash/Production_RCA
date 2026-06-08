# Production agent monitor (RCA POC)

Lab-oriented demo for **root cause analysis (RCA)** automation: a small Python API on **Postgres**, deployable to **AWS EKS**, with GitLab CI, observability hooks, and an **RCA agent** webhook service.

## Start here

Follow the full phased checklist in **[`docs/RCA_POC_PLAYBOOK.md`](docs/RCA_POC_PLAYBOOK.md)**.

## Quick local run

```bash
cp .env.example .env
docker compose up --build
```

- Health: `http://localhost:8000/health`
- Ready: `http://localhost:8000/ready`
- Items: `http://localhost:8000/items`

### Vagrant (Linux VM, 1 CPU, Docker)

From the repo root: `vagrant up` (requires VirtualBox) brings up **two** VMs: **`demo`** (Docker Compose app + Postgres, host ports 8000 / 5433) and **`agent`** (RCA agent image with optional `agent/.env` via `docker --env-file`, host **18080** → guest 8080). Use `vagrant up demo` or `vagrant up agent` for one machine; `vagrant ssh demo` / `vagrant ssh agent`. Details: [`app/README.md`](app/README.md).

## Layout

| Path | Description |
|------|-------------|
| `app/` | Demo FastAPI application |
| `agent/` | RCA webhook (`rca_agent` package); see [`agent/README.md`](agent/README.md) |
| `deploy/k8s/` | Kubernetes manifests |
| `terraform/` | VPC, ECR, EKS, GitLab OIDC IAM (poc environment) |

## License

POC / educational use. Harden before any real production use.
