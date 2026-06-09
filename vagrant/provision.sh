#!/usr/bin/env bash
# Installs Docker Engine + Compose plugin, kubectl, copies project off vboxsf (reliable builds),
# runs docker compose from repo root, verifies FastAPI <-> Postgres.
#
# Corporate TLS: drop PEM .crt/.pem into /vagrant/vagrant/certs/ (see vagrant/certs/README.md).

set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

WORK="/home/vagrant/compose-run"

# shellcheck source=/dev/null
source /vagrant/vagrant/install-docker.sh
# shellcheck source=/dev/null
source /vagrant/vagrant/install-kubectl.sh

# Docker builds on VirtualBox shared folders (/vagrant) often fail on Windows hosts; use ext4 copy.
mkdir -p "$WORK"
find /vagrant -mindepth 1 -maxdepth 1 ! -name ".vagrant" -exec cp -a {} "$WORK/" \;
chown -R vagrant:vagrant "$WORK"

# pip inside docker build uses the image CA store, not the host VM. Copy corporate PEMs
# into app/docker-certs/ so the Dockerfile deps stage can update-ca-certificates before pip.
BUILD_CERTS="$WORK/app/docker-certs"
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
    echo "Copied $n corporate CA file(s) to app/docker-certs for Docker build (pip/PyPI)."
  fi
fi

cd "$WORK"
docker compose version
docker compose up -d --build

echo "Waiting for Postgres health + API..."
for i in $(seq 1 45); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    break
  fi
  if [[ "$i" -eq 45 ]]; then
    echo "Timed out waiting for /health"
    docker compose ps
    docker compose logs --tail=80
    exit 1
  fi
  sleep 2
done

if ! curl -sf http://127.0.0.1:8000/ready | python3 -c "import sys, json; d=json.load(sys.stdin); sys.exit(0 if d.get(\"ready\") is True else 1)"; then
  echo "/ready did not report ready: true (DB check failed)"
  curl -sS -v http://127.0.0.1:8000/ready || true
  docker compose logs --tail=80 db app || true
  exit 1
fi

echo "OK: Postgres and API are up (/health and /ready). Try from host: http://127.0.0.1:8000/items"
