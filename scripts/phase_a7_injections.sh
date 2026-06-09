#!/usr/bin/env bash
# Run inside demo VM (or: vagrant ssh demo -c "sudo bash /vagrant/scripts/phase_a7_injections.sh")
set -eu
cd /home/vagrant/compose-run

recreate_app() {
  # shellcheck disable=SC2068
  export INJECT_DB_SLOW_MS="${INJECT_DB_SLOW_MS:-0}"
  export INJECT_UPSTREAM_TIMEOUT="${INJECT_UPSTREAM_TIMEOUT:-0}"
  export INJECT_CRASH_AFTER_REQUESTS="${INJECT_CRASH_AFTER_REQUESTS:-0}"
  export INJECT_ERROR_RATE_PERCENT="${INJECT_ERROR_RATE_PERCENT:-0}"
  docker compose up -d --force-recreate app
  for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  echo "ERROR: /health did not become ready after recreate" >&2
  docker compose logs --tail=40 app >&2 || true
  exit 1
}

echo "=== A.7a INJECT_DB_SLOW_MS=400 (expect /items wall time ~0.4s+) ==="
export INJECT_DB_SLOW_MS=400 INJECT_UPSTREAM_TIMEOUT=0 INJECT_CRASH_AFTER_REQUESTS=0 INJECT_ERROR_RATE_PERCENT=0
recreate_app
curl -sS -o /dev/null -w "items_time_total=%{time_total}s http=%{http_code}\n" http://127.0.0.1:8000/items

echo "=== A.7b INJECT_UPSTREAM_TIMEOUT=1 (expect 504) ==="
export INJECT_DB_SLOW_MS=0 INJECT_UPSTREAM_TIMEOUT=1 INJECT_CRASH_AFTER_REQUESTS=0 INJECT_ERROR_RATE_PERCENT=0
recreate_app
code=$(curl -sS -o /tmp/up.json -w "%{http_code}" http://127.0.0.1:8000/upstream-mock || true)
echo "upstream-mock http=$code body=$(cat /tmp/up.json)"

echo "=== A.7c INJECT_ERROR_RATE_PERCENT=100 (expect 500 on /items) ==="
export INJECT_DB_SLOW_MS=0 INJECT_UPSTREAM_TIMEOUT=0 INJECT_CRASH_AFTER_REQUESTS=0 INJECT_ERROR_RATE_PERCENT=100
recreate_app
code=$(curl -sS -o /tmp/it.json -w "%{http_code}" http://127.0.0.1:8000/items || true)
echo "items http=$code body=$(cat /tmp/it.json)"

echo "=== A.7d INJECT_CRASH_AFTER_REQUESTS=2 (process exits on 2nd request) ==="
export INJECT_DB_SLOW_MS=0 INJECT_UPSTREAM_TIMEOUT=0 INJECT_CRASH_AFTER_REQUESTS=2 INJECT_ERROR_RATE_PERCENT=0
docker compose up -d --force-recreate app
# Do not curl /health during startup — middleware counts every request toward the crash limit.
sleep 8
curl -sS -o /dev/null -w "req1 http=%{http_code}\n" http://127.0.0.1:8000/health
curl -sS -o /dev/null -w "req2 http=%{http_code}\n" http://127.0.0.1:8000/health || true
sleep 1
echo "container status:"
docker compose ps app || true

echo "=== Reset injections to defaults ==="
export INJECT_DB_SLOW_MS=0 INJECT_UPSTREAM_TIMEOUT=0 INJECT_CRASH_AFTER_REQUESTS=0 INJECT_ERROR_RATE_PERCENT=0
docker compose up -d --force-recreate app
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo "OK: app healthy after reset"
    exit 0
  fi
  sleep 1
done
echo "ERROR: app did not recover after reset" >&2
docker compose logs --tail=40 app >&2 || true
exit 1
