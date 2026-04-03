/**
 * AEGISCORE — StatCards Component
 * Row of 4 stat cards showing key metrics.
 */
import Card from '../ui/Card';
import { SkeletonCard } from '../ui/Skeleton';

export function StatCards({ stats, loading = false }) {
  if (loading) {
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
    );
  }

  const cards = [
    {
      label: 'TOTAL FINDINGS',
      value: stats?.total_findings ?? 0,
      sub: `across ${stats?.repos_count ?? 0} repositories`,
      accent: 'var(--accent)',
      valueColor: null,
    },
    {
      label: 'CRITICAL',
      value: stats?.critical ?? 0,
      sub: 'require immediate action',
      accent: 'var(--red-text)',
      valueColor: stats?.critical > 0 ? 'var(--red-text)' : null,
    },
    {
      label: 'HIGH',
      value: stats?.high ?? 0,
      sub: 'should be reviewed soon',
      accent: 'var(--amber-text)',
      valueColor: stats?.high > 0 ? 'var(--amber-text)' : null,
    },
    {
      label: 'FILES AT RISK',
      value: stats?.files_at_risk ?? 0,
      sub: 'ML-predicted risk score > 0.6',
      accent: 'var(--accent)',
      valueColor: null,
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
      {cards.map((card, i) => (
        <Card key={i} accentColor={card.accent}>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '10px',
            color: 'var(--text-secondary)',
            letterSpacing: '0.10em',
            textTransform: 'uppercase',
            marginBottom: '8px',
          }}>
            {card.label}
          </div>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 600,
            fontSize: '34px',
            color: card.valueColor || 'var(--text-primary)',
            lineHeight: 1.1,
            marginBottom: '6px',
          }}>
            {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
          </div>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 400,
            fontSize: '11px',
            color: 'var(--text-tertiary)',
          }}>
            {card.sub}
          </div>
        </Card>
      ))}
    </div>
  );
}

export default StatCards;
