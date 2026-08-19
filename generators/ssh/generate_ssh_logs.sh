#!/bin/sh
set -eu

COUNT="${1:-20}"
SOURCE_IP="${SOURCE_IP:-185.234.72.45}"
MODE="${MODE:-mixed}"
LOG_FILE="/logs/ssh/auth.log"
USERS="root admin ubuntu deploy analyst test"

mkdir -p "$(dirname "$LOG_FILE")"

choose_user() {
  set -- $USERS
  n=$(( $(od -An -N1 -tu1 /dev/urandom | tr -d ' ') % $# + 1 ))
  eval "printf '%s' \${$n}"
}

for i in $(seq 1 "$COUNT"); do
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  user=$(choose_user)

  if [ "$MODE" = "failure" ]; then
    result=failure
  elif [ "$MODE" = "success" ]; then
    result=success
  else
    if [ $((i % 6)) -eq 0 ]; then result=success; else result=failure; fi
  fi

  python3 - "$ts" "$user" "$SOURCE_IP" "$result" >> "$LOG_FILE" <<'PY'
import json, sys, uuid

ts, user, ip, result = sys.argv[1:]
record = {
    "@timestamp": ts,
    "event": {
        "kind": "event",
        "category": ["authentication"],
        "type": ["start"],
        "action": "ssh_login",
        "outcome": "success" if result == "success" else "failure",
        "code": "ssh_auth",
    },
    "user": {"name": user},
    "source": {"ip": ip},
    "network": {"transport": "tcp"},
    "service": {"name": "sshd", "type": "ssh"},
    "ssh": {
        "auth_method": "password",
        "session_id": uuid.uuid4().hex[:12],
    },
    "lab": {"synthetic": True, "scenario": "ssh_authentication"},
}
print(json.dumps(record, separators=(",", ":")))
PY
done

echo "Generated $COUNT SSH events ($MODE) from $SOURCE_IP"
