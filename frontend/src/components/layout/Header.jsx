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

export function Header() {
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

      {/* System Status */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
      }}>
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
          All systems operational
        </span>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
          marginLeft: '8px',
        }}>
          {timestamp}
        </span>
      </div>
    </header>
  );
}

export default Header;
