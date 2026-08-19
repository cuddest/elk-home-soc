import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

LOG = "/logs/windows/events.log"
DEFAULT_USERS = ["Administrator", "svc_backup", "analyst", "deploy"]


def event(event_id: str, source_ip: str, user: str, outcome: str) -> dict:
    return {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event": {
            "kind": "event",
            "category": ["authentication"],
            "type": ["start"],
            "code": event_id,
            "outcome": outcome,
            "action": "logon",
        },
        "winlog": {
            "channel": "Security",
            "provider_name": "Microsoft-Windows-Security-Auditing",
            "event_data": {
                "IpAddress": source_ip,
                "TargetUserName": user,
                "LogonType": "10",
            },
            "computer_name": "DC01-LAB",
        },
        "user": {"name": user},
        "source": {"ip": source_ip},
        "host": {"name": "DC01-LAB"},
        "message": f"Synthetic Windows Security Event {event_id}",
        "lab": {"synthetic": True, "scenario": "windows_authentication"},
        "agent": {"type": "winlogbeat-simulator", "version": "9.4.4"},
        "event_sequence": uuid.uuid4().hex[:12],
    }


def write_batch(count: int, mode: str, source_ip: str):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        for i in range(count):
            user = random.choice(DEFAULT_USERS)
            if mode == "failure":
                eid, out = "4625", "failure"
            elif mode == "success":
                eid, out = "4624", "success"
            else:
                eid, out = ("4625", "failure") if i % 5 else ("4624", "success")
            fh.write(json.dumps(event(eid, source_ip, user, out), separators=(",", ":")) + "\n")


def daemon(source_ip: str):
    while True:
        write_batch(1, "mixed", source_ip)
        time.sleep(8)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--mode", choices=["failure", "success", "mixed"], default="mixed")
    parser.add_argument("--source-ip", default="10.10.20.25")
    parser.add_argument("--daemon", action="store_true")
    args = parser.parse_args()

    if args.daemon:
        daemon(args.source_ip)
    else:
        write_batch(args.count, args.mode, args.source_ip)
        print(f"Generated {args.count} Windows events in {LOG}")
