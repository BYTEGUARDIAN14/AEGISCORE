/**
 * AEGISCORE — Button Component
 * Primary, secondary, and ghost button variants.
 */

const variants = {
  primary: {
    background: 'var(--accent)',
    color: '#ffffff',
    border: 'none',
    hoverBg: 'var(--accent-hover)',
  },
  secondary: {
    background: 'var(--bg-elevated)',
    color: 'var(--text-secondary)',
    border: '1px solid var(--border-default)',
    hoverBg: 'var(--bg-hover)',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--text-secondary)',
    border: 'none',
    hoverBg: 'var(--bg-hover)',
  },
  danger: {
    background: 'var(--red-badge-bg)',
    color: 'var(--red-text)',
    border: '1px solid var(--red-border)',
    hoverBg: 'var(--red-fill)',
  },
};

export function Button({
  children,
  variant = 'primary',
  size = 'default',
  fullWidth = false,
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  style = {},
  id,
}) {
  const v = variants[variant] || variants.primary;

  const sizeStyles = {
    small: { padding: '5px 10px', fontSize: '11px' },
    default: { padding: '7px 16px', fontSize: '12px' },
    large: { padding: '11px 20px', fontSize: '13px' },
  };

  const s = sizeStyles[size] || sizeStyles.default;

  const buttonStyle = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    fontFamily: 'var(--font-sans)',
    fontWeight: 500,
    borderRadius: '4px',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
    transition: 'background 100ms ease, border-color 100ms ease',
    width: fullWidth ? '100%' : 'auto',
    background: v.background,
    color: v.color,
    border: v.border,
    ...s,
    ...style,
  };

  const handleMouseEnter = (e) => {
    if (!disabled && !loading) {
      e.currentTarget.style.background = v.hoverBg;
    }
  };

  const handleMouseLeave = (e) => {
    if (!disabled && !loading) {
      e.currentTarget.style.background = v.background;
    }
  };

  return (
    <button
      id={id}
      type={type}
      style={buttonStyle}
      onClick={disabled || loading ? undefined : onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      disabled={disabled || loading}
    >
      {loading && (
        <span style={{
          display: 'inline-block',
          width: '12px',
          height: '12px',
          border: '2px solid currentColor',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 600ms linear infinite',
        }} />
      )}
      {children}
    </button>
  );
}

export default Button;
