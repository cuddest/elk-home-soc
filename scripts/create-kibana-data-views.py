#!/usr/bin/env python3
import os
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
KIBANA_URL = os.getenv("KIBANA_URL", "https://127.0.0.1:5601")
USER = os.getenv("KIBANA_USER", "elastic")
PASSWORD = os.getenv("KIBANA_PASSWORD", "ElasticLab2026")
VERIFY = str(ROOT / "certs" / "ca.crt") if (ROOT / "certs" / "ca.crt").exists() else False

DATA_VIEWS = [
    ("logs-nginx-*", "Nginx Web Logs"),
    ("logs-application-*", "Application Logs"),
    ("logs-ssh-*", "SSH Authentication"),
    ("logs-windows-*", "Windows Security"),
    ("security-detections-*", "Security Detections"),
    ("logs-*", "All Lab Logs"),
]

s = requests.Session()
s.auth = (USER, PASSWORD)
s.verify = VERIFY
s.headers.update({"kbn-xsrf": "true", "Content-Type": "application/json"})

for title, name in DATA_VIEWS:
    r = s.post(f"{KIBANA_URL}/api/data_views/data_view", json={
        "data_view": {"title": title, "name": name, "timeFieldName": "@timestamp"}
    }, timeout=15)
    if r.status_code in (200, 201):
        print(f"Created: {name} ({title})")
    elif r.status_code == 409:
        print(f"Already exists: {name}")
    else:
        print(f"Failed {name}: {r.status_code} {r.text}")
