import React from 'react';
import { Layers, ArrowUpRight } from 'lucide-react';
import type { EndpointStat } from '../types';

interface EndpointTableProps {
  endpoints: EndpointStat[];
  onSelectEndpoint?: (endpoint: string) => void;
  selectedEndpoint?: string;
}

export const EndpointTable: React.FC<EndpointTableProps> = ({
  endpoints,
  onSelectEndpoint,
  selectedEndpoint,
}) => {
  return (
    <div className="glass-panel" style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(6, 182, 212, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(6, 182, 212, 0.3)',
          }}>
            <Layers size={18} color="var(--accent-cyan)" />
          </div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>
              Endpoint Statistics
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Traffic volume and latency distributed by target path
            </p>
          </div>
        </div>
        <span className="badge badge-cyan">{endpoints.length} Routes</span>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '10px 12px' }}>Endpoint Route</th>
              <th style={{ padding: '10px 12px' }}>Total Requests</th>
              <th style={{ padding: '10px 12px' }}>Avg Latency</th>
              <th style={{ padding: '10px 12px' }}>Error Rate</th>
              <th style={{ padding: '10px 12px', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {endpoints.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: '36px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  No endpoint requests logged yet.
                </td>
              </tr>
            ) : (
              endpoints.map((ep) => (
                <tr
                  key={ep.endpoint}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    backgroundColor: selectedEndpoint === ep.endpoint ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                    transition: 'background 0.2s',
                  }}
                >
                  <td style={{ padding: '12px 12px' }}>
                    <span className="code-pill" style={{ color: '#38bdf8' }}>{ep.endpoint}</span>
                  </td>
                  <td style={{ padding: '12px 12px', fontWeight: 700, color: '#f8fafc' }}>
                    {ep.requests}
                  </td>
                  <td style={{ padding: '12px 12px', color: ep.average_latency_ms > 300 ? '#fda4af' : '#cbd5e1' }}>
                    {ep.average_latency_ms} ms
                  </td>
                  <td style={{ padding: '12px 12px' }}>
                    <span className={`badge ${ep.error_rate > 5 ? 'badge-rose' : 'badge-emerald'}`}>
                      {ep.error_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 12px', textAlign: 'right' }}>
                    {onSelectEndpoint && (
                      <button
                        onClick={() => onSelectEndpoint(selectedEndpoint === ep.endpoint ? '' : ep.endpoint)}
                        className="btn btn-secondary"
                        style={{ fontSize: '0.75rem', padding: '4px 8px' }}
                      >
                        {selectedEndpoint === ep.endpoint ? 'Clear Filter' : 'Filter Route'}
                        <ArrowUpRight size={12} />
                      </button>
                    )}
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
