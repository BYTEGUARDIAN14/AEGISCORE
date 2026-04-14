/**
 * AEGISCORE — Header Component
 * Top header bar with breadcrumb and system status.
 */
import { useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

const PAGE_TITLES = {
  '/dashboard': 'Overview',
  '/repos': 'Repositories',
  '/findings': 'Findings',
  '/risk': 'Risk Map',
  '/fixes': 'AI Fixes',
  '/correlations': 'Cross-Repo Correlations',
  '/settings': 'Settings',
  '/docs': 'Documentation',
};

export function Header({ onNewScan }) {
  const location = useLocation();
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(interval);
  }, []);

  const pageTitle = PAGE_TITLES[location.pathname] || 'AEGISCORE';
  const timestamp = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  return (
    <header style={{
      height: 'var(--header-height)',
      backgroundColor: 'var(--bg-base)',
      borderBottom: '1px solid var(--border-subtle)',
      padding: '0 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
    }}>
      {/* Breadcrumb */}
      <span style={{
        fontFamily: 'var(--font-sans)',
        fontWeight: 500,
        fontSize: '13px',
        color: 'var(--text-secondary)',
      }}>
        {pageTitle}
      </span>

      {/* Actions + Status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        {onNewScan && (
          <button
            onClick={onNewScan}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'var(--accent-muted)',
              border: '1px solid var(--accent-border)',
              color: 'var(--accent)',
              borderRadius: '5px',
              padding: '5px 12px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 600,
              fontSize: '11px',
              cursor: 'pointer',
              transition: 'all 120ms ease',
            }}
            onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'var(--accent)'; e.currentTarget.style.color = '#fff'; }}
            onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'var(--accent-muted)'; e.currentTarget.style.color = 'var(--accent)'; }}
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 2V10M2 6H10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            New Scan
          </button>
        )}

        <div style={{ width: '1px', height: '16px', backgroundColor: 'var(--border-subtle)' }} />

        <span style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          backgroundColor: 'var(--status-online)',
          display: 'inline-block',
          animation: 'pulse-dot 1.2s ease-in-out infinite',
        }} />
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
        }}>
          {timestamp}
        </span>
      </div>
    </header>
  );
}

export default Header;
