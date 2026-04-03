/**
 * AEGISCORE — RiskHeatmap Component
 * Displays files sorted by ML risk score with color-coded bars.
 */
import EmptyState from '../ui/EmptyState';

function getScoreColor(score) {
  if (score >= 0.8) return 'var(--red-text)';
  if (score >= 0.6) return 'var(--amber-text)';
  if (score >= 0.4) return 'var(--blue-text)';
  return 'var(--green-text)';
}

function getRiskLabel(score) {
  if (score >= 0.8) return 'CRITICAL RISK';
  if (score >= 0.6) return 'HIGH RISK';
  if (score >= 0.4) return 'MEDIUM';
  return 'MINIMAL';
}

export function RiskHeatmap({ files = [], loading = false }) {
  if (!loading && files.length === 0) {
    return (
      <div style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
      }}>
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid var(--border-subtle)',
        }}>
          <span style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 600,
            fontSize: '13px',
            color: 'var(--text-primary)',
          }}>
            Risk Heatmap
          </span>
        </div>
        <EmptyState
          icon="risk"
          heading="No risk data available"
          subtext="Risk scores will appear after scans are completed and the ML model is trained."
        />
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '8px',
      padding: '20px 24px',
    }}>
      <div style={{
        fontFamily: 'var(--font-sans)',
        fontWeight: 600,
        fontSize: '13px',
        color: 'var(--text-primary)',
        marginBottom: '16px',
      }}>
        Risk Heatmap
      </div>

      {files.map((file, i) => {
        const color = getScoreColor(file.score);
        const label = getRiskLabel(file.score);

        return (
          <div
            key={file.file_path || i}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '16px',
              padding: '10px 0',
              borderBottom: i < files.length - 1 ? '1px solid var(--border-subtle)' : 'none',
            }}
          >
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--text-secondary)',
              flex: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {file.file_path}
            </span>

            {/* Score Bar */}
            <div style={{
              width: '200px',
              height: '4px',
              backgroundColor: 'var(--bg-elevated)',
              borderRadius: '2px',
              overflow: 'hidden',
              flexShrink: 0,
            }}>
              <div style={{
                width: `${file.score * 100}%`,
                height: '100%',
                backgroundColor: color,
                borderRadius: '2px',
                transition: 'width 400ms ease',
              }} />
            </div>

            {/* Score Value */}
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontWeight: 500,
              fontSize: '12px',
              color,
              minWidth: '36px',
              textAlign: 'right',
            }}>
              {file.score.toFixed(2)}
            </span>

            {/* Risk Label */}
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color,
              minWidth: '90px',
              textAlign: 'right',
            }}>
              {label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default RiskHeatmap;
