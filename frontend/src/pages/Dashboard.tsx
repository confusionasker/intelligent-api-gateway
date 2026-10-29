import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Clock,
  AlertTriangle,
  Flame,
  Server,
  Filter,
  Send,
  Play,
  Brain,
  RotateCcw,
  Globe,
} from 'lucide-react';
import type {
  MetricsSummary,
  TimeSeriesPoint,
  EndpointStat,
  Anomaly,
  LatestAnomalyStatus,
  ApiKey,
  User,
} from '../types';
import {
  metricsApi,
  anomalyApi,
  apiKeyApi,
  gatewayApi,
  authApi,
} from '../services/api';
import { Navbar } from '../components/Navbar';
import { MetricCard } from '../components/MetricCard';
import { TrafficChart } from '../components/TrafficChart';
import { LatencyChart } from '../components/LatencyChart';
import { AnomalyTable } from '../components/AnomalyTable';
import { EndpointTable } from '../components/EndpointTable';
import { ApiKeyModal } from '../components/ApiKeyModal';

interface DashboardProps {
  onLogout: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  // State
  const [user, setUser] = useState<User | null>(null);
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [isKeysOpen, setIsKeysOpen] = useState(false);
  const [isPolling, setIsPolling] = useState(true);

  // Filters
  const [timeRange, setTimeRange] = useState<string>('1h');
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>('');
  const [anomalyOnly, setAnomalyOnly] = useState<boolean>(false);

  // Metrics data
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [timeseries, setTimeseries] = useState<TimeSeriesPoint[]>([]);
  const [endpoints, setEndpoints] = useState<EndpointStat[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [latestStatus, setLatestStatus] = useState<LatestAnomalyStatus | null>(null);

  const [actionFeedback, setActionFeedback] = useState<string | null>(null);
  const [simulating, setSimulating] = useState(false);

  // Custom Real-Time API Gateway Request Console
  const [customUrl, setCustomUrl] = useState('https://httpbin.org/get');
  const [customMethod, setCustomMethod] = useState('GET');
  const [customLoading, setCustomLoading] = useState(false);
  const [customSpiking, setCustomSpiking] = useState(false);
  const [customResult, setCustomResult] = useState<any>(null);

  const activeKey = keys.find((k) => k.is_active)?.key || 'pg_live_demo1234567890abcdef';

  // Fetch all dashboard data
  const loadData = useCallback(async () => {
    try {
      const [sum, ts, ep, anom, status] = await Promise.all([
        metricsApi.getSummary(timeRange, selectedEndpoint || undefined),
        metricsApi.getTimeseries(timeRange, selectedEndpoint || undefined),
        metricsApi.getEndpoints(),
        anomalyApi.getRecentAnomalies(50),
        anomalyApi.getLatestStatus(),
      ]);
      setSummary(sum);
      setTimeseries(ts);
      setEndpoints(ep);
      setAnomalies(anom);
      setLatestStatus(status);
    } catch (err) {
      console.error('Failed to fetch dashboard metrics:', err);
    }
  }, [timeRange, selectedEndpoint]);

  // Initial user and API keys load
  useEffect(() => {
    const fetchInitialMeta = async () => {
      try {
        const u = await authApi.getCurrentUser();
        setUser(u);
        const k = await apiKeyApi.listKeys();
        setKeys(k);
      } catch (err) {
        console.error('Initial metadata fetch failed:', err);
      }
    };
    fetchInitialMeta();
  }, []);

  // Polling loop (every 5 seconds)
  useEffect(() => {
    loadData();
    if (!isPolling) return;

    const interval = setInterval(() => {
      loadData();
    }, 5000);

    return () => clearInterval(interval);
  }, [loadData, isPolling]);

  // Key operations
  const handleCreateKey = async (name: string, rateLimit: number) => {
    const newKey = await apiKeyApi.createKey(name, rateLimit);
    setKeys((prev) => [newKey, ...prev]);
  };

  const handleDeactivateKey = async (id: number) => {
    await apiKeyApi.deactivateKey(id);
    setKeys((prev) => prev.map((k) => (k.id === id ? { ...k, is_active: false } : k)));
  };

  // Quick Action: Send Single Gateway Request
  const handleSendSingleTest = async () => {
    setActionFeedback('Sending request through PulseGate...');
    try {
      const resp = await gatewayApi.forwardRequest('http://localhost:8000/demo/hello', activeKey);
      setActionFeedback(`✅ Success: ${resp.data?.message || '200 OK'} (${resp.latency_ms} ms)`);
      loadData();
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 429) {
        setActionFeedback('⚠️ Rate limit exceeded (HTTP 429 Too Many Requests)');
      } else {
        setActionFeedback(`❌ Error: ${err.message}`);
      }
    }
    setTimeout(() => setActionFeedback(null), 4000);
  };

  // Quick Action: Simulate Traffic Spike from UI
  const handleSimulateSpike = async () => {
    setSimulating(true);
    setActionFeedback('🚀 Firing traffic burst (45 requests with rate-limiting & error spikes)...');
    try {
      const burstPromises = Array.from({ length: 45 }).map((_, i) => {
        let target = 'http://localhost:8000/demo/hello';
        if (i % 6 === 0) target = 'http://localhost:8000/demo/error';
        else if (i % 3 === 0) target = 'http://localhost:8000/demo/slow';
        return gatewayApi.forwardRequest(target, activeKey).catch(() => null);
      });
      await Promise.all(burstPromises);
      // Wait briefly for all DB writes to complete, then evaluate ML anomaly
      await new Promise((r) => setTimeout(r, 350));
      const evalResult = await anomalyApi.triggerEvaluation(60);
      if (evalResult.is_anomaly) {
        setActionFeedback(`🚨 ANOMALY DETECTED by Isolation Forest! Score: ${evalResult.anomaly_score}`);
      } else {
        setActionFeedback('Traffic burst evaluated by ML model.');
      }
      await loadData();
    } catch (err: any) {
      setActionFeedback(`Simulation error: ${err.message}`);
    } finally {
      setSimulating(false);
      setTimeout(() => setActionFeedback(null), 7000);
    }
  };

  // Quick Action: Send Custom Real-time API Request through Gateway
  const handleSendCustomRealRequest = async () => {
    if (!customUrl.trim()) return;
    setCustomLoading(true);
    setCustomResult(null);
    try {
      const resp = await gatewayApi.forwardRequest(customUrl.trim(), activeKey, customMethod);
      setCustomResult({
        success: true,
        status_code: resp.status_code || 200,
        latency_ms: resp.latency_ms,
        data: resp.data,
        headers: resp.headers,
      });
      setActionFeedback(`✅ Real API Proxy Success (${resp.latency_ms} ms)`);
      await loadData();
    } catch (err: any) {
      const status = err.response?.status;
      const respData = err.response?.data;
      setCustomResult({
        success: false,
        status_code: status || 500,
        latency_ms: respData?.latency_ms || 0,
        error: respData?.detail || err.message,
      });
      if (status === 429) {
        setActionFeedback('⚠️ Rate limit exceeded (HTTP 429 Too Many Requests)');
      } else {
        setActionFeedback(`Proxy Error: ${err.message}`);
      }
      await loadData();
    } finally {
      setCustomLoading(false);
    }
  };

  // Quick Action: Send Burst Spike to ANY custom URL to trigger Anomaly Detection
  const handleSendCustomBurstSpike = async () => {
    if (!customUrl.trim()) return;
    setCustomSpiking(true);
    setActionFeedback(`🚀 Firing 35 concurrent requests to ${customUrl.trim()}...`);
    try {
      const burstPromises = Array.from({ length: 35 }).map(() =>
        gatewayApi.forwardRequest(customUrl.trim(), activeKey, customMethod).catch(() => null)
      );
      await Promise.all(burstPromises);
      await new Promise((r) => setTimeout(r, 400));
      const evalResult = await anomalyApi.triggerEvaluation(60);
      if (evalResult.is_anomaly) {
        setActionFeedback(`🚨 ANOMALY DETECTED by Isolation Forest! Score: ${evalResult.anomaly_score}`);
      } else {
        setActionFeedback('Traffic burst sent. Check metrics.');
      }
      await loadData();
    } catch (err: any) {
      setActionFeedback(`Burst error: ${err.message}`);
    } finally {
      setCustomSpiking(false);
      setTimeout(() => setActionFeedback(null), 7000);
    }
  };

  // Quick Action: Trigger ML Anomaly Evaluation
  const handleTriggerEvaluation = async () => {
    setActionFeedback('Evaluating traffic against Isolation Forest model...');
    try {
      const res = await anomalyApi.triggerEvaluation(60);
      if (res.is_anomaly) {
        setActionFeedback(`🚨 Anomaly Detected: ${res.reason}`);
      } else {
        setActionFeedback(`🟢 Normal Traffic: ${res.reason} (Score: ${res.anomaly_score})`);
      }
      loadData();
    } catch (err: any) {
      setActionFeedback(`Evaluation error: ${err.message}`);
    }
    setTimeout(() => setActionFeedback(null), 5000);
  };

  // Latest Anomaly record if active
  const activeAnomaly = latestStatus?.latest_anomaly;
  const showAnomalyAlert = latestStatus?.status_label === 'ANOMALY' || latestStatus?.is_anomaly;

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '40px' }}>
      {/* Top Navigation */}
      <Navbar
        user={user}
        status={latestStatus}
        isPolling={isPolling}
        onTogglePolling={() => setIsPolling(!isPolling)}
        onRefresh={loadData}
        onOpenKeys={() => setIsKeysOpen(true)}
        onLogout={onLogout}
      />

      <main style={{ maxWidth: '1440px', margin: '0 auto', padding: '0 24px' }}>
        {/* SECTION 19: PROMINENT ANOMALY ALERT BANNER */}
        {showAnomalyAlert && activeAnomaly && (
          <div className="anomaly-alert-banner" style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                <div style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  background: 'rgba(244, 63, 94, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid var(--accent-rose)',
                }}>
                  <AlertTriangle size={24} color="var(--accent-rose)" />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#ffffff', letterSpacing: '-0.01em' }}>
                      ⚠ Traffic Anomaly Detected
                    </h2>
                    <span className="badge badge-rose">Isolation Forest Alert</span>
                  </div>
                  <p style={{ color: '#fda4af', fontWeight: 600, fontSize: '0.9rem', marginTop: '4px' }}>
                    Reason: {activeAnomaly.reason}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '10px', fontSize: '0.85rem' }}>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Request Count: </span>
                      <strong style={{ color: '#fff' }}>{activeAnomaly.request_count} / min</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Average Latency: </span>
                      <strong style={{ color: '#fff' }}>{activeAnomaly.average_latency_ms} ms</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Error Rate: </span>
                      <strong style={{ color: '#fff' }}>{(activeAnomaly.error_rate * 100).toFixed(1)}%</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Anomaly Score: </span>
                      <strong className="code-pill" style={{ color: '#fda4af' }}>{activeAnomaly.anomaly_score.toFixed(3)}</strong>
                    </div>
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Timestamp: </span>
                      <strong style={{ color: '#fff' }}>
                        {new Date(activeAnomaly.timestamp).toLocaleTimeString('en-IN', {
                          timeZone: 'Asia/Kolkata',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                          hour12: true,
                        })}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={handleTriggerEvaluation}
                className="btn btn-secondary"
                style={{ alignSelf: 'center', fontSize: '0.8rem' }}
              >
                <RotateCcw size={14} />
                <span>Re-Evaluate ML Model</span>
              </button>
            </div>
          </div>
        )}

        {/* Action Feedback Toast */}
        {actionFeedback && (
          <div style={{
            marginBottom: '20px',
            padding: '12px 18px',
            borderRadius: '10px',
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            color: '#c7d2fe',
            fontSize: '0.85rem',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <Activity size={16} />
            <span>{actionFeedback}</span>
          </div>
        )}

        {/* TOP METRIC CARDS */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <MetricCard
            title="Total Requests"
            value={summary?.total_requests ?? 0}
            subtitle={`${summary?.successful_requests ?? 0} OK · ${summary?.failed_requests ?? 0} Failed`}
            icon={<Server size={20} color="var(--accent-cyan)" />}
            accentColor="cyan"
          />
          <MetricCard
            title="Average Latency"
            value={`${summary?.average_latency_ms ?? 0} ms`}
            subtitle="Downstream response time"
            icon={<Clock size={20} color="var(--accent-indigo)" />}
            accentColor="indigo"
          />
          <MetricCard
            title="Error Rate"
            value={`${summary?.error_rate ?? 0}%`}
            subtitle="4xx & 5xx HTTP responses"
            icon={<AlertTriangle size={20} color={summary && summary.error_rate > 10 ? 'var(--accent-rose)' : 'var(--accent-emerald)'} />}
            accentColor={summary && summary.error_rate > 10 ? 'rose' : 'emerald'}
          />
          <MetricCard
            title="Current Traffic"
            value={`${summary?.requests_per_second ?? 0} RPS`}
            subtitle="Requests per second rate"
            icon={<Flame size={20} color="var(--accent-amber)" />}
            accentColor="amber"
          />
          <MetricCard
            title="Anomalies Detected"
            value={anomalies.length}
            subtitle={latestStatus?.status_label === 'ANOMALY' ? '⚠ Outlier Active' : 'Normal Baseline'}
            icon={<Brain size={20} color="var(--accent-rose)" />}
            accentColor="rose"
          />
        </div>

        {/* QUICK DEMO ACTION BAR */}
        <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc' }}>
                🚀 Quick Test Lab:
              </span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                Test gateway forwarding and ML anomaly detection directly:
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <button
                onClick={handleSendSingleTest}
                className="btn btn-secondary"
                style={{ fontSize: '0.8rem' }}
              >
                <Send size={14} color="var(--accent-cyan)" />
                <span>Send Normal Req (/demo/hello)</span>
              </button>

              <button
                onClick={handleSimulateSpike}
                className="btn btn-danger"
                style={{ fontSize: '0.8rem' }}
                disabled={simulating}
              >
                <Play size={14} color="var(--accent-rose)" />
                <span>{simulating ? 'Firing Spike...' : 'Simulate Traffic Spike (Burst)'}</span>
              </button>

              <button
                onClick={handleTriggerEvaluation}
                className="btn btn-secondary"
                style={{ fontSize: '0.8rem' }}
              >
                <Brain size={14} color="var(--accent-indigo)" />
                <span>Run Isolation Forest</span>
              </button>
            </div>
          </div>
        </div>

        {/* REAL-TIME LIVE API GATEWAY REQUEST CONSOLE */}
        <div className="glass-panel" style={{ padding: '20px 24px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 12px rgba(6, 182, 212, 0.3)'
              }}>
                <Globe size={20} color="#ffffff" />
              </div>
              <div>
                <h3 style={{ fontSize: '0.98rem', fontWeight: 700, margin: 0, color: '#f8fafc' }}>
                  Live Gateway Request Console (Test ANY Real API)
                </h3>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
                  Forward real HTTP requests through PulseGate to any live public or local API (SSRF protected & Token Bucket rate-limited).
                </p>
              </div>
            </div>

            {/* URL Presets */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600 }}>Presets:</span>
              <button
                type="button"
                onClick={() => setCustomUrl('https://httpbin.org/get')}
                className="btn btn-secondary"
                style={{ fontSize: '0.72rem', padding: '4px 10px' }}
              >
                httpbin.org/get
              </button>
              <button
                type="button"
                onClick={() => setCustomUrl('https://jsonplaceholder.typicode.com/posts/1')}
                className="btn btn-secondary"
                style={{ fontSize: '0.72rem', padding: '4px 10px' }}
              >
                jsonplaceholder (Post #1)
              </button>
              <button
                type="button"
                onClick={() => setCustomUrl('https://dummyjson.com/quotes/1')}
                className="btn btn-secondary"
                style={{ fontSize: '0.72rem', padding: '4px 10px' }}
              >
                dummyjson (Quotes)
              </button>
            </div>
          </div>

          {/* Request Input Form */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
            <select
              value={customMethod}
              onChange={(e) => setCustomMethod(e.target.value)}
              className="glass-panel"
              style={{
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                fontWeight: 700,
                color: '#38bdf8',
                background: 'rgba(15, 23, 42, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>

            <input
              type="text"
              value={customUrl}
              onChange={(e) => setCustomUrl(e.target.value)}
              placeholder="Enter target URL (e.g. https://httpbin.org/get or http://localhost:5000/api)"
              style={{
                flex: 1,
                minWidth: '280px',
                padding: '10px 16px',
                borderRadius: '8px',
                fontSize: '0.85rem',
                color: '#f8fafc',
                background: 'rgba(15, 23, 42, 0.85)',
                border: '1px solid rgba(255, 255, 255, 0.12)',
                outline: 'none',
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSendCustomRealRequest();
              }}
            />

            <button
              onClick={handleSendCustomRealRequest}
              disabled={customLoading || customSpiking}
              className="btn btn-primary"
              style={{ padding: '10px 18px', fontSize: '0.85rem', fontWeight: 600 }}
            >
              <Send size={15} />
              <span>{customLoading ? 'Forwarding...' : 'Send Single Req'}</span>
            </button>

            <button
              onClick={handleSendCustomBurstSpike}
              disabled={customLoading || customSpiking}
              className="btn btn-danger"
              style={{ padding: '10px 18px', fontSize: '0.85rem', fontWeight: 600 }}
              title="Send a concurrent burst of 35 requests to trigger rate limiting and ML anomaly detection on this URL"
            >
              <Flame size={15} color="var(--accent-rose)" />
              <span>{customSpiking ? 'Firing Spike...' : '⚡ Fire Burst Attack (Trigger Anomaly)'}</span>
            </button>
          </div>

          {/* Real-time Response Display */}
          {customResult && (
            <div
              style={{
                marginTop: '16px',
                padding: '14px 18px',
                borderRadius: '8px',
                background: 'rgba(2, 6, 23, 0.75)',
                border: `1px solid ${customResult.success ? 'rgba(16, 185, 129, 0.35)' : 'rgba(244, 63, 94, 0.35)'}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span
                    className="code-pill"
                    style={{
                      background: customResult.status_code < 400 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
                      color: customResult.status_code < 400 ? '#6ee7b7' : '#fda4af',
                      fontWeight: 700,
                      fontSize: '0.78rem',
                    }}
                  >
                    HTTP {customResult.status_code}
                  </span>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Downstream Latency: <strong style={{ color: '#38bdf8' }}>{customResult.latency_ms} ms</strong>
                  </span>
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                  Proxied through PulseGate AsyncClient
                </span>
              </div>

              <pre
                style={{
                  margin: 0,
                  padding: '12px',
                  borderRadius: '6px',
                  background: 'rgba(15, 23, 42, 0.95)',
                  fontSize: '0.75rem',
                  fontFamily: 'monospace',
                  color: '#e2e8f0',
                  maxHeight: '220px',
                  overflowY: 'auto',
                  border: '1px solid rgba(255, 255, 255, 0.05)',
                }}
              >
                {JSON.stringify(customResult.data || customResult.error, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* SECTION 20: DASHBOARD FILTERS */}
        <div className="glass-panel" style={{ padding: '14px 20px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Filter size={16} color="var(--text-muted)" />
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                Time Range:
              </span>
              <div style={{ display: 'flex', gap: '6px' }}>
                {[
                  { label: 'Last 5m', val: '5m' },
                  { label: 'Last 15m', val: '15m' },
                  { label: 'Last 1h', val: '1h' },
                  { label: 'Last 24h', val: '24h' },
                  { label: 'All', val: 'all' },
                ].map((t) => (
                  <button
                    key={t.val}
                    onClick={() => setTimeRange(t.val)}
                    className="btn"
                    style={{
                      padding: '4px 10px',
                      fontSize: '0.78rem',
                      background: timeRange === t.val ? 'var(--accent-indigo)' : 'rgba(255, 255, 255, 0.05)',
                      color: timeRange === t.val ? '#fff' : 'var(--text-muted)',
                      borderColor: timeRange === t.val ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                    }}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
              {/* Endpoint Filter */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Route:</span>
                <select
                  className="input-field"
                  style={{ padding: '6px 12px', fontSize: '0.8rem', width: 'auto' }}
                  value={selectedEndpoint}
                  onChange={(e) => setSelectedEndpoint(e.target.value)}
                >
                  <option value="">All Endpoints</option>
                  {endpoints.map((ep) => (
                    <option key={ep.endpoint} value={ep.endpoint}>
                      {ep.endpoint} ({ep.requests} reqs)
                    </option>
                  ))}
                </select>
              </div>

              {/* Anomaly-only toggle */}
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <input
                  type="checkbox"
                  checked={anomalyOnly}
                  onChange={(e) => setAnomalyOnly(e.target.checked)}
                  style={{ accentColor: 'var(--accent-rose)' }}
                />
                <span>Focus Anomalies Only</span>
              </label>
            </div>
          </div>
        </div>

        {/* CHARTS ROW */}
        {!anomalyOnly && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '20px', marginBottom: '24px' }}>
            <TrafficChart data={timeseries} />
            <LatencyChart data={timeseries} />
          </div>
        )}

        {/* TABLES ROW */}
        <div style={{ display: 'grid', gridTemplateColumns: anomalyOnly ? '1fr' : 'repeat(auto-fit, minmax(460px, 1fr))', gap: '20px' }}>
          <AnomalyTable anomalies={anomalies} />
          {!anomalyOnly && (
            <EndpointTable
              endpoints={endpoints}
              onSelectEndpoint={(ep) => setSelectedEndpoint(ep)}
              selectedEndpoint={selectedEndpoint}
            />
          )}
        </div>
      </main>

      {/* API Key Modal */}
      <ApiKeyModal
        isOpen={isKeysOpen}
        onClose={() => setIsKeysOpen(false)}
        keys={keys}
        onCreateKey={handleCreateKey}
        onDeactivateKey={handleDeactivateKey}
      />
    </div>
  );
};
