# PulseGate Backend API

FastAPI-powered intelligent API gateway with Redis Token Bucket rate limiting and scikit-learn Isolation Forest traffic anomaly detection.

## Key Features
- **Token Bucket Rate Limiting:** Enforces granular limits per API key using Redis (O(1) complexity) with automated in-memory fallback.
- **Unsupervised Anomaly Detection:** Real-time ML inference using scikit-learn `IsolationForest` across 6 engineered traffic features.
- **Gateway Forwarding:** High-throughput async proxying using `httpx` with destination host allowlist security.
- **Relational Analytics:** SQLite persistence of request logs, latencies, error states, and detected anomalies.
- **Full Test Coverage:** 28 automated pytest test cases validating auth, gateway routing, rate limiting, and ML predictions.

## Installation & Running

### 1. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Bootstrap Model & Database
```bash
python app/ml/train_model.py
python app/db/init_db.py
```

### 4. Run Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be available at: `http://localhost:8000/docs`

## Run Automated Tests
```bash
pytest tests -v
```
