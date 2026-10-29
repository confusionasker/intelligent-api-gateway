import React from 'react';
import { AlertTriangle, Clock } from 'lucide-react';
import type { Anomaly } from '../types';

interface AnomalyTableProps {
  anomalies: Anomaly[];
}

export const AnomalyTable: React.FC<AnomalyTableProps> = ({ anomalies }) => {
  return (
    <div className="glass-panel" style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(244, 63, 94, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(244, 63, 94, 0.3)',
          }}>
            <AlertTriangle size={18} color="var(--accent-rose)" />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
              Detected Traffic Anomalies
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Events classified as outliers by scikit-learn Isolation Forest
            </p>
          </div>
        </div>
        <span className="badge badge-rose">
          {anomalies.length} Incident{anomalies.length === 1 ? '' : 's'}
        </span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '10px 12px' }}>Timestamp</th>
              <th style={{ padding: '10px 12px' }}>Traffic Vol</th>
              <th style={{ padding: '10px 12px' }}>Avg Latency</th>
              <th style={{ padding: '10px 12px' }}>Error Rate</th>
              <th style={{ padding: '10px 12px' }}>ML Score</th>
              <th style={{ padding: '10px 12px' }}>Contributing Reason</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '36px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  🟢 No traffic anomalies recorded. Baseline traffic is operating within normal boundaries.
                </td>
              </tr>
            ) : (
              anomalies.map((item) => (
                <tr
                  key={item.id}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    transition: 'background 0.2s',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <td style={{ padding: '12px 12px', whiteSpace: 'nowrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Clock size={13} color="var(--text-dim)" />
                      <span className="code-pill">
                        {new Date(item.timestamp).toLocaleTimeString('en-IN', {
                          timeZone: 'Asia/Kolkata',
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                          hour12: true,
                        })}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 12px', fontWeight: 700, color: '#f8fafc' }}>
                    {item.request_count} <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>req/min</span>
                  </td>
                  <td style={{ padding: '12px 12px', color: item.average_latency_ms > 350 ? '#fda4af' : '#cbd5e1' }}>
                    {item.average_latency_ms} ms
                  </td>
                  <td style={{ padding: '12px 12px' }}>
                    <span className={`badge ${item.error_rate > 0.1 ? 'badge-rose' : 'badge-emerald'}`}>
                      {(item.error_rate * 100).toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 12px' }}>
                    <span className="code-pill" style={{ color: '#f43f5e' }}>
                      {item.anomaly_score.toFixed(3)}
                    </span>
                  </td>
                  <td style={{ padding: '12px 12px', color: '#e2e8f0', maxWidth: '300px' }}>
                    {item.reason}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
