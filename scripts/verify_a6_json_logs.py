"""Parse docker compose log lines from stdin; validate Phase A.6 JSON shape."""
from __future__ import annotations

import json
import re
import sys

REQUIRED = {"timestamp", "level", "message", "service", "trace_id"}
# docker compose prefixes lines like "app-1  | {...}"
PREFIX = re.compile(r"^app-\d+\s+\|\s+")


def main() -> int:
    ok = 0
    saw_items = False
    for line in sys.stdin:
        line = line.rstrip("\n")
        m = PREFIX.match(line)
        payload = line[m.end() :] if m else line
        payload = payload.strip()
        if not payload.startswith("{"):
            continue
        try:
            o = json.loads(payload)
        except json.JSONDecodeError as e:
            print("FAIL JSON:", e, "line:", payload[:200], file=sys.stderr)
            return 1
        missing = REQUIRED - o.keys()
        if missing:
            print("FAIL missing:", missing, file=sys.stderr)
            return 1
        ok += 1
        if o.get("message") == "items_list":
            saw_items = True
            if "http.route" not in o or "db.latency_ms" not in o:
                print("FAIL items_list missing http.route or db.latency_ms", file=sys.stderr)
                return 1
    if ok == 0:
        print("FAIL: no JSON application log lines found", file=sys.stderr)
        return 1
    if not saw_items:
        print("WARN: no items_list line yet — run GET /items then re-fetch logs", file=sys.stderr)
    print(f"OK: {ok} JSON log line(s); items_list has http.route + db.latency_ms: {saw_items}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
