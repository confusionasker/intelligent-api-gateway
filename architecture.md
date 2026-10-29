# PulseGate Architecture Documentation

## 1. System Architecture Overview

PulseGate is designed as an intelligent reverse-proxy API gateway that transparently intercepts client traffic, enforces high-throughput rate limiting, asynchronously routes requests to downstream microservices, logs granular metrics, and continuously analyzes traffic patterns using an unsupervised Machine Learning model (Isolation Forest) to detect anomalies in real time.

```
+---------------------------------------------------------------------------------------+
|                                    INCOMING TRAFFIC                                    |
|                   (API Clients, Mobile Apps, Traffic Simulators)                      |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
|                                 FASTAPI API GATEWAY                                   |
|                                (http://localhost:8000)                                |
+---------------------------------------------------------------------------------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
       [ Authentication & Validation ]                 [ React Dashboard ]
       - JWT Bearer Verification                       (Telemetry, Charts, Alerts)
       - X-API-Key DB Lookup                                      |
                    |                                             |
                    v                                             |
       [ Token Bucket Rate Limiter ]                              |
       - Thread-Safe In-Memory Store (O(1), zero setup)           |
       - Optional Redis backend support                           |
                    |                                             |
          +---------+---------+                                   |
          |                   |                                   |
     [Allowed]           [Exceeded]                               |
          |                   |                                   |
          v                   v                                   |
  [ Gateway Forwarder ] [ HTTP 429 Too Many Requests ]            |
  - Target URL Validation                                         |
  - Async HTTPX Client                                            |
  - Latency Measurement                                           |
          |                                                       |
          v                                                       |
  [ Downstream Service ]                                          |
  (e.g., /demo/hello, Port 8001)                                  |
          |                                                       |
          +-------------------+-----------------------------------+
                              |
                              v
                +----------------------------+
                |    REQUEST METRICS PIPELINE|
                +----------------------------+
                              |
                              v
                [ SQLite `request_logs` ]
                (timestamp, endpoint, latency, status_code, is_error)
                              |
                              v
                [ Feature Engineering (1-Min Window) ]
                [req_count, rps, avg_lat, err_rate, unique_endpoints, 5xx_count]
                              |
                              v
                [ Isolation Forest ML Model ]
                (Contamination=0.03, n_estimators=100)
                              |
                    +---------+---------+
                    |                   |
               [Score >= 0]        [Score < 0]
                 (Normal)           (Anomaly)
                    |                   |
                    v                   v
             [ Baseline State ]  [ Persist to `anomalies` Table ]
                                 [ Compute Human-Readable Reason ]
                                        |
                                        v
                                 [ WebSocket / 5s Polling Alert ]
                                 "⚠ TRAFFIC ANOMALY DETECTED"
```

---

## 2. Component Breakdown

### 2.1 Authentication & Security (`app.core.security`, `app.api.routes_auth`)
- **Password Hashing:** Uses `bcrypt` with automated per-user cryptographic salts.
- **JWT Session Tokens:** Issues signed JSON Web Tokens (`HS256`) containing subject claims and standard expiration (`exp`) times.
- **API Key Engine:** Generates cryptographically secure keys with prefix `pg_live_` using Python's `secrets.token_hex(16)`. Keys are indexed in SQLite for sub-millisecond lookup and can be dynamically assigned individual rate limits and active/revoked states.
- **SSRF Prevention:** The gateway checks destination hosts against an allowlist (`localhost`, `127.0.0.1`, etc.) preventing attackers from abusing the gateway to probe internal networks.

### 2.2 Token Bucket Rate Limiter (`app.services.rate_limiter`)
- **Algorithm:** Models rate limiting via a bucket of capacity $C$ refilled at rate $r = C / W$ tokens/second.
- **In-Memory Engine (Default):** Stores `{ "tokens": float, "last_updated": timestamp }` in memory using `threading.Lock()` for thread safety across concurrent async requests. Zero external Redis installation or setup needed.
- **Optional Redis Backend:** Can be switched to Redis via `RATE_LIMITER_BACKEND=redis` in `.env` for multi-node deployments.
- **Time Complexity:** $O(1)$ constant time lookup and update.
- **Space Complexity:** $O(K)$ where $K$ is the number of active API keys.
- **Pruning:** Automatically cleans up stale tokens inactive for $> 2 \times W$.

### 2.3 Gateway Forwarding Service (`app.services.gateway_service`)
- Proxies HTTP traffic asynchronously using `httpx.AsyncClient`.
- Employs strict connection and read timeouts (5s / 10s) to prevent thread exhaustion.
- Strips sensitive hop-by-hop headers while forwarding `X-Forwarded-By` and `X-Consumer-Key-Id`.
- Calculates high-precision response latency via `time.perf_counter()`.

### 2.4 Metrics Aggregation (`app.services.metrics_service`)
- Every incoming request through the gateway records a row in `request_logs`.
- Indexes on `timestamp`, `endpoint`, and `is_error` enable efficient sliding window queries.
- Aggregates high-level summaries (Total, Success, Failed, RPS, Average Latency) and time-series buckets.

### 2.5 Machine Learning Engine (`app.ml`)
- **Model:** `sklearn.ensemble.IsolationForest`.
- **Why Isolation Forest?**
  1. **Unsupervised:** Web traffic does not come with pre-existing labels of "attack" vs "normal". Isolation Forest isolates anomalies without requiring supervised labels.
  2. **Linear Time Complexity:** Constructs an ensemble of random isolation trees ($iTrees$). Because anomalies require fewer random splits to isolate, they have noticeably shorter path lengths from the tree root:
     $$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
  3. **High Dimensional Robustness:** Easily processes multiple features (traffic volume, latency, error rate, 5xx counts) simultaneously rather than relying on brittle one-dimensional thresholds.
- **Feature Vector:** Extracted from 1-minute sliding windows:
  1. `request_count`: Total requests in window
  2. `requests_per_second`: Request throughput rate
  3. `average_latency`: Mean response duration (ms)
  4. `error_rate`: Ratio of 4xx/5xx responses (0.0 to 1.0)
  5. `unique_endpoints`: Diversity of paths requested
  6. `status_5xx_count`: Critical downstream failures

### 2.6 Explainability Engine (`app.ml.predict.explain_anomaly_reasons`)
While the Isolation Forest mathematically classifies points as inliers (`+1`) or outliers (`-1`), interviewers and site-reliability engineers require interpretable explanations. PulseGate inspects feature vector deviations against baseline bounds to generate intuitive diagnostic reasons:
- High traffic spike: *"Unusual traffic volume (520 req/min) detected."*
- High latency: *"Abnormal response latency (840 ms) detected."*
- High error rate: *"High API error rate (22.5%) detected."*
- Multi-vector degradation: *"Multiple traffic metrics deviated from normal baseline."*

### 2.7 Frontend React Dashboard (`frontend/src`)
- **Aesthetic:** Dark glassmorphic user interface with neon glowing accents and micro-animations.
- **Real-Time Polling:** Automatically queries `/api/metrics/summary`, `/api/metrics/timeseries`, and `/api/anomalies/latest` every 5 seconds.
- **Interactive Test Lab:** Embedded quick-action controls allowing interviewers to immediately trigger single requests, 35-request bursts, or manual ML evaluations without switching windows.
