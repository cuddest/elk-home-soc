#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "Missing .env. Run: cp .env.example .env" >&2
  exit 1
fi
if [[ ! -f certs/ca.crt ]]; then
  echo "Missing certificates. Run: ./scripts/bootstrap-certs.sh" >&2
  exit 1
fi

set -a
source .env
set +a

fail() { echo "[FAIL] $*" >&2; exit 1; }
pass() { echo "[PASS] $*"; }

curl --silent --fail --cacert certs/ca.crt \
  -u "elastic:${ELASTIC_PASSWORD}" \
  "https://127.0.0.1:${ES_PORT:-9200}/_cluster/health" >/dev/null && pass "Elasticsearch HTTPS/auth"

curl --silent --fail -k "https://127.0.0.1:${KIBANA_PORT:-5601}/api/status" >/dev/null && pass "Kibana HTTPS"

curl --silent --fail "http://127.0.0.1:${NGINX_PORT:-8080}/health" >/dev/null && pass "Nginx -> Flask"

python3 generators/scenarios/run_normal_traffic.py --count 5 >/dev/null && pass "Normal HTTP traffic generated"

SOURCE_IP=185.234.72.45 MODE=failure \
  bash generators/ssh/generate_ssh_logs.sh 6 >/dev/null && pass "SSH failure telemetry generated"

python3 generators/windows/generate_windows_events.py --count 6 --mode failure --source-ip 185.234.72.45 >/dev/null && pass "Windows failure telemetry generated"

sleep 5

python3 - <<'PY'
import os
import requests
from pathlib import Path
root = Path.cwd()
verify = str(root / 'certs' / 'ca.crt')
r = requests.get(
    f"https://127.0.0.1:{os.getenv('ES_PORT','9200')}/logs-*/_count",
    auth=('elastic', os.environ['ELASTIC_PASSWORD']), verify=verify,
    timeout=15,
)
r.raise_for_status()
count = r.json()['count']
print(f"[PASS] Elasticsearch indexed {count} log event(s)")
if count == 0:
    raise SystemExit("[FAIL] Elasticsearch has no indexed lab events")
PY

echo "[PASS] Smoke test complete"
