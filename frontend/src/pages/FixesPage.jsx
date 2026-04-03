/**
 * AEGISCORE — FixesPage
 * AI fix suggestions list with confidence filter and review panel.
 */
import { useState, useEffect, useCallback } from 'react';
import Badge from '../components/ui/Badge';
import EmptyState from '../components/ui/EmptyState';
import FixReview from '../components/fixes/FixReview';
import { listFixes } from '../api/fixes';

export function FixesPage() {
  const [fixes, setFixes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFix, setSelectedFix] = useState(null);
  const [filter, setFilter] = useState('all');

  const fetchFixes = useCallback(async () => {
    try {
      const params = {};
      if (filter !== 'all') params.confidence = filter;
      const res = await listFixes(params);
      setFixes(res.fixes || []);
    } catch (err) {
      console.error('Failed to fetch fixes:', err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchFixes();
  }, [fetchFixes]);

  const filters = ['all', 'high', 'medium', 'low'];

  return (
    <div>
      {/* Filters */}
      <div style={{
        display: 'flex',
        gap: '6px',
        marginBottom: '16px',
      }}>
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              backgroundColor: filter === f ? 'var(--accent-muted)' : 'var(--bg-elevated)',
              border: `1px solid ${filter === f ? 'var(--accent-border)' : 'var(--border-subtle)'}`,
              color: filter === f ? 'var(--accent)' : 'var(--text-secondary)',
              borderRadius: '4px',
              padding: '5px 12px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '11px',
              cursor: 'pointer',
              textTransform: 'capitalize',
              transition: 'background 100ms ease',
            }}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Fix List or Selected Fix */}
      {selectedFix ? (
        <div>
          <button
            onClick={() => setSelectedFix(null)}
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-default)',
              color: 'var(--text-secondary)',
              borderRadius: '4px',
              padding: '5px 12px',
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '11px',
              cursor: 'pointer',
              marginBottom: '16px',
            }}
          >
            Back to list
          </button>
          <FixReview
            fix={selectedFix}
            finding={selectedFix._finding}
            onApplied={() => fetchFixes()}
          />
        </div>
      ) : fixes.length === 0 && !loading ? (
        <EmptyState
          icon="fixes"
          heading="No fix suggestions"
          subtext="AI fixes are generated for critical and high severity findings after scans complete."
        />
      ) : (
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '8px',
          overflow: 'hidden',
        }}>
          {fixes.map((fix, i) => (
            <div
              key={fix.id}
              onClick={() => setSelectedFix(fix)}
              style={{
                padding: '14px 20px',
                borderBottom: i < fixes.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transition: 'background 100ms ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--bg-hover)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
            >
              <Badge status={fix.confidence}>{fix.confidence}</Badge>

              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                flex: 1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {fix.finding_id?.slice(0, 8)}...
              </span>

              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--text-tertiary)',
              }}>
                {fix.model_used}
              </span>

              {fix.applied ? (
                <span style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: '11px',
                  color: 'var(--green-text)',
                }}>
                  Applied
                </span>
              ) : (
                <span style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: '11px',
                  color: 'var(--text-tertiary)',
                }}>
                  Pending
                </span>
              )}

              <span style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                color: 'var(--text-tertiary)',
              }}>
                {new Date(fix.generated_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FixesPage;
