/**
 * AEGISCORE — DocsPage
 * Embedded API reference, CLI guide, and platform documentation.
 */
import { useState } from 'react';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';

const API_ENDPOINTS = [
  { group: 'Authentication', endpoints: [
    { method: 'POST', path: '/auth/register', desc: 'Register new user account', auth: false },
    { method: 'POST', path: '/auth/login', desc: 'Authenticate and get JWT tokens', auth: false },
    { method: 'POST', path: '/auth/refresh', desc: 'Exchange refresh token for new access token', auth: false },
    { method: 'GET', path: '/auth/me', desc: 'Get current user profile', auth: true },
  ]},
  { group: 'Organizations', endpoints: [
    { method: 'POST', path: '/orgs', desc: 'Create new organization (admin only)', auth: true },
    { method: 'GET', path: '/orgs/{org_id}', desc: 'Get organization details', auth: true },
    { method: 'GET', path: '/orgs/{org_id}/teams', desc: 'List teams in organization', auth: true },
    { method: 'POST', path: '/orgs/{org_id}/teams', desc: 'Create new team', auth: true },
    { method: 'POST', path: '/orgs/{org_id}/teams/{team_id}/members', desc: 'Add member to team', auth: true },
    { method: 'DELETE', path: '/orgs/{org_id}/teams/{team_id}/members/{user_id}', desc: 'Remove team member', auth: true },
  ]},
  { group: 'Repositories', endpoints: [
    { method: 'POST', path: '/repos', desc: 'Connect a repository to a team', auth: true },
    { method: 'GET', path: '/repos', desc: 'List repositories (filtered by team access)', auth: true },
    { method: 'GET', path: '/repos/{repo_id}', desc: 'Get repository detail with last scan', auth: true },
    { method: 'PUT', path: '/repos/{repo_id}', desc: 'Update repository settings', auth: true },
    { method: 'DELETE', path: '/repos/{repo_id}', desc: 'Disconnect (soft-delete) repository', auth: true },
  ]},
  { group: 'Scans', endpoints: [
    { method: 'POST', path: '/scans/trigger', desc: 'Trigger security scan (Semgrep/Bandit/Trivy)', auth: true },
    { method: 'GET', path: '/scans', desc: 'List scans with filters and pagination', auth: true },
    { method: 'GET', path: '/scans/{scan_id}', desc: 'Get full scan detail with task statuses', auth: true },
    { method: 'GET', path: '/scans/{scan_id}/status', desc: 'Lightweight status for polling', auth: true },
  ]},
  { group: 'Findings', endpoints: [
    { method: 'GET', path: '/findings', desc: 'List findings with severity/scanner/repo filters', auth: true },
    { method: 'GET', path: '/findings/{finding_id}', desc: 'Get finding detail with fix and correlations', auth: true },
  ]},
  { group: 'Risk', endpoints: [
    { method: 'GET', path: '/risk/heatmap', desc: 'Get file risk scores for a repository', auth: true },
    { method: 'GET', path: '/risk/history', desc: 'Get risk score history for a specific file', auth: true },
    { method: 'GET', path: '/risk/model/status', desc: 'Get ML model version and accuracy metrics', auth: true },
  ]},
  { group: 'Fixes', endpoints: [
    { method: 'GET', path: '/fixes', desc: 'List AI-generated fix suggestions', auth: true },
    { method: 'POST', path: '/fixes/{fix_id}/apply', desc: 'Mark a fix suggestion as applied', auth: true },
  ]},
  { group: 'Correlations', endpoints: [
    { method: 'GET', path: '/correlations', desc: 'List cross-repo vulnerability correlation groups', auth: true },
  ]},
  { group: 'System', endpoints: [
    { method: 'GET', path: '/metrics', desc: 'Prometheus metrics endpoint', auth: false },
    { method: 'GET', path: '/health', desc: 'Basic health check', auth: false },
    { method: 'GET', path: '/api/v1/health', desc: 'Detailed health with component status', auth: false },
  ]},
];

const CLI_COMMANDS = [
  { cmd: 'aegiscore login', desc: 'Authenticate with your AEGISCORE instance', args: '--email, --password, --api-url' },
  { cmd: 'aegiscore scan', desc: 'Trigger a security scan on a repository', args: '--repo, --branch, --commit, --scanners' },
  { cmd: 'aegiscore status', desc: 'Check the status of a running scan', args: '--scan-id' },
  { cmd: 'aegiscore findings', desc: 'List security findings with filters', args: '--repo, --severity, --scanner, --limit' },
  { cmd: 'aegiscore predict', desc: 'Run ML risk prediction on a repository', args: '--repo, --top-n' },
  { cmd: 'aegiscore fix', desc: 'Generate AI fix suggestions for a finding', args: '--finding-id' },
  { cmd: 'aegiscore correlate', desc: 'Run cross-repo correlation analysis', args: '--rule-id' },
  { cmd: 'aegiscore report', desc: 'Generate security scan report', args: '--scan-id, --format (json/csv/md)' },
  { cmd: 'aegiscore health', desc: 'Check API and component health status', args: '' },
];

const METHOD_COLORS = {
  GET: { bg: '#0D2818', color: '#4ADE80', border: '#16A34A' },
  POST: { bg: '#1A1A2E', color: '#818CF8', border: '#6366F1' },
  PUT: { bg: '#1C1708', color: '#FBBF24', border: '#D97706' },
  DELETE: { bg: '#1C0808', color: '#F87171', border: '#DC2626' },
};

export function DocsPage() {
  const [activeTab, setActiveTab] = useState('api');
  const [expandedGroup, setExpandedGroup] = useState(null);

  const tabs = [
    { id: 'api', label: 'API Reference' },
    { id: 'cli', label: 'CLI Commands' },
    { id: 'quickstart', label: 'Quick Start' },
  ];

  return (
    <div style={{ maxWidth: '900px' }}>
      {/* Tabs */}
      <div style={{
        display: 'flex', gap: '2px',
        marginBottom: '24px',
        backgroundColor: 'var(--bg-elevated)',
        borderRadius: '6px',
        padding: '3px',
        width: 'fit-content',
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              backgroundColor: activeTab === tab.id ? 'var(--bg-surface)' : 'transparent',
              border: activeTab === tab.id ? '1px solid var(--border-subtle)' : '1px solid transparent',
              color: activeTab === tab.id ? 'var(--text-primary)' : 'var(--text-tertiary)',
              borderRadius: '4px',
              padding: '6px 16px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '12px',
              cursor: 'pointer',
              transition: 'all 100ms ease',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* API Reference Tab */}
      {activeTab === 'api' && (
        <div>
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            marginBottom: '16px',
          }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
              Base URL: http://localhost:8000/api/v1
            </span>
            <a
              href="/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--accent)',
                textDecoration: 'none', padding: '4px 10px',
                border: '1px solid var(--accent-border)', borderRadius: '4px',
                backgroundColor: 'var(--accent-muted)',
              }}
            >
              Open Swagger UI
            </a>
          </div>

          {API_ENDPOINTS.map(group => (
            <div key={group.group} style={{ marginBottom: '8px' }}>
              <div
                onClick={() => setExpandedGroup(expandedGroup === group.group ? null : group.group)}
                style={{
                  padding: '12px 16px',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: expandedGroup === group.group ? '8px 8px 0 0' : '8px',
                  cursor: 'pointer',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  transition: 'background 100ms ease',
                }}
                onMouseEnter={e => { e.currentTarget.style.backgroundColor = 'var(--bg-hover)'; }}
                onMouseLeave={e => { e.currentTarget.style.backgroundColor = 'var(--bg-surface)'; }}
              >
                <span style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                  {group.group}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                  {group.endpoints.length} endpoint{group.endpoints.length !== 1 ? 's' : ''}
                </span>
              </div>

              {expandedGroup === group.group && (
                <div style={{
                  border: '1px solid var(--border-subtle)',
                  borderTop: 'none',
                  borderRadius: '0 0 8px 8px',
                  overflow: 'hidden',
                }}>
                  {group.endpoints.map((ep, i) => {
                    const mc = METHOD_COLORS[ep.method] || METHOD_COLORS.GET;
                    return (
                      <div key={i} style={{
                        padding: '10px 16px',
                        borderBottom: i < group.endpoints.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                        display: 'flex', alignItems: 'center', gap: '12px',
                        backgroundColor: 'var(--bg-surface)',
                      }}>
                        <span style={{
                          fontFamily: 'var(--font-mono)', fontWeight: 600, fontSize: '10px',
                          backgroundColor: mc.bg, color: mc.color, border: `1px solid ${mc.border}`,
                          padding: '2px 8px', borderRadius: '3px', minWidth: '52px', textAlign: 'center',
                        }}>
                          {ep.method}
                        </span>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)', minWidth: '280px' }}>
                          {ep.path}
                        </span>
                        <span style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--text-secondary)', flex: 1 }}>
                          {ep.desc}
                        </span>
                        {ep.auth && (
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ flexShrink: 0 }}>
                            <rect x="3" y="1" width="6" height="4" rx="2" stroke="var(--text-tertiary)" strokeWidth="1.2" fill="none"/>
                            <rect x="1.5" y="5" width="9" height="6" rx="1" stroke="var(--text-tertiary)" strokeWidth="1.2" fill="none"/>
                          </svg>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* CLI Commands Tab */}
      {activeTab === 'cli' && (
        <div>
          <div style={{ marginBottom: '16px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
            Install: pip install -e ./cli
          </div>
          <Card padding="0">
            {CLI_COMMANDS.map((cmd, i) => (
              <div key={i} style={{
                padding: '14px 20px',
                borderBottom: i < CLI_COMMANDS.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                display: 'flex', alignItems: 'flex-start', gap: '16px',
              }}>
                <div style={{ minWidth: '200px' }}>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--accent)', fontWeight: 600 }}>
                    {cmd.cmd}
                  </div>
                  {cmd.args && (
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-tertiary)', marginTop: '4px' }}>
                      {cmd.args}
                    </div>
                  )}
                </div>
                <div style={{ fontFamily: 'var(--font-sans)', fontSize: '13px', color: 'var(--text-secondary)' }}>
                  {cmd.desc}
                </div>
              </div>
            ))}
          </Card>
        </div>
      )}

      {/* Quick Start Tab */}
      {activeTab === 'quickstart' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {[
            { step: 1, title: 'Start the platform', code: 'docker compose up -d' },
            { step: 2, title: 'Register an admin account', code: 'curl -X POST http://localhost:8000/api/v1/auth/register \\\n  -H "Content-Type: application/json" \\\n  -d \'{"email":"admin@aegiscore.com","password":"password123","full_name":"Admin User"}\'' },
            { step: 3, title: 'Login to get tokens', code: 'curl -X POST http://localhost:8000/api/v1/auth/login \\\n  -H "Content-Type: application/json" \\\n  -d \'{"email":"admin@aegiscore.com","password":"password123"}\'' },
            { step: 4, title: 'Create an organization', code: 'curl -X POST http://localhost:8000/api/v1/orgs \\\n  -H "Authorization: Bearer $TOKEN" \\\n  -H "Content-Type: application/json" \\\n  -d \'{"name":"My Company","slug":"my-company","plan":"community"}\'' },
            { step: 5, title: 'Connect a repository', code: 'curl -X POST http://localhost:8000/api/v1/repos \\\n  -H "Authorization: Bearer $TOKEN" \\\n  -H "Content-Type: application/json" \\\n  -d \'{"team_id":"$TEAM_ID","name":"my-app","github_url":"https://github.com/org/repo","default_branch":"main"}\'' },
            { step: 6, title: 'Trigger a scan', code: 'curl -X POST http://localhost:8000/api/v1/scans/trigger \\\n  -H "Authorization: Bearer $TOKEN" \\\n  -H "Content-Type: application/json" \\\n  -d \'{"repo_id":"$REPO_ID","commit_sha":"abc123","branch":"main","scanners":["semgrep","bandit","trivy"]}\'' },
            { step: 7, title: 'Open the dashboard', code: 'open http://localhost  # Docker production\nopen http://localhost:5173  # Local development' },
          ].map(item => (
            <Card key={item.step}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <span style={{
                  width: '24px', height: '24px', borderRadius: '50%',
                  backgroundColor: 'var(--accent-muted)', color: 'var(--accent)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'var(--font-mono)', fontSize: '11px', fontWeight: 700,
                  border: '1px solid var(--accent-border)', flexShrink: 0,
                }}>
                  {item.step}
                </span>
                <span style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
                  {item.title}
                </span>
              </div>
              <pre style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                borderRadius: '6px',
                padding: '12px 16px',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
                overflowX: 'auto',
                margin: 0,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}>
                {item.code}
              </pre>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocsPage;
