# PulseGate — Intelligent API Gateway with AI Traffic Anomaly Detection

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-IsolationForest-orange.svg)](https://scikit-learn.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org/)
[![Tests](https://img.shields.io/badge/Tests-28%20Passed-brightgreen.svg)]()

> A production-style, beginner-friendly API Gateway featuring **Token Bucket rate limiting via Redis**, asynchronous reverse proxying, relational telemetry logging, and real-time **unsupervised Machine Learning anomaly detection using Isolation Forest**. Designed for clean software architecture and interview excellence (e.g., Infosys Specialist Programmer / Digital Specialist Engineer).

---

## 1. Project Overview

Modern cloud architectures place an API Gateway at the edge of infrastructure. While traditional gateways rely on static rule thresholds (e.g., "block if > 100 requests"), sophisticated microservices require intelligent anomaly detection to detect stealthy DDoS spikes, resource exhaustion, and cascade failure states.

**PulseGate** solves this by:
1. Acting as a reverse proxy in front of backend microservices.
2. Authenticating clients via **JWT** and secure **API Keys** (`pg_live_...`).
3. Enforcing high-performance **Token Bucket Rate Limiting** ($O(1)$) using Redis.
4. Aggregating traffic metrics into sliding 1-minute time windows.
5. Feeding 6-dimensional feature vectors into an **Isolation Forest** model to detect anomalies without hardcoded heuristics.
6. Displaying real-time telemetry, interactive traffic simulators, and pulsing anomaly alerts on a modern glassmorphic React dashboard.

---

## 2. Architecture & Request Flow

```
Client / Simulator
        ↓
PulseGate Gateway (FastAPI, Port 8000)
        ↓
Authentication (JWT / API Key)
        ↓
Token Bucket Rate Limiter (Redis Hash, O(1))
        ↓
Target Allowlist Check & Async Forwarding (HTTPX)
        ↓
Downstream Service (e.g. /demo/hello)
        ↓
Request Metrics Recording (SQLite request_logs)
        ↓
Feature Engineering (1-Minute Sliding Window)
        ↓
Isolation Forest Inference (scikit-learn)
        ↓
[Normal] → Telemetry Charts (Recharts)
[Anomaly] → Database Anomaly Record + "⚠ Traffic Anomaly Detected" Dashboard Alert
```

---

## 3. Technology Stack

- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, SQLite, Redis / fakeredis, HTTPX, PyJWT, bcrypt.
- **Machine Learning:** scikit-learn (`IsolationForest`), pandas, numpy, joblib.
- **Frontend:** React 18, TypeScript, Vite, Axios, Recharts, Lucide-React, Vanilla CSS (Glassmorphism & Dark Mode).
- **Testing:** pytest, pytest-asyncio, FastAPI TestClient.
- **Simulators:** Async/sync traffic burst generators for normal and spike traffic.
- **Docker-Free Local Development:** Runs natively on Windows, Linux, and macOS without requiring containers.

---

## 4. Repository Structure

```
intelligent-api-gateway/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI app, lifespan, CORS, error handling
│   │   ├── api/
│   │   │   ├── routes_auth.py          # /api/auth & /api/keys endpoints
│   │   │   ├── routes_gateway.py       # /api/gateway/request & demo targets
│   │   │   ├── routes_metrics.py       # /api/metrics summary, timeseries, endpoints
│   │   │   ├── routes_anomaly.py       # /api/anomalies list, latest status, evaluate
│   │   │   └── routes_health.py        # /health diagnostic check
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic Settings
│   │   │   ├── security.py             # bcrypt hashing & JWT token handling
│   │   │   └── dependencies.py         # DB session, JWT user, and API key dependencies
│   │   ├── models/
│   │   │   ├── user.py                 # User table
│   │   │   ├── api_key.py              # ApiKey table
│   │   │   ├── request_log.py          # RequestLog table (indexed)
│   │   │   └── anomaly.py              # Anomaly table
│   │   ├── schemas/
│   │   │   ├── auth.py                 # Pydantic auth schemas
│   │   │   ├── gateway.py              # Gateway request/response schemas
│   │   │   ├── metrics.py              # Analytics schemas
│   │   │   └── anomaly.py              # Anomaly schemas
│   │   ├── services/
│   │   │   ├── rate_limiter.py         # Token Bucket service with Redis & fallback
│   │   │   ├── gateway_service.py      # Async HTTPX proxy & SSRF protection
│   │   │   ├── metrics_service.py      # SQLite aggregation & time-series
│   │   │   ├── anomaly_service.py      # Window evaluation & anomaly persistence
│   │   │   └── ml_service.py           # ML orchestration
│   │   ├── ml/
│   │   │   ├── feature_engineering.py  # 6-D feature vector extractor
│   │   │   ├── train_model.py          # Baseline synthetic bootstrapping & training
│   │   │   ├── predict.py              # Model inference & explainability engine
│   │   │   └── model/                  # Serialized isolation_forest.joblib
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy engine & session factory
│   │   │   └── init_db.py              # Schema generation & admin seeding
│   │   └── utils/
│   │       ├── logger.py               # Structured logging
│   │       └── time_utils.py           # UTC time window helpers
│   ├── tests/
│   │   ├── conftest.py                 # Pytest fixtures & in-memory DB
│   │   ├── test_auth.py                # 6 Auth tests
│   │   ├── test_rate_limiter.py        # 5 Rate limiter & API key tests
│   │   ├── test_gateway.py             # 7 Gateway forwarding & security tests
│   │   ├── test_metrics.py             # 3 Metrics aggregation tests
│   │   └── test_anomaly.py             # 7 ML Isolation Forest tests
│   ├── requirements.txt                # Stable backend dependencies
│   ├── .env.example                    # Environment variable template
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Top navigation, status badge, live toggle
│   │   │   ├── MetricCard.tsx          # Stat cards with glow badges
│   │   │   ├── TrafficChart.tsx        # Recharts AreaChart (volume)
│   │   │   ├── LatencyChart.tsx        # Recharts LineChart (latency & error rate)
│   │   │   ├── AnomalyTable.tsx        # Table of detected ML anomalies
│   │   │   ├── EndpointTable.tsx       # Per-route breakdown
│   │   │   └── ApiKeyModal.tsx         # Key generation & copy modal
│   │   ├── pages/
│   │   │   ├── Login.tsx               # Auth page with quick demo autofill
│   │   │   └── Dashboard.tsx           # Full telemetry & alert center
│   │   ├── services/
│   │   │   └── api.ts                  # Axios client & API endpoints
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript interfaces
│   │   ├── App.tsx                     # Main router
│   │   ├── main.tsx                    # React DOM root
│   │   └── index.css                   # Glassmorphic dark styling
│   ├── package.json
│   └── README.md
│
├── simulator/
│   ├── normal_traffic.py               # 1-5 RPS baseline traffic simulator
│   ├── spike_traffic.py                # 25-50 RPS burst simulator
│   └── requirements.txt
│
├── architecture.md                     # Deep-dive architecture design doc
├── .gitignore
└── README.md                           # Main documentation
```

---

## 5. Core Algorithms & Machine Learning Details

### 5.1 Token Bucket vs. Sliding Window Log

| Attribute | Token Bucket (Used in PulseGate) | Sliding Window Log |
| :--- | :--- | :--- |
| **Concept** | Bucket fills at rate $r$; each request removes 1 token. | Stores timestamp of every request in sorted set. |
| **Time Complexity** | **$O(1)$** constant time per request. | **$O(\log N)$** insertion, $O(N)$ removal. |
| **Space Complexity** | **$O(1)$** per key (only stores tokens & timestamp). | **$O(N)$** memory scales linearly with traffic. |
| **Burst Handling** | Smoothly permits bursts up to capacity $C$. | Strict rate enforcement, higher memory under load. |
| **Storage Engine** | **In-Memory Thread-Safe Dict (Default)** or optional Redis | Redis ZADD + ZREMRANGEBYSCORE. |

#### Time Complexity Explanation:
In PulseGate, checking rate limits does not iterate through prior requests. It computes elapsed time $\Delta t = T_{\text{now}} - T_{\text{last}}$, refills tokens proportionally $\min(C, \text{tokens} + \Delta t \cdot r)$, and stores the result back in memory protected by `threading.Lock`. This executes in **$O(1)$ constant time** with zero external Redis setup required.

### 5.2 Isolation Forest for Traffic Anomaly Detection

#### Why Isolation Forest is ideal for API Gateways:
1. **Unsupervised Learning:** Production API traffic is unlabelled. Attack patterns, DDoS bursts, and database locks evolve dynamically. Isolation Forest requires no labeled training data.
2. **Linear Time & Low Memory:** Isolation Forest builds an ensemble of random trees ($iTrees$). Outliers are isolated near the root with very few random splits, while normal points require deep trees.
3. **Multivariate Analysis:** Instead of a single static rule (e.g. `requests > 100`), Isolation Forest evaluates 6 interdependent dimensions simultaneously. A small traffic increase coupled with a 5x latency jump is correctly recognized as an anomaly.

#### Mathematical Foundation:
Given a dataset of $n$ instances, the average path length of an unsuccessful search in a Binary Search Tree is:
$$c(n) = 2 \ln(n - 1) + 0.5772156649 - \frac{2(n - 1)}{n}$$
The anomaly score $s(x, n)$ for an instance $x$ is:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Where $E(h(x))$ is the expected path length across the forest of isolation trees:
- If $E(h(x)) \to 0$, $s \to 1$ $\rightarrow$ **High confidence anomaly**.
- If $E(h(x)) \to n - 1$, $s \to 0$ $\rightarrow$ **Normal baseline instance**.

#### Feature Engineering (1-Minute Sliding Window):
1. `request_count`: Total requests received in 60 seconds.
2. `requests_per_second`: Request throughput rate ($req / 60$).
3. `average_latency`: Mean duration of downstream responses in ms.
4. `error_rate`: Ratio of 4xx/5xx responses ($0.0$ to $1.0$).
5. `unique_endpoints`: Count of distinct API paths accessed.
6. `status_5xx_count`: Critical downstream server failures.

#### Rule-Based vs. ML Anomaly Detection:
- **Rule-Based:** Uses hardcoded `if requests > 100: flag_error()`. Brittle, fails on slow-and-low attacks, and cannot account for latency degradation.
- **ML-Based (Isolation Forest):** Identifies non-linear multidimensional outliers. If latency triples while error rate rises to 15%, the model triggers an anomaly even if request volume stayed below a naive threshold.

---

## 6. Installation & Quick Start

### Prerequisites
- Python 3.12+ installed
- Node.js v18+ and npm installed
- Redis (Optional: if Redis is not installed, PulseGate automatically switches to built-in in-memory fallback!)

---

### Step 1: Set Up Backend Environment

```bash
# Clone repository
cd intelligent-api-gateway

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### Step 2: Bootstrap Database & ML Model

```bash
# Set PYTHONPATH to include backend
$env:PYTHONPATH="backend"   # Windows PowerShell
# or: export PYTHONPATH="backend" # Linux/macOS

# Train Isolation Forest baseline model
python backend/app/ml/train_model.py

# Initialize SQLite database and seed admin account
python backend/app/db/init_db.py
```
*Output:*
- Model artifact saved to `backend/app/ml/model/isolation_forest.joblib`
- SQLite tables created in `pulsegate.db`
- Default Admin Account seeded: `admin` / `admin123`
- Default API Key generated: `pg_live_demo1234567890abcdef`

### Step 3: Start Backend API

```bash
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

---

### Step 4: Set Up & Start Frontend Dashboard

Open a new terminal:
```bash
cd intelligent-api-gateway/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Dashboard URL: `http://localhost:5173`

---

## 7. Running the Full Demo Walkthrough

1. **Open Frontend:** Navigate to `http://localhost:5173`.
2. **Login:** Click **"Fill Demo Credentials"** (`admin` / `admin123`) and click **Sign In**.
3. **Inspect Initial State:** The dashboard indicates `🟢 NORMAL TRAFFIC` with 0 anomalies.
4. **Copy API Key:** Click the **API Keys** button in the navbar to view your key (`pg_live_demo1234567890abcdef`).
5. **Run Normal Traffic Simulator:**
   Open a third terminal:
   ```bash
   python simulator/normal_traffic.py 30
   ```
   *Generates 1-4 RPS baseline requests to `/demo/hello`.*
   The dashboard updates every 5 seconds showing steady latency (~100-150 ms) and green status.
6. **Trigger Traffic Spike Simulation:**
   ```bash
   python simulator/spike_traffic.py 120
   ```
   *Sends a 35+ RPS burst with high latency and 500 error injections.*
   - Rate Limiter actively blocks requests exceeding the token bucket limit with **HTTP 429 Too Many Requests**.
   - Isolation Forest automatically scores the traffic window, flags an outlier ($score < 0$), and writes to the `anomalies` table.
7. **Observe Dashboard Alert:**
   The dashboard switches to `🔴 ANOMALY DETECTED` and displays the pulsing red alert banner:
   ```
   ⚠ Traffic Anomaly Detected
   Reason: Multiple traffic metrics deviated from normal baseline: Unusual traffic volume; High API error rate
   Request Count: 120 / min
   Average Latency: 320 ms
   Error Rate: 22.5%
   ```

*(Alternatively, you can test this without terminal commands by clicking **"Simulate Traffic Spike"** directly in the Dashboard Quick Test Lab!)*

---

## 8. Running Automated Tests

PulseGate includes 28 test cases verifying authentication, rate limiting, request forwarding, metrics aggregation, and ML anomaly predictions.

```bash
$env:PYTHONPATH="backend"
pytest backend/tests -v
```

### Test Coverage Summary:
- `test_auth.py` (6 tests): Registration, duplicate check, bcrypt password validation, JWT issuance, profile authentication, unauthenticated rejection.
- `test_rate_limiter.py` (5 tests): API key generation, deactivation, token bucket capacity checks, 429 retry-after calculation, rate limit header formatting.
- `test_gateway.py` (7 tests): Forwarding proxy, allowlist host verification, missing key rejection, invalid key rejection, demo targets (`/demo/hello`, `/demo/slow`, `/demo/error`).
- `test_metrics.py` (3 tests): Database metric logging, summary API calculations, time-series aggregation, per-endpoint stats.
- `test_anomaly.py` (7 tests): Model serialization loading, 6-feature vector extraction, normal traffic prediction (`1`), spike traffic prediction (`-1`), explainability engine reasoning, anomaly retrieval APIs.

---

## 9. API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System health check (DB, Redis, ML status) | No |
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Login and receive signed JWT token | No |
| `GET` | `/api/auth/me` | Fetch logged-in user profile | Bearer JWT |
| `POST` | `/api/keys` | Generate a new `pg_live_...` API key | Bearer JWT |
| `GET` | `/api/keys` | List active API keys | Bearer JWT |
| `DELETE` | `/api/keys/{id}` | Revoke an API key | Bearer JWT |
| `POST` | `/api/gateway/request` | Reverse-proxy client request downstream | `X-API-Key` |
| `GET` | `/api/metrics/summary` | Overall gateway performance summary | No |
| `GET` | `/api/metrics/timeseries` | 1-minute bucketed metrics for charts | No |
| `GET` | `/api/metrics/endpoints` | Per-route latency and error metrics | No |
| `GET` | `/api/anomalies` | List detected ML traffic anomalies | No |
| `GET` | `/api/anomalies/latest` | Latest health status and anomaly event | No |
| `POST` | `/api/anomalies/evaluate`| Trigger immediate Isolation Forest evaluation | No |
| `GET` | `/demo/hello` | Demo downstream service endpoint | No |
| `GET` | `/demo/slow` | Demo delayed response endpoint | No |
| `GET` | `/demo/error` | Demo 500 error endpoint | No |

---

## 10. Database Schema & Indexing

SQLite database schema managed via SQLAlchemy ORM:

```
users (id PK, username UNIQUE INDEX, hashed_password, is_active, created_at)
  │
  └──< api_keys (id PK, key UNIQUE INDEX, name, user_id FK INDEX, rate_limit, is_active, created_at)
        │
        └──< request_logs (id PK, timestamp INDEX, endpoint INDEX, method, api_key_id FK, status_code, latency_ms, is_error INDEX)

anomalies (id PK, timestamp INDEX, request_count, average_latency_ms, error_rate, anomaly_score, reason, created_at)
```

### Why Database Indexes are Critical:
1. **$O(\log N)$ Time-Window Queries:** The dashboard and anomaly service filter requests by time (`timestamp >= now - 60s`). Without an index on `timestamp`, SQLite must perform a full table scan ($O(N)$), causing latency to degrade as traffic logs grow. A B-tree index reduces search to $O(\log N)$.
2. **Instant API Key Validation:** Authenticating incoming gateway requests requires finding the key record. The index on `api_keys.key` ensures validation completes in microseconds.
3. **Composite Index (`timestamp`, `endpoint`):** Speeds up endpoint-specific timeseries aggregations.

---

## 11. Production Upgrade Roadmap (Future Scope)

While PulseGate is optimized for local clarity and zero-friction execution, production enterprise gateways would implement:
- **Apache Kafka / Redpanda:** For high-throughput asynchronous metric stream ingestion instead of direct synchronous database writes.
- **Distributed Redis Cluster:** For synchronized rate-limiting across multi-region gateway nodes.
- **PostgreSQL / TimescaleDB:** For hyper-table time-series storage and automated partitioning.
- **OpenTelemetry & Prometheus/Grafana:** For standardized distributed tracing and alerting hooks to PagerDuty/Slack.
- **Model Drift Detection:** Utilizing Evidently AI to detect concept drift in traffic baselines and trigger automated re-training pipelines.