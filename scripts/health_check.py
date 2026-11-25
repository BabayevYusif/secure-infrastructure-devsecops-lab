"""Simple HTTP health check for the lab API.

Usage:
    python3 scripts/health_check.py http://127.0.0.1:8080/health
    python3 scripts/health_check.py http://127.0.0.1:8080/health --timeout 3 --retries 3

Prints one JSON line and exits 0 when healthy, 1 when unhealthy (usable from cron,
Ansible, Kubernetes exec probes or CI).
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def check(url: str, timeout: float) -> dict:
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            elapsed_ms = round((time.monotonic() - start) * 1000, 1)
            return {
                "url": url,
                "healthy": resp.status == 200,
                "status_code": resp.status,
                "response_ms": elapsed_ms,
            }
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        return {"url": url, "healthy": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP health check")
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    result = {}
    for attempt in range(1, args.retries + 1):
        result = check(args.url, args.timeout)
        result["attempt"] = attempt
        if result["healthy"]:
            break
        if attempt < args.retries:
            time.sleep(args.delay)

    print(json.dumps(result))
    return 0 if result.get("healthy") else 1


if __name__ == "__main__":
    sys.exit(main())
