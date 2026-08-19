#!/usr/bin/env python3
"""Run deterministic lab detections against Elasticsearch.

This is intentionally a transparent educational detector rather than a production
rule engine. It demonstrates aggregation, thresholds, correlation, and alert
creation against ECS-style events.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
CA = ROOT / "certs" / "ca.crt"

ES_URL = os.getenv("ES_URL", "https://127.0.0.1:9200")
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "ElasticLab2026")


class ES:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.auth = (ES_USER, ES_PASSWORD)
        self.session.verify = str(CA) if CA.exists() else False
        self.session.headers.update({"Content-Type": "application/json"})

    def search(self, query: dict[str, Any]) -> dict[str, Any]:
        r = self.session.post(f"{ES_URL}/logs-*/_search", json=query, timeout=15)
        r.raise_for_status()
        return r.json()

    def index_alert(self, alert: dict[str, Any]) -> None:
        r = self.session.post(f"{ES_URL}/security-detections-lab/_doc/{alert['event']['id']}", json=alert, timeout=15)
        r.raise_for_status()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_alert(name: str, severity: str, reason: str, source_ip: str | None, fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "@timestamp": now_iso(),
        "event": {
            "id": uuid.uuid4().hex,
            "kind": "alert",
            "category": ["intrusion_detection"],
            "type": ["info"],
            "action": name,
            "severity": {"low": 20, "medium": 50, "high": 80}.get(severity, 50),
            "reason": reason,
        },
        "rule": {"name": name, "category": "ELK Security Monitoring Lab"},
        "source": {"ip": source_ip} if source_ip else {},
        "labels": {"synthetic": True, "severity": severity},
        "lab": fields,
    }


def ssh_bruteforce(es: ES) -> list[dict[str, Any]]:
    q = {
        "size": 0,
        "query": {"bool": {"filter": [
            {"term": {"event.dataset": "lab.ssh"}},
            {"term": {"event.outcome": "failure"}},
            {"range": {"@timestamp": {"gte": "now-5m"}}},
        ]}},
        "aggs": {"sources": {"terms": {"field": "source.ip", "size": 20},
                                "aggs": {"users": {"terms": {"field": "user.name", "size": 10}}}}},
    }
    data = es.search(q)
    alerts = []
    for bucket in data.get("aggregations", {}).get("sources", {}).get("buckets", []):
        if bucket["doc_count"] >= 5:
            users = [u["key"] for u in bucket["users"]["buckets"]]
            alerts.append(make_alert(
                "ssh_bruteforce",
                "high",
                f"{bucket['doc_count']} failed SSH authentications in five minutes",
                bucket["key"],
                {"count": bucket["doc_count"], "target_users": users, "window": "5m"},
            ))
    return alerts


def windows_bruteforce(es: ES) -> list[dict[str, Any]]:
    q = {
        "size": 0,
        "query": {"bool": {"filter": [
            {"term": {"event.dataset": "lab.windows"}},
            {"term": {"event.code": "4625"}},
            {"range": {"@timestamp": {"gte": "now-5m"}}},
        ]}},
        "aggs": {"sources": {"terms": {"field": "source.ip", "size": 20},
                                "aggs": {"users": {"terms": {"field": "user.name", "size": 10}}}}},
    }
    data = es.search(q)
    alerts = []
    for bucket in data.get("aggregations", {}).get("sources", {}).get("buckets", []):
        if bucket["doc_count"] >= 5:
            alerts.append(make_alert(
                "windows_bruteforce",
                "high",
                f"{bucket['doc_count']} Windows 4625 failures in five minutes",
                bucket["key"],
                {"count": bucket["doc_count"], "target_users": [u["key"] for u in bucket["users"]["buckets"]]},
            ))
    return alerts


def web_scan(es: ES) -> list[dict[str, Any]]:
    q = {
        "size": 0,
        "query": {"bool": {"filter": [
            {"term": {"event.dataset": "lab.nginx"}},
            {"term": {"http.response.status_code": 404}},
            {"range": {"@timestamp": {"gte": "now-5m"}}},
        ]}},
        "aggs": {"sources": {"terms": {"field": "source.ip", "size": 20}}},
    }
    data = es.search(q)
    return [make_alert("web_scanning", "medium",
                       f"{b['doc_count']} HTTP 404s from one source in five minutes",
                       b["key"], {"count": b["doc_count"], "window": "5m"})
            for b in data.get("aggregations", {}).get("sources", {}).get("buckets", []) if b["doc_count"] >= 10]


def application_errors(es: ES) -> list[dict[str, Any]]:
    q = {
        "size": 0,
        "query": {"bool": {"filter": [
            {"term": {"event.dataset": "lab.application"}},
            {"range": {"http.response.status_code": {"gte": 500}}},
            {"range": {"@timestamp": {"gte": "now-5m"}}},
        ]}},
        "aggs": {"paths": {"terms": {"field": "url.path", "size": 20}}},
    }
    data = es.search(q)
    alerts = []
    for b in data.get("aggregations", {}).get("paths", {}).get("buckets", []):
        if b["doc_count"] >= 3:
            alerts.append(make_alert("application_error_burst", "medium",
                                     f"{b['doc_count']} application 5xx responses in five minutes",
                                     None, {"path": b["key"], "count": b["doc_count"]}))
    return alerts


def failure_then_success(es: ES) -> list[dict[str, Any]]:
    q = {
        "size": 0,
        "query": {"bool": {"filter": [
            {"terms": {"event.outcome": ["failure", "success"]}},
            {"term": {"event.category": "authentication"}},
            {"range": {"@timestamp": {"gte": "now-10m"}}},
        ]}},
        "aggs": {"sources": {"terms": {"field": "source.ip", "size": 50},
            "aggs": {
                "failures": {"filter": {"term": {"event.outcome": "failure"}}},
                "successes": {"filter": {"term": {"event.outcome": "success"}}},
            }}},
    }
    data = es.search(q)
    alerts = []
    for b in data.get("aggregations", {}).get("sources", {}).get("buckets", []):
        if b["failures"]["doc_count"] >= 3 and b["successes"]["doc_count"] >= 1:
            alerts.append(make_alert("authentication_failure_then_success", "high",
                                     "Repeated authentication failures followed by success",
                                     b["key"], {"failures": b["failures"]["doc_count"], "successes": b["successes"]["doc_count"], "window": "10m"}))
    return alerts


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="Run all detections once")
    p.add_argument("--no-index", action="store_true", help="Print alerts without indexing them")
    args = p.parse_args()

    es = ES()
    detections = [ssh_bruteforce, windows_bruteforce, web_scan, application_errors, failure_then_success]
    all_alerts: list[dict[str, Any]] = []
    for fn in detections:
        all_alerts.extend(fn(es))

    for alert in all_alerts:
        if not args.no_index:
            es.index_alert(alert)
        print(json.dumps(alert, indent=2))

    print(f"Detected {len(all_alerts)} alert(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
