"""PulseGate Normal Traffic Simulator.

Generates realistic baseline API traffic:
- 1 to 5 requests per second
- Normal response latency (~50-250 ms)
- 97%+ HTTP 200 OK responses to /demo/hello
- Rare client (4xx) or server errors to simulate organic web traffic
"""

import os
import sys
import time
import random
import httpx
from datetime import datetime

# Configure UTF-8 console output for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000/api/gateway/request")
DEMO_BASE = os.getenv("DEMO_BASE", "http://localhost:8000")
API_KEY = os.getenv("PULSEGATE_API_KEY", "pg_live_demo1234567890abcdef")


def send_normal_request(client: httpx.Client) -> tuple[int, float]:
    """Send one normal request through the gateway."""
    # 95% to /demo/hello, 5% to /demo/slow
    target_endpoint = "/demo/hello" if random.random() < 0.95 else "/demo/slow"
    target_url = f"{DEMO_BASE}{target_endpoint}"

    payload = {
        "target_url": target_url,
        "method": "GET",
    }
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }

    start = time.perf_counter()
    try:
        resp = client.post(GATEWAY_URL, json=payload, headers=headers, timeout=5.0)
        status_code = resp.status_code
    except Exception:
        status_code = 500
    latency = round((time.perf_counter() - start) * 1000.0, 1)
    return status_code, latency


def run_normal_simulation(duration_seconds: int = 60):
    print("=" * 65)
    print("  PULSEGATE -- NORMAL TRAFFIC SIMULATOR")
    print("=" * 65)
    print(f"Gateway URL: {GATEWAY_URL}")
    print(f"API Key:     {API_KEY}")
    print(f"Rate:        1-4 requests/sec (Normal baseline)")
    print("Press Ctrl+C to stop.\n")

    start_time = time.time()
    total_sent = 0
    ok_count = 0
    err_count = 0

    with httpx.Client() as client:
        try:
            while time.time() - start_time < duration_seconds:
                status_code, lat = send_normal_request(client)
                total_sent += 1
                if status_code < 400:
                    ok_count += 1
                    status_symbol = "[OK]"
                else:
                    err_count += 1
                    status_symbol = "[ERR]"

                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] {status_symbol} HTTP {status_code} | Latency: {lat:5.1f}ms | Total: {total_sent}")

                # Sleep 0.2 to 0.7 seconds (approx 1.5 to 5 RPS)
                time.sleep(random.uniform(0.2, 0.7))

        except KeyboardInterrupt:
            print("\nSimulation stopped by user.")

    print("\n" + "-" * 40)
    print(f"Normal Simulation Completed: Sent {total_sent} reqs ({ok_count} OK, {err_count} errors)")


if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    run_normal_simulation(duration)
