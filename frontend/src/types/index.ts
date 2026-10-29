export interface MetricsSummary {
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  average_latency_ms: number;
  requests_per_second: number;
}

export interface TimeSeriesPoint {
  timestamp: string;
  requests: number;
  average_latency_ms: number;
  error_rate: number;
}

export interface EndpointStat {
  endpoint: string;
  requests: number;
  average_latency_ms: number;
  error_rate: number;
}

export interface Anomaly {
  id: number;
  timestamp: string;
  request_count: number;
  average_latency_ms: number;
  error_rate: number;
  anomaly_score: number;
  reason: string;
}

export interface LatestAnomalyStatus {
  is_anomaly: boolean;
  status_label: 'NORMAL' | 'WARNING' | 'ANOMALY';
  latest_anomaly: Anomaly | null;
  window_stats?: {
    window_seconds: number;
    request_count: number;
    requests_per_second: number;
    average_latency_ms: number;
    error_rate: number;
    unique_endpoints: number;
    status_5xx_count: number;
    anomaly_score: number;
    prediction: number;
    reason: string;
  };
}

export interface ApiKey {
  id: number;
  key: string;
  name: string;
  rate_limit: number;
  is_active: boolean;
  created_at: string;
}

export interface User {
  id: number;
  username: string;
  is_active: boolean;
  created_at: string;
}
