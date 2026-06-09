#!/usr/bin/env bash
# Second VM: Docker + kubectl, build agent image from repo copy, run with docker --env-file agent/.env when present.
# Corporate TLS: same vagrant/certs/ as demo VM (see vagrant/certs/README.md).

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

WORK="/home/vagrant/agent-run"

# shellcheck source=/dev/null
source /vagrant/vagrant/install-docker.sh
# shellcheck source=/dev/null
source /vagrant/vagrant/install-kubectl.sh

mkdir -p "$WORK"
find /vagrant -mindepth 1 -maxdepth 1 ! -name ".vagrant" -exec cp -a {} "$WORK/" \;
chown -R vagrant:vagrant "$WORK"

# pip inside docker build uses the image CA store, not the host VM. Copy corporate PEMs
# into agent/docker-certs/ so the Dockerfile deps stage can update-ca-certificates before pip.
BUILD_CERTS="$WORK/agent/docker-certs"
mkdir -p "$BUILD_CERTS"
find "$BUILD_CERTS" -mindepth 1 -maxdepth 1 \( -name '*.crt' -o -name '*.cer' -o -name '*.pem' \) -delete 2>/dev/null || true
SRC_CERTS="$WORK/vagrant/certs"
if [[ -d "$SRC_CERTS" ]]; then
  n=0
  shopt -s nullglob
  for f in "$SRC_CERTS"/*.crt "$SRC_CERTS"/*.cer "$SRC_CERTS"/*.pem; do
    [[ -f "$f" ]] || continue
    grep -q "BEGIN CERTIFICATE" "$f" 2>/dev/null || continue
    cp "$f" "$BUILD_CERTS/build-$(basename "$f")"
    n=$((n + 1))
  done
  shopt -u nullglob
  if [[ "$n" -gt 0 ]]; then
    echo "Copied $n corporate CA file(s) to agent/docker-certs for Docker build (pip/PyPI)."
  fi
fi

docker rm -f rca-agent 2>/dev/null || true

cd "$WORK/agent"
docker build -t rca-agent:local .

ENV_FILE="$WORK/agent/.env"
run_opts=(docker run -d --name rca-agent --restart unless-stopped -p 8080:8080)
if [[ -f "$ENV_FILE" ]]; then
  echo "Using docker --env-file $ENV_FILE (LLM keys from host agent/.env)."
  run_opts+=(--env-file "$ENV_FILE")
else
  echo "WARN: $ENV_FILE not found — container starts without LLM env (stub RCA). Create agent/.env on the host."
fi
run_opts+=(rca-agent:local)
"${run_opts[@]}"

echo "Waiting for agent /health..."
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1; then
    break
  fi
  if [[ "$i" -eq 30 ]]; then
    echo "Timed out waiting for agent /health"
    docker logs --tail=80 rca-agent 2>/dev/null || true
    exit 1
  fi
  sleep 2
done

echo "OK: RCA agent is up. From host: http://127.0.0.1:18080/health (port 18080 -> guest 8080)."
