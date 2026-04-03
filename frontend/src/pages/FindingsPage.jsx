/**
 * AEGISCORE — FindingsPage
 * Full-page findings table with filter options and detail panel.
 */
import { useState, useEffect, useCallback } from 'react';
import FindingsTable from '../components/findings/FindingsTable';
import FindingDetail from '../components/findings/FindingDetail';
import { listFindings, getFinding } from '../api/findings';

export function FindingsPage() {
  const [findings, setFindings] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [detailData, setDetailData] = useState(null);

  const fetchFindings = useCallback(async () => {
    try {
      const res = await listFindings({ limit: 100 });
      setFindings(res.findings || []);
      setTotal(res.total || 0);
    } catch (err) {
      console.error('Failed to fetch findings:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFindings();
  }, [fetchFindings]);

  const handleRowClick = async (finding) => {
    setSelectedFinding(finding);
    try {
      const detail = await getFinding(finding.id);
      setDetailData(detail);
    } catch (err) {
      setDetailData(finding);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
        }}>
          {total} total findings
        </span>
      </div>

      <FindingsTable
        findings={findings}
        loading={loading}
        onRowClick={handleRowClick}
      />

      {selectedFinding && (
        <>
          <div
            onClick={() => { setSelectedFinding(null); setDetailData(null); }}
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
            finding={detailData || selectedFinding}
            onClose={() => { setSelectedFinding(null); setDetailData(null); }}
          />
        </>
      )}
    </div>
  );
}

export default FindingsPage;
