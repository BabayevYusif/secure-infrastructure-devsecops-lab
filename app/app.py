"""Minimal demo service used to practice secure delivery (CI/CD, hardening, Kubernetes).

Endpoints:
  GET /health          liveness/readiness probe
  GET /api/v1/status   service metadata (version, environment)
"""
import os
import time

from flask import Flask, jsonify

app = Flask(__name__)
START_TIME = time.time()
VERSION = os.getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("APP_ENV", "lab")


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.get("/api/v1/status")
def status():
    return jsonify(
        service="devsecops-lab-api",
        version=VERSION,
        environment=ENVIRONMENT,
        uptime_seconds=round(time.time() - START_TIME, 1),
    )


if __name__ == "__main__":
    # Local development only. In containers the app runs under gunicorn.
    app.run(host="127.0.0.1", port=8080)
