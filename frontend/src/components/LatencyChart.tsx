import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { TimeSeriesPoint } from '../types';

interface LatencyChartProps {
  data: TimeSeriesPoint[];
}

export const LatencyChart: React.FC<LatencyChartProps> = ({ data }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            Latency & Error Rate Dynamics
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Response duration (ms) and failed request ratio (%)
          </p>
        </div>
        <span className="badge badge-indigo">Performance</span>
      </div>

      <div style={{ width: '100%', height: 260 }}>
        {data.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No performance metrics collected yet.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(val) => val.split(' ')[1] || val}
                stroke="#64748b"
                tick={{ fontSize: 11 }}
              />
              <YAxis yAxisId="left" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  color: '#f8fafc',
                  fontSize: '0.8rem',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="average_latency_ms"
                name="Avg Latency (ms)"
                stroke="#818cf8"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="error_rate"
                name="Error Rate (%)"
                stroke="#f43f5e"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
