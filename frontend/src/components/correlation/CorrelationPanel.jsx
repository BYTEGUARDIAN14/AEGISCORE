/**
 * AEGISCORE — CorrelationPanel Component
 * Displays cross-repo vulnerability correlation groups.
 */
import Badge from '../ui/Badge';
import EmptyState from '../ui/EmptyState';

export function CorrelationPanel({ correlations = [], loading = false }) {
  if (!loading && correlations.length === 0) {
    return (
      <EmptyState
        icon="correlations"
        heading="No cross-repo correlations"
        subtext="Correlations will appear when the same vulnerability is found across multiple repositories."
      />
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {correlations.map((group, i) => (
        <div
          key={i}
          style={{
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
            padding: '16px 20px',
            backgroundColor: 'var(--bg-surface)',
          }}
        >
          {/* Header */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            marginBottom: '12px',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--text-secondary)',
            }}>
              {group.rule_id}
            </span>
            <Badge severity={group.severity} />
          </div>

          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '13px',
            color: 'var(--text-primary)',
            marginBottom: '10px',
          }}>
            Found in {group.repos_affected} repositories
          </div>

          {/* Repo List */}
          {group.repos?.map((repo, j) => (
            <div
              key={j}
              style={{
                padding: '6px 0',
                borderTop: j > 0 ? '1px solid var(--border-subtle)' : 'none',
              }}
            >
              <div style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '12px',
                color: 'var(--text-primary)',
              }}>
                {repo.repo_name}
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-tertiary)',
                  marginLeft: '8px',
                }}>
                  {repo.team_name}
                </span>
              </div>
              {repo.files?.map((file, k) => (
                <div
                  key={k}
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--text-tertiary)',
                    paddingLeft: '12px',
                    marginTop: '2px',
                  }}
                >
                  {file.file_path}:{file.line_number}
                </div>
              ))}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

export default CorrelationPanel;
