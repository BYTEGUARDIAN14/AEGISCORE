/**
 * AEGISCORE — EmptyState Component
 * Displayed when a list or panel has no data.
 * Uses inline SVG icons — never emoji.
 */

const icons = {
  findings: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 3L33 30H3L18 3Z" stroke="var(--border-focus)" strokeWidth="2" strokeLinejoin="round"/>
      <path d="M18 14V21" stroke="var(--border-focus)" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="18" cy="25" r="1.5" fill="var(--border-focus)"/>
    </svg>
  ),
  scans: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="18" cy="18" r="14" stroke="var(--border-focus)" strokeWidth="2"/>
      <path d="M18 10V18L24 22" stroke="var(--border-focus)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),
  repos: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="5" y="5" width="26" height="26" rx="3" stroke="var(--border-focus)" strokeWidth="2"/>
      <path d="M12 18H24M12 13H24M12 23H19" stroke="var(--border-focus)" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  risk: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="18" width="6" height="12" rx="1" stroke="var(--border-focus)" strokeWidth="2"/>
      <rect x="15" y="12" width="6" height="18" rx="1" stroke="var(--border-focus)" strokeWidth="2"/>
      <rect x="24" y="6" width="6" height="24" rx="1" stroke="var(--border-focus)" strokeWidth="2"/>
    </svg>
  ),
  fixes: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20.5 5.5L30.5 15.5L15.5 30.5H5.5V20.5L20.5 5.5Z" stroke="var(--border-focus)" strokeWidth="2" strokeLinejoin="round"/>
      <path d="M17 9L27 19" stroke="var(--border-focus)" strokeWidth="2"/>
    </svg>
  ),
  correlations: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="10" cy="10" r="4" stroke="var(--border-focus)" strokeWidth="2"/>
      <circle cx="26" cy="10" r="4" stroke="var(--border-focus)" strokeWidth="2"/>
      <circle cx="18" cy="26" r="4" stroke="var(--border-focus)" strokeWidth="2"/>
      <path d="M13 13L15 22M23 13L21 22" stroke="var(--border-focus)" strokeWidth="2"/>
    </svg>
  ),
  default: (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="18" cy="18" r="14" stroke="var(--border-focus)" strokeWidth="2"/>
      <path d="M14 18H22M18 14V22" stroke="var(--border-focus)" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
};

export function EmptyState({
  icon = 'default',
  heading = 'No data found',
  subtext = 'There are no items to display.',
  action,
}) {
  const svgIcon = icons[icon] || icons.default;

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '200px',
      padding: '40px 20px',
      textAlign: 'center',
    }}>
      <div style={{ marginBottom: '16px' }}>
        {svgIcon}
      </div>
      <h3 style={{
        fontFamily: 'var(--font-sans)',
        fontWeight: 500,
        fontSize: '14px',
        color: 'var(--text-secondary)',
        marginBottom: '6px',
      }}>
        {heading}
      </h3>
      <p style={{
        fontFamily: 'var(--font-sans)',
        fontWeight: 400,
        fontSize: '12px',
        color: 'var(--text-tertiary)',
        maxWidth: '280px',
      }}>
        {subtext}
      </p>
      {action && (
        <div style={{ marginTop: '16px' }}>
          {action}
        </div>
      )}
    </div>
  );
}

export default EmptyState;
