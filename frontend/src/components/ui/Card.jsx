/**
 * AEGISCORE — Card Component
 * Surface-level container with optional accent border.
 */

export function Card({
  children,
  accentColor,
  padding = '20px 24px',
  style = {},
  onClick,
  id,
}) {
  const cardStyle = {
    backgroundColor: 'var(--bg-surface)',
    border: '1px solid var(--border-subtle)',
    borderRadius: '8px',
    padding,
    position: 'relative',
    overflow: 'hidden',
    cursor: onClick ? 'pointer' : 'default',
    transition: onClick ? 'background 100ms ease' : 'none',
    ...style,
  };

  const accentStyle = accentColor ? {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: accentColor,
  } : null;

  const handleMouseEnter = (e) => {
    if (onClick) {
      e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
    }
  };

  const handleMouseLeave = (e) => {
    if (onClick) {
      e.currentTarget.style.backgroundColor = 'var(--bg-surface)';
    }
  };

  return (
    <div
      id={id}
      style={cardStyle}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {accentStyle && <div style={accentStyle} />}
      {children}
    </div>
  );
}

export default Card;
