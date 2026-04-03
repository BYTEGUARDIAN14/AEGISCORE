/**
 * AEGISCORE — Sidebar Component
 * Fixed navigation sidebar with org selector and nav items.
 */
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useOrg } from '../../hooks/useOrg';

const NAV_ITEMS = [
  {
    section: 'PLATFORM',
    items: [
      { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
      { label: 'Repositories', path: '/repos', icon: 'repos' },
      { label: 'Findings', path: '/findings', icon: 'findings' },
      { label: 'Risk Map', path: '/risk', icon: 'risk' },
      { label: 'Fixes', path: '/fixes', icon: 'fixes' },
      { label: 'Correlations', path: '/correlations', icon: 'correlations' },
    ],
  },
  {
    section: 'SYSTEM',
    items: [
      { label: 'Settings', path: '/settings', icon: 'settings' },
      { label: 'Documentation', path: '/docs', icon: 'docs' },
    ],
  },
];

const ICONS = {
  dashboard: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/><rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/><rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/><rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.5"/></svg>
  ),
  repos: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 4.5C2 3.12 3.12 2 4.5 2H11.5C12.88 2 14 3.12 14 4.5V13L8 10L2 13V4.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
  ),
  findings: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1.5L14.5 13H1.5L8 1.5Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 6.5V9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><circle cx="8" cy="11" r="0.75" fill="currentColor"/></svg>
  ),
  risk: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="9" width="3" height="5.5" rx="0.5" stroke="currentColor" strokeWidth="1.5"/><rect x="6.5" y="5.5" width="3" height="9" rx="0.5" stroke="currentColor" strokeWidth="1.5"/><rect x="11.5" y="2" width="3" height="12.5" rx="0.5" stroke="currentColor" strokeWidth="1.5"/></svg>
  ),
  fixes: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M9 2L14 7L7 14H2V9L9 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>
  ),
  correlations: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="4" cy="4" r="2" stroke="currentColor" strokeWidth="1.5"/><circle cx="12" cy="4" r="2" stroke="currentColor" strokeWidth="1.5"/><circle cx="8" cy="12" r="2" stroke="currentColor" strokeWidth="1.5"/><path d="M5.5 5.5L7 10M10.5 5.5L9 10" stroke="currentColor" strokeWidth="1.5"/></svg>
  ),
  settings: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="2.5" stroke="currentColor" strokeWidth="1.5"/><path d="M8 1V3M8 13V15M1 8H3M13 8H15M3.05 3.05L4.46 4.46M11.54 11.54L12.95 12.95M12.95 3.05L11.54 4.46M4.46 11.54L3.05 12.95" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  ),
  docs: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 2H10L13 5V14H3V2Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M6 8H10M6 10.5H10M6 5.5H8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  ),
};

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { orgName } = useOrg();

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : '??';

  return (
    <aside style={{
      position: 'fixed',
      top: 0,
      left: 0,
      bottom: 0,
      width: 'var(--sidebar-width)',
      backgroundColor: 'var(--bg-surface)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 100,
      overflow: 'hidden',
    }}>
      {/* Logo */}
      <div style={{
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        borderBottom: '1px solid var(--border-subtle)',
        gap: '10px',
      }}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 1L18 5.5V14.5L10 19L2 14.5V5.5L10 1Z" stroke="var(--accent)" strokeWidth="1.5" strokeLinejoin="round"/>
          <path d="M10 5L14 7.5V12.5L10 15L6 12.5V7.5L10 5Z" stroke="var(--accent)" strokeWidth="1.5" strokeLinejoin="round"/>
          <circle cx="10" cy="10" r="1.5" fill="var(--accent)"/>
        </svg>
        <span style={{
          fontFamily: 'var(--font-sans)',
          fontWeight: 600,
          fontSize: '14px',
          color: 'var(--text-primary)',
          letterSpacing: '0.05em',
        }}>
          AEGISCORE
        </span>
      </div>

      {/* Org Selector */}
      <div style={{
        height: '48px',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        borderBottom: '1px solid var(--border-subtle)',
        cursor: 'pointer',
      }}>
        <span style={{
          fontFamily: 'var(--font-sans)',
          fontWeight: 400,
          fontSize: '13px',
          color: 'var(--text-secondary)',
          flex: 1,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {orgName}
        </span>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M3 5L6 8L9 5" stroke="var(--text-tertiary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, overflowY: 'auto', paddingBottom: '60px' }}>
        {NAV_ITEMS.map((section) => (
          <div key={section.section}>
            <div style={{
              padding: '20px 20px 6px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '9px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
            }}>
              {section.section}
            </div>
            {section.items.map((item) => {
              const isActive = location.pathname === item.path ||
                (item.path !== '/dashboard' && location.pathname.startsWith(item.path));

              return (
                <div
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  style={{
                    height: '36px',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '0 12px 0 16px',
                    gap: '10px',
                    cursor: 'pointer',
                    backgroundColor: isActive ? 'var(--bg-active)' : 'transparent',
                    borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                    transition: 'background 100ms ease',
                    color: isActive ? 'var(--text-primary)' : 'var(--text-tertiary)',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <span style={{ color: isActive ? 'var(--text-primary)' : 'var(--text-tertiary)', display: 'flex' }}>
                    {ICONS[item.icon]}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-sans)',
                    fontWeight: 500,
                    fontSize: '12px',
                    color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                  }}>
                    {item.label}
                  </span>
                </div>
              );
            })}
          </div>
        ))}
      </nav>

      {/* User Info */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '12px 16px',
        borderTop: '1px solid var(--border-subtle)',
        backgroundColor: 'var(--bg-surface)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        cursor: 'pointer',
      }}
        onClick={logout}
        title="Click to logout"
      >
        <div style={{
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          backgroundColor: 'var(--bg-elevated)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'var(--font-sans)',
          fontSize: '9px',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          flexShrink: 0,
        }}>
          {initials}
        </div>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {user?.email || 'user@aegis.io'}
        </span>
      </div>
    </aside>
  );
}

export default Sidebar;
