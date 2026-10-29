import React, { useState } from 'react';
import { Zap, ShieldCheck, Activity, BrainCircuit, ArrowRight, Lock, User as UserIcon } from 'lucide-react';
import { authApi } from '../services/api';

interface LoginProps {
  onLoginSuccess: (token: string) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await authApi.register(username, password);
        // Automatically login after successful registration
        const loginRes = await authApi.login(username, password);
        localStorage.setItem('token', loginRes.access_token);
        onLoginSuccess(loginRes.access_token);
      } else {
        const res = await authApi.login(username, password);
        localStorage.setItem('token', res.access_token);
        onLoginSuccess(res.access_token);
      }
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || err.response?.data?.detail || 'Authentication failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = () => {
    setUsername('admin');
    setPassword('admin123');
    setIsRegister(false);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
    }}>
      <div style={{ width: '100%', maxWidth: '440px' }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '14px',
            boxShadow: '0 0 24px rgba(99, 102, 241, 0.45)',
          }}>
            <Zap size={28} color="#ffffff" />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
            PulseGate
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '4px' }}>
            Intelligent API Gateway & AI Traffic Anomaly Detection
          </p>
        </div>

        {/* Auth Card */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-subtle)', marginBottom: '24px' }}>
            <button
              onClick={() => { setIsRegister(false); setError(null); }}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: !isRegister ? '2px solid var(--accent-indigo)' : 'none',
                color: !isRegister ? '#fff' : 'var(--text-dim)',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
              }}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsRegister(true); setError(null); }}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: isRegister ? '2px solid var(--accent-indigo)' : 'none',
                color: isRegister ? '#fff' : 'var(--text-dim)',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
              }}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div style={{
              padding: '10px 14px',
              borderRadius: '8px',
              background: 'rgba(244, 63, 94, 0.15)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              color: '#fda4af',
              fontSize: '0.82rem',
              marginBottom: '18px',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  className="input-field"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  required
                />
                <UserIcon size={16} color="var(--text-dim)" style={{ position: 'absolute', right: '12px', top: '12px' }} />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="password"
                  className="input-field"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
                <Lock size={16} color="var(--text-dim)" style={{ position: 'absolute', right: '12px', top: '12px' }} />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ padding: '12px', marginTop: '8px' }} disabled={loading}>
              <span>{loading ? 'Authenticating...' : isRegister ? 'Register Account' : 'Sign In to Dashboard'}</span>
              <ArrowRight size={16} />
            </button>
          </form>

          {/* Quick Demo Pre-fill */}
          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)', textAlign: 'center' }}>
            <button
              onClick={handleQuickDemo}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--accent-cyan)',
                fontSize: '0.8rem',
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Fill Demo Credentials (admin / admin123)
            </button>
          </div>
        </div>

        {/* Feature Highlights for Interviewers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginTop: '20px' }}>
          <div className="glass-panel" style={{ padding: '12px', textAlign: 'center' }}>
            <Activity size={18} color="var(--accent-emerald)" style={{ margin: '0 auto 6px' }} />
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f8fafc' }}>Token Bucket</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Redis O(1) Limits</div>
          </div>
          <div className="glass-panel" style={{ padding: '12px', textAlign: 'center' }}>
            <BrainCircuit size={18} color="var(--accent-indigo)" style={{ margin: '0 auto 6px' }} />
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f8fafc' }}>Isolation Forest</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>Unsupervised ML</div>
          </div>
          <div className="glass-panel" style={{ padding: '12px', textAlign: 'center' }}>
            <ShieldCheck size={18} color="var(--accent-cyan)" style={{ margin: '0 auto 6px' }} />
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f8fafc' }}>API Security</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)' }}>JWT + API Keys</div>
          </div>
        </div>
      </div>
    </div>
  );
};
