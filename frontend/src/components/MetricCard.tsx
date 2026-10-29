import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  accentColor: string; // e.g., 'cyan', 'indigo', 'emerald', 'rose', 'amber'
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  accentColor,
}) => {
  const getGradient = () => {
    switch (accentColor) {
      case 'emerald':
        return 'linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(16, 185, 129, 0.05) 100%)';
      case 'rose':
        return 'linear-gradient(135deg, rgba(244, 63, 94, 0.2) 0%, rgba(244, 63, 94, 0.05) 100%)';
      case 'amber':
        return 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)';
      case 'cyan':
        return 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(6, 182, 212, 0.05) 100%)';
      default:
        return 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%)';
    }
  };

  const getBorderColor = () => {
    switch (accentColor) {
      case 'emerald': return 'rgba(16, 185, 129, 0.3)';
      case 'rose': return 'rgba(244, 63, 94, 0.35)';
      case 'amber': return 'rgba(245, 158, 11, 0.3)';
      case 'cyan': return 'rgba(6, 182, 212, 0.3)';
      default: return 'rgba(99, 102, 241, 0.3)';
    }
  };

  return (
    <div
      className="glass-panel"
      style={{
        padding: '20px 24px',
        position: 'relative',
        overflow: 'hidden',
        border: `1px solid ${getBorderColor()}`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {title}
          </span>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, marginTop: '4px', letterSpacing: '-0.02em', color: '#ffffff' }}>
            {value}
          </div>
          {subtitle && (
            <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '4px' }}>
              {subtitle}
            </p>
          )}
        </div>
        <div
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            background: getGradient(),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: `1px solid ${getBorderColor()}`,
          }}
        >
          {icon}
        </div>
      </div>
    </div>
  );
};
