#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

MODE=""
REAL_SSH=0

usage() {
  cat <<USAGE
Usage:
  ./lab.sh start --mode simulation
  ./lab.sh start --mode real
  ./lab.sh start --mode hybrid [--real-ssh]
  ./lab.sh stop
  ./lab.sh status
  ./lab.sh smoke

Modes:
  simulation  Local generators + Docker web/app sources. No external endpoints required.
  real        ELK backend + Nginx/Flask. Exposes Logstash Beats port for real Filebeat/Winlogbeat endpoints.
  hybrid      Simulation sources + real endpoint integration. Use --real-ssh to add the real SSH container.
USAGE
}

compose_args() {
  local mode="$1"
  case "$mode" in
    simulation)
      printf '%s\n' docker compose --profile simulation
      ;;
    real)
      printf '%s\n' docker compose -f docker-compose.yml -f docker-compose.real.yml
      ;;
    hybrid)
      printf '%s\n' docker compose -f docker-compose.yml -f docker-compose.real.yml --profile simulation
      ;;
    *)
      echo "Unknown mode: $mode" >&2
      exit 2
      ;;
  esac
}

start() {
  local mode="$1"
  shift
  local -a args
  read -r -a args <<< "$(compose_args "$mode")"

  if [[ "$mode" == "real" || "$mode" == "hybrid" ]]; then
    echo "Starting $mode mode; Logstash Beats will be published on ${LOGSTASH_BEATS_BIND:-127.0.0.1}:${LOGSTASH_BEATS_PORT:-5044}."
  else
    echo "Starting simulation mode. External endpoints are not required."
  fi

  if (( REAL_SSH )); then
    args+=(--profile real-ssh)
  fi

  "${args[@]}" up -d
}

stop() {
  docker compose -f docker-compose.yml -f docker-compose.real.yml --profile simulation --profile real-ssh down
}

case "${1:-}" in
  start)
    shift
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --mode)
          MODE="${2:-}"; shift 2
          ;;
        --real-ssh)
          REAL_SSH=1; shift
          ;;
        *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
      esac
    done
    [[ -n "$MODE" ]] || { usage; exit 2; }
    start "$MODE"
    ;;
  stop)
    stop
    ;;
  status)
    docker compose ps
    ;;
  smoke)
    ./scripts/smoke-test.sh
    ;;
  *)
    usage
    exit 2
    ;;
esac
