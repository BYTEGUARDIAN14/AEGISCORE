/**
 * AEGISCORE — RepoPage
 * Repository list (when no repoId) or single repository detail view.
 */
import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import StatCards from '../components/dashboard/StatCards';
import RiskHeatmap from '../components/risk/RiskHeatmap';
import Badge from '../components/ui/Badge';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import EmptyState from '../components/ui/EmptyState';
import apiClient from '../api/client';
import { getRiskHeatmap } from '../api/risk';
import { listScans } from '../api/scans';

/* ─── Connect Repository Modal ─────────────────────────────────── */
function ConnectRepoModal({ isOpen, onClose, onCreated }) {
  const [teams, setTeams] = useState([]);
  const [teamId, setTeamId] = useState('');
  const [name, setName] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      setError(null);
      // Try to load teams from stored org
      const org = localStorage.getItem('aegiscore_org');
      if (org) {
        const parsed = JSON.parse(org);
        if (parsed?.id) {
          apiClient.get(`/orgs/${parsed.id}/teams`).then(data => {
            setTeams(data || []);
            if (data?.length > 0 && !teamId) setTeamId(data[0].id);
          }).catch(() => {});
        }
      }
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const inputStyle = {
    width: '100%', backgroundColor: 'var(--bg-elevated)',
    border: '1px solid var(--border-default)', borderRadius: '4px',
    padding: '9px 12px', fontFamily: 'var(--font-sans)', fontSize: '13px',
    color: 'var(--text-primary)', outline: 'none', boxSizing: 'border-box',
  };
  const labelStyle = {
    display: 'block', fontFamily: 'var(--font-sans)', fontWeight: 500,
    fontSize: '10px', color: 'var(--text-tertiary)', letterSpacing: '0.08em',
    textTransform: 'uppercase', marginBottom: '6px',
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!teamId) { setError('Select a team'); return; }
    setSubmitting(true); setError(null);
    try {
      const repo = await apiClient.post('/repos', {
        team_id: teamId, name, github_url: githubUrl, default_branch: branch,
      });
      onCreated?.(repo);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to connect repository');
    } finally { setSubmitting(false); }
  };

  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 299, backdropFilter: 'blur(2px)' }} />
      <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '460px', backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-default)', borderRadius: '12px', zIndex: 300, boxShadow: '0 20px 60px rgba(0,0,0,0.4)' }}>
        <div style={{ padding: '20px 24px 16px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '15px', color: 'var(--text-primary)' }}>Connect Repository</div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-tertiary)' }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
          </button>
        </div>
        <form onSubmit={handleSubmit} style={{ padding: '20px 24px' }}>
          <div style={{ marginBottom: '14px' }}>
            <div style={labelStyle}>TEAM</div>
            <select style={{ ...inputStyle, cursor: 'pointer' }} value={teamId} onChange={e => setTeamId(e.target.value)}>
              <option value="">Select team</option>
              {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <div style={{ marginBottom: '14px' }}>
            <div style={labelStyle}>REPOSITORY NAME</div>
            <input style={inputStyle} value={name} onChange={e => setName(e.target.value)} placeholder="my-application" required />
          </div>
          <div style={{ marginBottom: '14px' }}>
            <div style={labelStyle}>GITHUB URL</div>
            <input style={inputStyle} value={githubUrl} onChange={e => setGithubUrl(e.target.value)} placeholder="https://github.com/org/repo" required />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <div style={labelStyle}>DEFAULT BRANCH</div>
            <input style={inputStyle} value={branch} onChange={e => setBranch(e.target.value)} placeholder="main" />
          </div>
          {error && <div style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--red-text)', marginBottom: '12px', padding: '8px 12px', backgroundColor: '#1C0808', borderRadius: '4px', border: '1px solid #5C1C1C' }}>{error}</div>}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <Button variant="ghost" onClick={onClose} type="button">Cancel</Button>
            <Button variant="primary" type="submit" loading={submitting}>Connect</Button>
          </div>
        </form>
      </div>
    </>
  );
}

/* ─── Repo Card ──────────────────────────────────────────────── */
function RepoCard({ repo, onClick }) {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
        padding: '20px',
        cursor: 'pointer',
        transition: 'all 120ms ease',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--accent-border)';
        e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-subtle)';
        e.currentTarget.style.backgroundColor = 'var(--bg-surface)';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 4.5C2 3.12 3.12 2 4.5 2H11.5C12.88 2 14 3.12 14 4.5V13L8 10L2 13V4.5Z" stroke="var(--accent)" strokeWidth="1.5" strokeLinejoin="round"/>
        </svg>
        <span style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '14px', color: 'var(--text-primary)', flex: 1 }}>
          {repo.name}
        </span>
        <Badge status={repo.is_active ? 'completed' : 'failed'}>
          {repo.is_active ? 'Active' : 'Inactive'}
        </Badge>
      </div>

      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)', marginBottom: '12px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {repo.github_url}
      </div>

      <div style={{ display: 'flex', gap: '16px' }}>
        <div>
          <div style={{ fontFamily: 'var(--font-sans)', fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '2px' }}>BRANCH</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>{repo.default_branch}</div>
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-sans)', fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '2px' }}>LAST SCAN</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
            {repo.last_scan_at ? new Date(repo.last_scan_at).toLocaleDateString() : 'Never'}
          </div>
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-sans)', fontSize: '10px', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '2px' }}>CONNECTED</div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-secondary)' }}>
            {new Date(repo.connected_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─── Repo List View ─────────────────────────────────────────── */
function RepoListView() {
  const navigate = useNavigate();
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showConnect, setShowConnect] = useState(false);

  const fetchRepos = useCallback(async () => {
    try {
      const data = await apiClient.get('/repos');
      setRepos(data || []);
    } catch (err) {
      console.error('Failed to fetch repos:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchRepos(); }, [fetchRepos]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
          {repos.length} repositor{repos.length !== 1 ? 'ies' : 'y'} connected
        </span>
        <Button variant="primary" onClick={() => setShowConnect(true)}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 2V10M2 6H10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
            Connect Repository
          </span>
        </Button>
      </div>

      {repos.length === 0 && !loading ? (
        <EmptyState
          icon="repos"
          heading="No repositories connected"
          subtext="Connect your first repository to start running security scans."
        />
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '12px' }}>
          {repos.map(repo => (
            <RepoCard
              key={repo.id}
              repo={repo}
              onClick={() => navigate(`/repos/${repo.id}`)}
            />
          ))}
        </div>
      )}

      <ConnectRepoModal
        isOpen={showConnect}
        onClose={() => setShowConnect(false)}
        onCreated={() => fetchRepos()}
      />
    </div>
  );
}

/* ─── Repo Detail View ───────────────────────────────────────── */
function RepoDetailView({ repoId }) {
  const [repo, setRepo] = useState(null);
  const [riskFiles, setRiskFiles] = useState([]);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [repoData, riskData, scansData] = await Promise.all([
          apiClient.get(`/repos/${repoId}`),
          getRiskHeatmap(repoId, 0, 20).catch(() => ({ files: [] })),
          listScans({ repo_id: repoId, limit: 10 }).catch(() => ({ scans: [] })),
        ]);
        setRepo(repoData);
        setRiskFiles(riskData.files || []);
        setScans(scansData.scans || []);
      } catch (err) {
        console.error('Failed to fetch repo data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [repoId]);

  const repoStats = repo?.last_scan ? {
    total_findings: repo.last_scan.total_findings,
    critical: repo.last_scan.critical_count,
    high: repo.last_scan.high_count,
    files_at_risk: riskFiles.filter(f => f.score >= 0.6).length,
    repos_count: 1,
  } : { total_findings: 0, critical: 0, high: 0, files_at_risk: 0, repos_count: 1 };

  return (
    <div>
      {/* Repo Title */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{
          fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '16px',
          color: 'var(--text-primary)', marginBottom: '4px',
        }}>
          {repo?.name || 'Repository'}
        </h1>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-tertiary)' }}>
          {repo?.default_branch || 'main'} • {repo?.github_url || ''}
        </span>
      </div>

      {/* Stats */}
      <div style={{ marginBottom: '24px' }}>
        <StatCards stats={repoStats} loading={loading} />
      </div>

      {/* Risk Heatmap */}
      <div style={{ marginBottom: '24px' }}>
        <RiskHeatmap files={riskFiles} loading={loading} />
      </div>

      {/* Scan History */}
      <Card padding="0">
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '13px', color: 'var(--text-primary)' }}>
            Scan History
          </span>
        </div>
        {scans.length === 0 ? (
          <EmptyState icon="scans" heading="No scans yet" subtext="Trigger a scan to start analyzing this repository." />
        ) : (
          scans.map((scan) => (
            <div key={scan.id} style={{
              padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)',
              display: 'flex', alignItems: 'center', gap: '12px', transition: 'background 100ms ease',
            }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-hover)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
            >
              <Badge status={scan.status}>{scan.status}</Badge>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                {scan.commit_sha?.slice(0, 8)}
              </span>
              <span style={{ fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--text-secondary)' }}>
                {scan.branch}
              </span>
              <span style={{ fontFamily: 'var(--font-sans)', fontSize: '13px', color: 'var(--text-primary)', flex: 1 }}>
                {scan.total_findings} findings
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-tertiary)' }}>
                {new Date(scan.triggered_at).toLocaleDateString()}
              </span>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}

/* ─── Page Entry Point ───────────────────────────────────────── */
export function RepoPage() {
  const { repoId } = useParams();

  if (!repoId) {
    return <RepoListView />;
  }

  return <RepoDetailView repoId={repoId} />;
}

export default RepoPage;
