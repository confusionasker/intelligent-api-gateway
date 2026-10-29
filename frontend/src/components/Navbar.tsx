import React from 'react';
import { Activity, Key, RefreshCw, LogOut, ShieldCheck, Zap } from 'lucide-react';
import type { User, LatestAnomalyStatus } from '../types';

interface NavbarProps {
  user: User | null;
  status: LatestAnomalyStatus | null;
  isPolling: boolean;
  onTogglePolling: () => void;
  onRefresh: () => void;
  onOpenKeys: () => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  user,
  status,
  isPolling,
  onTogglePolling,
  onRefresh,
  onOpenKeys,
  onLogout,
}) => {
  const statusLabel = status?.status_label || 'NORMAL';

  return (
    <header className="glass-panel" style={{ margin: '16px 24px', padding: '14px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        {/* Brand & Live Traffic Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(99, 102, 241, 0.4)'
            }}>
              <Zap size={22} color="#ffffff" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  PulseGate
                </span>
                <span className="code-pill" style={{ fontSize: '0.7rem' }}>v1.0 ML Gateway</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                AI-Driven Traffic Anomaly Detection & Token Bucket Gateway
              </p>
            </div>
          </div>

          {/* Traffic Status Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '9999px',
            background: statusLabel === 'ANOMALY' ? 'rgba(244, 63, 94, 0.15)' : statusLabel === 'WARNING' ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.12)',
            border: `1px solid ${statusLabel === 'ANOMALY' ? 'rgba(244, 63, 94, 0.4)' : statusLabel === 'WARNING' ? 'rgba(245, 158, 11, 0.4)' : 'rgba(16, 185, 129, 0.3)'}`,
          }}>
            <span className={`indicator-dot ${statusLabel === 'ANOMALY' ? 'indicator-anomaly' : statusLabel === 'WARNING' ? 'indicator-warning' : 'indicator-normal'}`} />
            <span style={{
              fontSize: '0.78rem',
              fontWeight: 700,
              letterSpacing: '0.04em',
              color: statusLabel === 'ANOMALY' ? '#fda4af' : statusLabel === 'WARNING' ? '#fcd34d' : '#6ee7b7'
            }}>
              {statusLabel === 'ANOMALY' ? '🔴 ANOMALY DETECTED' : statusLabel === 'WARNING' ? '🟠 ELEVATED TRAFFIC' : '🟢 NORMAL TRAFFIC'}
            </span>
          </div>
        </div>

        {/* Right Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Polling Toggle */}
          <button
            onClick={onTogglePolling}
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
            title={isPolling ? 'Pause 5-second polling' : 'Resume live polling'}
          >
            <Activity size={15} color={isPolling ? 'var(--accent-emerald)' : 'var(--text-muted)'} />
            <span>{isPolling ? 'Live (5s)' : 'Paused'}</span>
          </button>

          {/* Manual Refresh */}
          <button
            onClick={onRefresh}
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
            title="Refresh dashboard data now"
          >
            <RefreshCw size={15} />
            <span>Sync</span>
          </button>

          {/* API Key Modal Button */}
          <button
            onClick={onOpenKeys}
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            <Key size={15} color="var(--accent-cyan)" />
            <span>API Keys</span>
          </button>

          {/* User & Logout */}
          {user && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <ShieldCheck size={16} color="var(--accent-purple)" />
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#cbd5e1' }}>
                  {user.username}
                </span>
              </div>
              <button
                onClick={onLogout}
                className="btn btn-danger"
                style={{ padding: '6px 10px' }}
                title="Log out"
              >
                <LogOut size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
