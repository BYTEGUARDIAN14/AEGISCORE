/**
 * AEGISCORE — CorrelationsPage
 * Cross-repo vulnerability correlations view.
 */
import { useState, useEffect } from 'react';
import CorrelationPanel from '../components/correlation/CorrelationPanel';
import { listCorrelations } from '../api/correlations';

export function CorrelationsPage() {
  const [correlations, setCorrelations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetch() {
      try {
        const res = await listCorrelations({ limit: 50 });
        setCorrelations(res.correlations || []);
      } catch (err) {
        console.error('Failed to fetch correlations:', err);
      } finally {
        setLoading(false);
      }
    }
    fetch();
  }, []);

  return (
    <div>
      <div style={{
        marginBottom: '16px',
        fontFamily: 'var(--font-mono)',
        fontSize: '11px',
        color: 'var(--text-tertiary)',
      }}>
        {correlations.length} correlation group{correlations.length !== 1 ? 's' : ''} detected
      </div>

      <CorrelationPanel correlations={correlations} loading={loading} />
    </div>
  );
}

export default CorrelationsPage;
