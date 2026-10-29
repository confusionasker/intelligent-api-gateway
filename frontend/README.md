# PulseGate Frontend Dashboard

Real-time API gateway telemetry and anomaly alert dashboard built with React 18, TypeScript, Vite, and Recharts.

## Features
- **Real-time Live Polling:** Automatically refreshes traffic metrics every 5 seconds without manual page reloads.
- **Visual Anomaly Alerts:** Prominent pulsing banner when an anomaly is classified by the ML engine.
- **Traffic Telemetry:** Recharts visualization of traffic volume, average response latency, and error rate percentages.
- **Route Analytics:** Per-endpoint breakdown of throughput and performance.
- **Interactive Quick Test Lab:** Fire single demo calls, burst traffic spikes, and trigger ML model evaluations directly from the UI.
- **API Key Management:** Generate, copy, and revoke client API keys and rate limits.

## Setup & Running

```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Build for production
npm run build
```
Dashboard will be accessible at: `http://localhost:5173`
Default demo login: `admin` / `admin123`
