import React, { useState } from 'react';
import { X, Copy, Check, Plus, Trash2, KeyRound } from 'lucide-react';
import type { ApiKey } from '../types';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  keys: ApiKey[];
  onCreateKey: (name: string, rateLimit: number) => Promise<void>;
  onDeactivateKey: (id: number) => Promise<void>;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  isOpen,
  onClose,
  keys,
  onCreateKey,
  onDeactivateKey,
}) => {
  const [name, setName] = useState('Service Key');
  const [rateLimit, setRateLimit] = useState(20);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleCopy = (keyText: string) => {
    navigator.clipboard.writeText(keyText);
    setCopiedKey(keyText);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await onCreateKey(name, rateLimit);
      setName('Secondary Key');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: '16px',
    }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '640px', padding: '24px', position: 'relative' }}>
        <button
          onClick={onClose}
          style={{ position: 'absolute', top: '18px', right: '18px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
        >
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <KeyRound size={20} color="#fff" />
          </div>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
              PulseGate API Keys
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Manage keys and Token Bucket limits (default 20 req/min)
            </p>
          </div>
        </div>

        {/* Generate Key Form */}
        <form onSubmit={handleCreate} style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
          <input
            type="text"
            className="input-field"
            style={{ flex: 2, minWidth: '160px' }}
            placeholder="Key Label (e.g. Mobile App)"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            type="number"
            className="input-field"
            style={{ flex: 1, minWidth: '100px' }}
            placeholder="Limit (RPM)"
            value={rateLimit}
            onChange={(e) => setRateLimit(Number(e.target.value))}
            min={1}
            max={1000}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <Plus size={16} />
            <span>Generate Key</span>
          </button>
        </form>

        {/* Existing Keys List */}
        <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
          {keys.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '24px' }}>
              No API keys found. Generate one to authenticate gateway requests.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {keys.map((k) => (
                <div
                  key={k.id}
                  style={{
                    padding: '12px 14px',
                    borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div style={{ overflow: 'hidden' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                        {k.name}
                      </span>
                      <span className="badge badge-cyan">{k.rate_limit} req/min</span>
                      {!k.is_active && <span className="badge badge-rose">Revoked</span>}
                    </div>
                    <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="code-pill" style={{ fontSize: '0.75rem' }}>{k.key}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <button
                      onClick={() => handleCopy(k.key)}
                      className="btn btn-secondary"
                      style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                      title="Copy Key to Clipboard"
                    >
                      {copiedKey === k.key ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
                      <span>{copiedKey === k.key ? 'Copied' : 'Copy'}</span>
                    </button>
                    {k.is_active && (
                      <button
                        onClick={() => onDeactivateKey(k.id)}
                        className="btn btn-danger"
                        style={{ padding: '6px 8px' }}
                        title="Deactivate Key"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
