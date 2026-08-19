#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose down -v
rm -f data/logs/nginx/*.log data/logs/app/*.log data/logs/ssh/*.log data/logs/windows/*.log data/logs/detections/*.jsonl 2>/dev/null || true
mkdir -p data/logs/{nginx,app,ssh,windows,detections}
touch data/logs/nginx/access.log data/logs/app/requests.log data/logs/ssh/auth.log data/logs/windows/events.log

echo "Lab reset. Start again with: ./scripts/bootstrap-certs.sh && docker compose up -d"
