import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import type { TimeSeriesPoint } from '../types';

interface TrafficChartProps {
  data: TimeSeriesPoint[];
}

export const TrafficChart: React.FC<TrafficChartProps> = ({ data }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
            Traffic Volume Over Time
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Requests per 1-minute window evaluated by Gateway
          </p>
        </div>
        <span className="badge badge-cyan">Requests / min</span>
      </div>

      <div style={{ width: '100%', height: 260 }}>
        {data.length === 0 ? (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No traffic recorded in this time range yet. Send demo traffic to populate.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.06)" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(val) => val.split(' ')[1] || val}
                stroke="#64748b"
                tick={{ fontSize: 11 }}
              />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
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
              <Area
                type="monotone"
                dataKey="requests"
                name="Requests"
                stroke="#06b6d4"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#trafficGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
