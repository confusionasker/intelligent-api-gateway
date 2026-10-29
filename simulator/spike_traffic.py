"""PulseGate Traffic Spike Simulator.

Generates an aggressive burst of abnormal traffic:
- 25 to 50 requests per second
- High latency endpoints (/demo/slow)
- Error-inducing endpoints (/demo/error)
- Triggers Token Bucket 429 Rate Limit rejections
- Causes Isolation Forest ML model to detect a high-confidence traffic anomaly!
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
EVAL_URL = os.getenv("EVAL_URL", "http://localhost:8000/api/anomalies/evaluate")


def send_spike_request(client: httpx.Client) -> tuple[int, float]:
    """Send one spike request with mixed endpoints."""
    # 60% /demo/hello, 25% /demo/slow (high latency), 15% /demo/error (500)
    roll = random.random()
    if roll < 0.60:
        target_endpoint = "/demo/hello"
    elif roll < 0.85:
        target_endpoint = "/demo/slow"
    else:
        target_endpoint = "/demo/error"

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
        resp = client.post(GATEWAY_URL, json=payload, headers=headers, timeout=4.0)
        status_code = resp.status_code
    except Exception:
        status_code = 504
    latency = round((time.perf_counter() - start) * 1000.0, 1)
    return status_code, latency


def run_spike_simulation(total_requests: int = 150):
    print("=" * 65)
    print("  !! PULSEGATE -- TRAFFIC SPIKE SIMULATOR !!")
    print("=" * 65)
    print(f"Gateway URL:    {GATEWAY_URL}")
    print(f"API Key:        {API_KEY}")
    print(f"Target Volume:  {total_requests} requests burst (~30-50 RPS)")
    print("Firing traffic spike now...\n")

    start_time = time.time()
    ok_count = 0
    rate_limited_count = 0
    error_count = 0

    with httpx.Client() as client:
        for i in range(1, total_requests + 1):
            status_code, lat = send_spike_request(client)
            if status_code == 200:
                ok_count += 1
                sym = "[OK]"
            elif status_code == 429:
                rate_limited_count += 1
                sym = "[RATE-LIMITED 429]"
            else:
                error_count += 1
                sym = "[ERROR 5xx]"

            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {sym} HTTP {status_code} | Lat: {lat:5.1f}ms | Req #{i}")

            # Micro-sleep to achieve high concurrency burst (25-50 RPS)
            time.sleep(random.uniform(0.015, 0.04))

        elapsed = max(0.1, time.time() - start_time)
        rps = round(total_requests / elapsed, 1)

        print("\n" + "=" * 65)
        print("  SPIKE TRANSMISSION SUMMARY")
        print("=" * 65)
        print(f"Total Sent:       {total_requests} requests in {elapsed:.2f}s ({rps} req/sec)")
        print(f"Successful (200): {ok_count}")
        print(f"Rate-Limited:     {rate_limited_count}")
        print(f"Failed / Errors:  {error_count}")

        # Trigger real-time Isolation Forest evaluation to verify anomaly detection
        print("\nTriggering Isolation Forest ML Evaluation...")
        try:
            eval_resp = client.post(EVAL_URL, timeout=5.0)
            if eval_resp.status_code == 200:
                res = eval_resp.json()
                is_anomaly = res.get("is_anomaly")
                reason = res.get("reason")
                score = res.get("anomaly_score")
                if is_anomaly:
                    print("\n" + "!" * 65)
                    print("  [ALERT] TRAFFIC ANOMALY DETECTED BY ISOLATION FOREST! [ALERT]")
                    print("!" * 65)
                    print(f"  Anomaly Score:  {score}")
                    print(f"  Explanation:    {reason}")
                    print("  Status:         Anomaly stored in SQLite database!")
                    print("  Dashboard UI:   Alert banner will now appear in RED!")
                    print("!" * 65)
                else:
                    print(f"ML Result: Normal (Score: {score}). Send more requests to exceed boundary.")
            else:
                print(f"Evaluation response: {eval_resp.status_code}")
        except Exception as exc:
            print(f"Could not connect to evaluation endpoint: {exc}")


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    run_spike_simulation(count)
