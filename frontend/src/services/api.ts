import axios from 'axios';
import type {
  MetricsSummary,
  TimeSeriesPoint,
  EndpointStat,
  Anomaly,
  LatestAnomalyStatus,
  ApiKey,
  User,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Attach JWT access token to requests automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication APIs
export const authApi = {
  login: async (username: string, password: string): Promise<{ access_token: string; token_type: string }> => {
    const res = await apiClient.post('/api/auth/login', { username, password });
    return res.data;
  },
  register: async (username: string, password: string): Promise<User> => {
    const res = await apiClient.post('/api/auth/register', { username, password });
    return res.data;
  },
  getCurrentUser: async (): Promise<User> => {
    const res = await apiClient.get('/api/auth/me');
    return res.data;
  },
};

// API Key Management APIs
export const apiKeyApi = {
  listKeys: async (): Promise<ApiKey[]> => {
    const res = await apiClient.get('/api/keys');
    return res.data;
  },
  createKey: async (name: string = 'Primary Key', rate_limit: number = 20): Promise<ApiKey> => {
    const res = await apiClient.post('/api/keys', { name, rate_limit });
    return res.data;
  },
  deactivateKey: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/keys/${id}`);
  },
};

// Metrics Reporting APIs
export const metricsApi = {
  getSummary: async (timeRange: string = '1h', endpoint?: string): Promise<MetricsSummary> => {
    const res = await apiClient.get('/api/metrics/summary', {
      params: { time_range: timeRange, endpoint },
    });
    return res.data;
  },
  getTimeseries: async (timeRange: string = '1h', endpoint?: string): Promise<TimeSeriesPoint[]> => {
    const res = await apiClient.get('/api/metrics/timeseries', {
      params: { time_range: timeRange, endpoint, limit: 40 },
    });
    return res.data;
  },
  getEndpoints: async (): Promise<EndpointStat[]> => {
    const res = await apiClient.get('/api/metrics/endpoints');
    return res.data;
  },
};

// Anomaly Detection APIs
export const anomalyApi = {
  getRecentAnomalies: async (limit: number = 30): Promise<Anomaly[]> => {
    const res = await apiClient.get('/api/anomalies', { params: { limit } });
    return res.data;
  },
  getLatestStatus: async (): Promise<LatestAnomalyStatus> => {
    const res = await apiClient.get('/api/anomalies/latest');
    return res.data;
  },
  triggerEvaluation: async (windowSeconds: number = 60): Promise<any> => {
    const res = await apiClient.post('/api/anomalies/evaluate', null, {
      params: { window_seconds: windowSeconds },
    });
    return res.data;
  },
};

// Gateway Test Call API
export const gatewayApi = {
  forwardRequest: async (targetUrl: string, apiKey: string, method: string = 'GET'): Promise<any> => {
    const res = await apiClient.post(
      '/api/gateway/request',
      { target_url: targetUrl, method },
      { headers: { 'X-API-Key': apiKey } }
    );
    return res.data;
  },
};
