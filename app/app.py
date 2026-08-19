import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)
LOG_PATH = "/logs/app/requests.log"

logger = logging.getLogger("labapp")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_PATH)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def emit_event(**kwargs):
    event = {
        "@timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "service": {"name": "lab-api", "type": "web"},
        "event": {"kind": "event", "category": ["web"], "type": ["access"]},
        "request": {"id": request.headers.get("X-Request-ID", f"req-{uuid.uuid4().hex[:12]}")},
        "source": {"ip": request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")},
        "http": {
            "request": {"method": request.method},
            "version": "1.1",
        },
        "url": {"path": request.path},
        "user_agent": {"original": request.headers.get("User-Agent", "unknown")},
        "event": {"kind": "event", "category": ["web"], "type": ["access"]},
    }
    event["http"]["response"] = {"status_code": kwargs.pop("status_code")}
    event["event"]["duration"] = kwargs.pop("duration_ns")
    event.update(kwargs)
    logger.info(json.dumps(event, separators=(",", ":")))


@app.before_request
def before_request():
    request._start = time.perf_counter_ns()


@app.after_request
def after_request(response):
    duration_ns = time.perf_counter_ns() - getattr(request, "_start", time.perf_counter_ns())
    emit_event(status_code=response.status_code, duration_ns=duration_ns)
    return response


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "lab-api"})


@app.get("/api/products")
def products():
    return jsonify({
        "products": [
            {"id": 1, "name": "Laptop", "price": 1299},
            {"id": 2, "name": "Keyboard", "price": 99},
            {"id": 3, "name": "Monitor", "price": 349},
        ]
    })


@app.get("/api/cart")
def cart():
    return jsonify({"items": 2, "total": 1398})


@app.post("/api/checkout")
def checkout():
    return jsonify({"status": "accepted", "order_id": f"ord-{uuid.uuid4().hex[:8]}"}), 201


@app.post("/api/login")
def login():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "unknown")
    password = body.get("password", "")
    if username == "analyst" and password == "LabPassword!":
        return jsonify({"authenticated": True}), 200
    return jsonify({"authenticated": False, "error": "invalid_credentials"}), 401


@app.get("/api/admin")
def admin():
    role = request.headers.get("X-Role", "guest")
    if role != "admin":
        return jsonify({"error": "forbidden"}), 403
    return jsonify({"status": "admin access granted"})


@app.get("/api/error")
def error():
    return jsonify({"error": "synthetic server error"}), 500


@app.get("/api/slow")
def slow():
    delay = random.uniform(0.25, 0.75)
    time.sleep(delay)
    return jsonify({"delay_seconds": round(delay, 3)})


@app.get("/")
def root():
    return jsonify({
        "service": "ELK Security Monitoring Lab API",
        "endpoints": [
            "/api/health", "/api/products", "/api/cart", "/api/checkout",
            "/api/login", "/api/admin", "/api/error", "/api/slow"
        ]
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "not_found", "path": request.path}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
