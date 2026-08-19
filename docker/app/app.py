from flask import Flask, request, jsonify
import json, time, random, uuid
from datetime import datetime

app = Flask(__name__)
LOG_FILE = "/logs/app/requests.log"

def write_log(method, endpoint, status, latency):
    entry = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request_id": "req-" + str(uuid.uuid4())[:8],
        "method": method,
        "endpoint": endpoint,
        "status_code": status,
        "latency_ms": latency
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

@app.route("/api/health")
def health():
    latency = random.randint(5, 30)
    write_log("GET", "/api/health", 200, latency)
    return jsonify({"status": "ok"})

@app.route("/api/products")
def products():
    latency = random.randint(20, 80)
    write_log("GET", "/api/products", 200, latency)
    return jsonify({"products": ["prod-101", "prod-202", "prod-303"]})

@app.route("/api/checkout", methods=["POST"])
def checkout():
    latency = random.randint(100, 500)
    data = request.get_json(silent=True) or {}
    if not data.get("item"):
        write_log("POST", "/api/checkout", 400, latency)
        return jsonify({"error": "missing item"}), 400
    write_log("POST", "/api/checkout", 200, latency)
    return jsonify({"order_id": "ord-" + str(uuid.uuid4())[:8], "status": "confirmed"})

@app.route("/api/cart", methods=["POST"])
def cart():
    latency = random.randint(10, 60)
    write_log("POST", "/api/cart", 200, latency)
    return jsonify({"cart": "updated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
