/**
 * AEGISCORE — DashboardPage
 * Overview page with stats, severity trend, active scans, and recent findings.
 */
import { useState, useEffect, useCallback } from 'react';
import StatCards from '../components/dashboard/StatCards';
import SeverityBreakdown from '../components/dashboard/SeverityBreakdown';
import ActiveScans from '../components/dashboard/ActiveScans';
import FindingsTable from '../components/findings/FindingsTable';
import FindingDetail from '../components/findings/FindingDetail';
import { listFindings } from '../api/findings';
import { listScans } from '../api/scans';

export function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [recentFindings, setRecentFindings] = useState([]);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [findingsRes, scansRes] = await Promise.all([
        listFindings({ limit: 20 }).catch(() => ({ findings: [], total: 0 })),
        listScans({ limit: 10 }).catch(() => ({ scans: [], total: 0 })),
      ]);

      setRecentFindings(findingsRes.findings || []);

      // Compute stats from findings
      const findings = findingsRes.findings || [];
      const critical = findings.filter(f => f.severity === 'CRITICAL').length;
      const high = findings.filter(f => f.severity === 'HIGH').length;

      setStats({
        total_findings: findingsRes.total || findings.length,
        critical,
        high,
        files_at_risk: new Set(findings.map(f => f.file_path)).size,
        repos_count: new Set((scansRes.scans || []).map(s => s.repo_id)).size || 1,
      });
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setStats({
        total_findings: 0,
        critical: 0,
        high: 0,
        files_at_risk: 0,
        repos_count: 0,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div>
      {/* Stats Row */}
      <div style={{ marginBottom: '24px' }}>
        <StatCards stats={stats} loading={loading} />
      </div>

      {/* Charts + Active Scans Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '3fr 2fr',
        gap: '16px',
        marginBottom: '24px',
      }}>
        <SeverityBreakdown />
        <ActiveScans />
      </div>

      {/* Recent Findings */}
      <FindingsTable
        findings={recentFindings}
        loading={loading}
        onRowClick={(finding) => setSelectedFinding(finding)}
      />

      {/* Finding Detail Panel */}
      {selectedFinding && (
        <>
          <div
            onClick={() => setSelectedFinding(null)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.4)',
              zIndex: 199,
            }}
          />
          <FindingDetail
            finding={selectedFinding}
            onClose={() => setSelectedFinding(null)}
          />
        </>
      )}
    </div>
  );
}

export default DashboardPage;
