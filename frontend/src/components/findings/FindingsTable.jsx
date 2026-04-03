/**
 * AEGISCORE — FindingsTable Component
 * Full-featured findings table with severity filters and sorting.
 */
import { useState, useMemo } from 'react';
import Badge from '../ui/Badge';
import EmptyState from '../ui/EmptyState';

const SEVERITY_ORDER = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };

export function FindingsTable({ findings = [], loading = false, onRowClick }) {
  const [filter, setFilter] = useState('ALL');
  const [sortField, setSortField] = useState('severity');
  const [sortDir, setSortDir] = useState('asc');

  const filtered = useMemo(() => {
    let result = [...findings];
    if (filter !== 'ALL') {
      result = result.filter((f) => f.severity === filter);
    }
    result.sort((a, b) => {
      let cmp = 0;
      if (sortField === 'severity') {
        cmp = (SEVERITY_ORDER[a.severity] ?? 4) - (SEVERITY_ORDER[b.severity] ?? 4);
      } else if (sortField === 'file_path') {
        cmp = a.file_path.localeCompare(b.file_path);
      } else if (sortField === 'scanner') {
        cmp = a.scanner.localeCompare(b.scanner);
      } else if (sortField === 'rule_id') {
        cmp = a.rule_id.localeCompare(b.rule_id);
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return result;
  }, [findings, filter, sortField, sortDir]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  };

  const SortArrow = ({ field }) => {
    if (sortField !== field) return null;
    return (
      <span style={{ color: 'var(--accent)', marginLeft: '4px' }}>
        {sortDir === 'asc' ? '↑' : '↓'}
      </span>
    );
  };

  const filters = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: '8px',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px 20px',
        borderBottom: '1px solid var(--border-subtle)',
      }}>
        <span style={{
          fontFamily: 'var(--font-sans)',
          fontWeight: 600,
          fontSize: '13px',
          color: 'var(--text-primary)',
        }}>
          Security Findings
        </span>

        <div style={{ display: 'flex', gap: '6px' }}>
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
                transition: 'background 100ms ease, border-color 100ms ease',
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <EmptyState
          icon="findings"
          heading="No findings match"
          subtext="Try adjusting your filters or trigger a new scan."
        />
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{
                backgroundColor: 'var(--bg-base)',
                borderBottom: '1px solid var(--border-default)',
              }}>
                {[
                  { key: 'severity', label: 'SEVERITY', width: '80px' },
                  { key: 'file_path', label: 'FILE', width: '220px' },
                  { key: 'scanner', label: 'SCANNER', width: '90px' },
                  { key: 'rule_id', label: 'RULE', width: '160px' },
                  { key: 'message', label: 'MESSAGE', width: 'auto' },
                  { key: 'cwe', label: 'CWE', width: '80px' },
                  { key: 'fix', label: 'FIX', width: '60px' },
                ].map((col) => (
                  <th
                    key={col.key}
                    onClick={() => col.key !== 'message' && col.key !== 'fix' && handleSort(col.key)}
                    style={{
                      padding: '10px 16px',
                      fontFamily: 'var(--font-sans)',
                      fontWeight: 500,
                      fontSize: '10px',
                      color: 'var(--text-tertiary)',
                      letterSpacing: '0.08em',
                      textTransform: 'uppercase',
                      textAlign: 'left',
                      cursor: col.key !== 'message' && col.key !== 'fix' ? 'pointer' : 'default',
                      width: col.width,
                      whiteSpace: 'nowrap',
                      userSelect: 'none',
                    }}
                  >
                    {col.label}
                    {col.key !== 'message' && col.key !== 'fix' && <SortArrow field={col.key} />}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((finding) => (
                <tr
                  key={finding.id}
                  onClick={() => onRowClick?.(finding)}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    cursor: onRowClick ? 'pointer' : 'default',
                    transition: 'background 100ms ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--bg-hover)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }}
                >
                  <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                    <Badge severity={finding.severity} />
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '12px',
                      color: 'var(--text-secondary)',
                    }}>
                      {finding.file_path}
                    </span>
                    <span style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '12px',
                      color: 'var(--text-tertiary)',
                    }}>
                      :{finding.line_number}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{
                      backgroundColor: 'var(--bg-elevated)',
                      border: '1px solid var(--border-default)',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontFamily: 'var(--font-sans)',
                      fontSize: '11px',
                      color: 'var(--text-secondary)',
                    }}>
                      {finding.scanner}
                    </span>
                  </td>
                  <td style={{
                    padding: '12px 16px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--text-tertiary)',
                    maxWidth: '160px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {finding.rule_id?.slice(0, 35)}
                  </td>
                  <td style={{
                    padding: '12px 16px',
                    fontFamily: 'var(--font-sans)',
                    fontSize: '13px',
                    color: 'var(--text-primary)',
                    maxWidth: '300px',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {finding.message?.slice(0, 65)}
                  </td>
                  <td style={{
                    padding: '12px 16px',
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--text-tertiary)',
                  }}>
                    {finding.cwe || '—'}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    {finding.has_fix ? (
                      <span style={{
                        fontFamily: 'var(--font-sans)',
                        fontSize: '12px',
                        color: 'var(--accent)',
                        cursor: 'pointer',
                      }}>
                        View fix
                      </span>
                    ) : (
                      <span style={{
                        fontFamily: 'var(--font-sans)',
                        fontSize: '12px',
                        color: 'var(--text-tertiary)',
                      }}>
                        —
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default FindingsTable;
