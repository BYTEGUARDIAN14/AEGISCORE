/**
 * AEGISCORE — RepoPage
 * Single repository view with stats, risk heatmap, and scan history.
 */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import StatCards from '../components/dashboard/StatCards';
import RiskHeatmap from '../components/risk/RiskHeatmap';
import Badge from '../components/ui/Badge';
import Card from '../components/ui/Card';
import EmptyState from '../components/ui/EmptyState';
import apiClient from '../api/client';
import { getRiskHeatmap } from '../api/risk';
import { listScans } from '../api/scans';

export function RepoPage() {
  const { repoId } = useParams();
  const [repo, setRepo] = useState(null);
  const [riskFiles, setRiskFiles] = useState([]);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [repoData, riskData, scansData] = await Promise.all([
          repoId ? apiClient.get(`/repos/${repoId}`) : Promise.resolve(null),
          repoId ? getRiskHeatmap(repoId, 0, 20).catch(() => ({ files: [] })) : Promise.resolve({ files: [] }),
          repoId ? listScans({ repo_id: repoId, limit: 10 }).catch(() => ({ scans: [] })) : Promise.resolve({ scans: [] }),
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
          fontFamily: 'var(--font-sans)',
          fontWeight: 600,
          fontSize: '16px',
          color: 'var(--text-primary)',
          marginBottom: '4px',
        }}>
          {repo?.name || 'Repository'}
        </h1>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          color: 'var(--text-tertiary)',
        }}>
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
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
        }}>
          <span style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 600,
            fontSize: '13px',
            color: 'var(--text-primary)',
          }}>
            Scan History
          </span>
        </div>

        {scans.length === 0 ? (
          <EmptyState
            icon="scans"
            heading="No scans yet"
            subtext="Trigger a scan to start analyzing this repository."
          />
        ) : (
          scans.map((scan) => (
            <div
              key={scan.id}
              style={{
                padding: '12px 20px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transition: 'background 100ms ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-hover)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
            >
              <Badge status={scan.status}>{scan.status}</Badge>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--text-tertiary)',
              }}>
                {scan.commit_sha?.slice(0, 8)}
              </span>
              <span style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
              }}>
                {scan.branch}
              </span>
              <span style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                color: 'var(--text-primary)',
                flex: 1,
              }}>
                {scan.total_findings} findings
              </span>
              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--text-tertiary)',
              }}>
                {new Date(scan.triggered_at).toLocaleDateString()}
              </span>
            </div>
          ))
        )}
      </Card>
    </div>
  );
}

export default RepoPage;
