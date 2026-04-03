/**
 * AEGISCORE — ActiveScans Component
 * Live panel showing currently running and queued scans.
 */
import { useState, useEffect, useCallback } from 'react';
import Badge from '../ui/Badge';
import EmptyState from '../ui/EmptyState';
import { listScans } from '../../api/scans';
import { usePolling } from '../../hooks/usePolling';

export function ActiveScans() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchScans = useCallback(async () => {
    try {
      const [runningRes, queuedRes] = await Promise.all([
        listScans({ scan_status: 'running', limit: 10 }),
        listScans({ scan_status: 'queued', limit: 10 }),
      ]);
      const combined = [
        ...(runningRes?.scans || []),
        ...(queuedRes?.scans || []),
      ];
      setScans(combined);
    } catch (err) {
      console.error('Failed to fetch active scans:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(fetchScans, 10000, true);

  const getProgress = (scan) => {
    if (scan.status === 'completed') return 100;
    if (scan.status === 'queued') return 0;
    if (scan.status === 'running') return 45 + Math.random() * 30;
    return 0;
  };

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
          Active Scans
        </span>
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
        }}>
          {scans.length} active
        </span>
      </div>

      {/* Scan List */}
      {scans.length === 0 && !loading ? (
        <EmptyState
          icon="scans"
          heading="No active scans"
          subtext="All scanners are idle. Trigger a new scan to begin."
        />
      ) : (
        scans.map((scan) => {
          const progress = getProgress(scan);
          return (
            <div
              key={scan.id}
              style={{
                padding: '12px 20px',
                borderBottom: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontFamily: 'var(--font-sans)',
                  fontWeight: 500,
                  fontSize: '13px',
                  color: 'var(--text-primary)',
                  marginBottom: '2px',
                }}>
                  Scan
                </div>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-tertiary)',
                }}>
                  {scan.branch} • {scan.commit_sha?.slice(0, 8)}
                </div>
              </div>

              <Badge status={scan.status}>{scan.status}</Badge>

              {/* Progress Bar */}
              <div style={{
                width: '180px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                <div style={{
                  flex: 1,
                  height: '3px',
                  backgroundColor: 'var(--bg-elevated)',
                  borderRadius: '2px',
                  overflow: 'hidden',
                }}>
                  <div style={{
                    width: `${progress}%`,
                    height: '100%',
                    backgroundColor: scan.status === 'completed' ? 'var(--green-text)' : 'var(--accent)',
                    borderRadius: '2px',
                    transition: 'width 400ms ease',
                  }} />
                </div>
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-tertiary)',
                  minWidth: '36px',
                  textAlign: 'right',
                }}>
                  {Math.round(progress)}%
                </span>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}

export default ActiveScans;
