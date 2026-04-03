/**
 * AEGISCORE — FixReview Component
 * AI fix review panel with diff display and apply action.
 */
import { useState } from 'react';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import { applyFix } from '../../api/fixes';

export function FixReview({ fix, finding, onApplied }) {
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(fix?.applied || false);
  const [error, setError] = useState(null);

  if (!fix) return null;

  const handleApply = async () => {
    setApplying(true);
    setError(null);
    try {
      await applyFix(fix.id);
      setApplied(true);
      onApplied?.(fix.id);
    } catch (err) {
      setError(err.message || 'Failed to apply fix');
    } finally {
      setApplying(false);
    }
  };

  const renderDiff = (diffText) => {
    if (!diffText) return null;
    const lines = diffText.split('\n');

    return (
      <pre style={{
        backgroundColor: 'var(--bg-elevated)',
        border: '1px solid var(--border-default)',
        borderRadius: '6px',
        padding: '12px',
        fontFamily: 'var(--font-mono)',
        fontSize: '12px',
        lineHeight: 1.6,
        overflowX: 'auto',
        margin: 0,
      }}>
        {lines.map((line, i) => {
          let className = '';
          let bg = 'transparent';
          let color = 'var(--text-tertiary)';

          if (line.startsWith('+') && !line.startsWith('+++')) {
            bg = '#0A1C0E';
            color = 'var(--green-text)';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            bg = '#1C0A0A';
            color = 'var(--red-text)';
          } else if (line.startsWith('@@')) {
            color = 'var(--blue-text)';
          } else if (line.startsWith('---') || line.startsWith('+++')) {
            color = 'var(--text-secondary)';
          }

          return (
            <div key={i} style={{ background: bg, color, padding: '0 4px' }}>
              {line}
            </div>
          );
        })}
      </pre>
    );
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '8px',
      overflow: 'hidden',
    }}>
      {/* Finding Summary */}
      {finding && (
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          flexWrap: 'wrap',
        }}>
          <Badge severity={finding.severity} />
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: 'var(--text-secondary)',
          }}>
            {finding.file_path}:{finding.line_number}
          </span>
          <span style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
            color: 'var(--text-primary)',
            flex: 1,
          }}>
            {finding.message?.slice(0, 80)}
          </span>
        </div>
      )}

      {/* Fix Content */}
      <div style={{ padding: '20px' }}>
        {/* Confidence */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '16px',
        }}>
          <span style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '10px',
            color: 'var(--text-tertiary)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
          }}>
            CONFIDENCE
          </span>
          <Badge status={fix.confidence}>
            {fix.confidence}
          </Badge>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--text-tertiary)',
            marginLeft: 'auto',
          }}>
            {fix.model_used}
          </span>
        </div>

        {/* Diff */}
        {renderDiff(fix.unified_diff)}

        {/* Explanation */}
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border-subtle)',
        }}>
          <p style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: 1.6,
            margin: 0,
          }}>
            {fix.explanation}
          </p>
        </div>

        {/* Apply Action */}
        <div style={{ marginTop: '16px', display: 'flex', gap: '8px', alignItems: 'center' }}>
          {applied ? (
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              color: 'var(--green-text)',
            }}>
              Fix applied
              {fix.applied_at && ` at ${new Date(fix.applied_at).toLocaleString()}`}
            </span>
          ) : (
            <Button
              variant="primary"
              onClick={handleApply}
              loading={applying}
              disabled={applying}
            >
              Apply Fix
            </Button>
          )}
          {error && (
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              color: 'var(--red-text)',
            }}>
              {error}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default FixReview;
