/**
 * AEGISCORE — Badge Component
 * Severity and status badges with semantic coloring.
 */

const SEVERITY_STYLES = {
  CRITICAL: {
    background: 'var(--red-badge-bg)',
    border: 'var(--red-badge-border)',
    color: 'var(--red-badge-text)',
  },
  HIGH: {
    background: 'var(--amber-badge-bg)',
    border: 'var(--amber-badge-border)',
    color: 'var(--amber-badge-text)',
  },
  MEDIUM: {
    background: 'var(--blue-badge-bg)',
    border: 'var(--blue-badge-border)',
    color: 'var(--blue-badge-text)',
  },
  LOW: {
    background: 'var(--green-badge-bg)',
    border: 'var(--green-badge-border)',
    color: 'var(--green-badge-text)',
  },
};

const STATUS_STYLES = {
  completed: {
    background: 'var(--green-badge-bg)',
    border: 'var(--green-badge-border)',
    color: 'var(--green-badge-text)',
  },
  running: {
    background: 'var(--blue-badge-bg)',
    border: 'var(--blue-badge-border)',
    color: 'var(--blue-badge-text)',
  },
  queued: {
    background: 'var(--bg-elevated)',
    border: 'var(--border-default)',
    color: 'var(--text-tertiary)',
  },
  failed: {
    background: 'var(--red-badge-bg)',
    border: 'var(--red-badge-border)',
    color: 'var(--red-badge-text)',
  },
  high: {
    background: 'var(--green-badge-bg)',
    border: 'var(--green-badge-border)',
    color: 'var(--green-badge-text)',
  },
  medium: {
    background: 'var(--amber-badge-bg)',
    border: 'var(--amber-badge-border)',
    color: 'var(--amber-badge-text)',
  },
  low: {
    background: 'var(--red-badge-bg)',
    border: 'var(--red-badge-border)',
    color: 'var(--red-badge-text)',
  },
};

const baseStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  fontFamily: 'var(--font-sans)',
  fontWeight: 600,
  fontSize: '10px',
  letterSpacing: '0.06em',
  textTransform: 'uppercase',
  borderRadius: '4px',
  padding: '3px 8px',
  lineHeight: 1.4,
  whiteSpace: 'nowrap',
};

export function Badge({ children, variant = 'default', severity, status, style = {} }) {
  let colorStyle = {};

  if (severity && SEVERITY_STYLES[severity.toUpperCase()]) {
    colorStyle = SEVERITY_STYLES[severity.toUpperCase()];
  } else if (status && STATUS_STYLES[status.toLowerCase()]) {
    colorStyle = STATUS_STYLES[status.toLowerCase()];
  } else {
    colorStyle = {
      background: 'var(--bg-elevated)',
      border: 'var(--border-default)',
      color: 'var(--text-secondary)',
    };
  }

  return (
    <span
      style={{
        ...baseStyle,
        backgroundColor: colorStyle.background,
        border: `1px solid ${colorStyle.border}`,
        color: colorStyle.color,
        ...style,
      }}
    >
      {children || severity || status}
    </span>
  );
}

export default Badge;
