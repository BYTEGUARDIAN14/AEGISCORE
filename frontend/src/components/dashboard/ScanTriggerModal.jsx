/**
 * AEGISCORE — ScanTriggerModal
 * Modal to configure and trigger a new security scan.
 */
import { useState, useEffect } from 'react';
import Button from '../ui/Button';
import Badge from '../ui/Badge';
import apiClient from '../../api/client';
import { triggerScan } from '../../api/scans';

export function ScanTriggerModal({ isOpen, onClose, onTriggered, initialRepoId }) {
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(initialRepoId || '');
  const [branch, setBranch] = useState('main');
  const [commitSha, setCommitSha] = useState('');
  const [scanners, setScanners] = useState({
    semgrep: true,
    bandit: true,
    trivy: true,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (isOpen) {
      // Pre-select initialRepoId if provided, else fall back to first repo
      if (initialRepoId) setSelectedRepo(initialRepoId);
      apiClient.get('/repos').then(data => {
        setRepos(data || []);
        if (data && data.length > 0 && !initialRepoId && !selectedRepo) {
          setSelectedRepo(data[0].id);
        }
      }).catch(() => {});
      // Reset state
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, initialRepoId]);

  if (!isOpen) return null;

  const selectedScanners = Object.entries(scanners)
    .filter(([, v]) => v)
    .map(([k]) => k);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedRepo) { setError('Select a repository'); return; }
    if (selectedScanners.length === 0) { setError('Select at least one scanner'); return; }

    setSubmitting(true);
    setError(null);
    try {
      // Backend requires a valid 40-char hex SHA — generate one if left blank
      const effectiveSha = commitSha.trim() || Array.from(
        { length: 40 },
        (_, i) => i < 32 ? '0' : Math.floor(Math.random() * 16).toString(16)
      ).join('');
      const result = await triggerScan(
        selectedRepo,
        effectiveSha,
        branch,
        selectedScanners,
      );
      setSuccess(`Scan queued with ${selectedScanners.length} scanner(s)`);
      onTriggered?.(result);
      setTimeout(() => {
        onClose();
        setSuccess(null);
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to trigger scan');
    } finally {
      setSubmitting(false);
    }
  };

  const inputStyle = {
    width: '100%',
    backgroundColor: 'var(--bg-elevated)',
    border: '1px solid var(--border-default)',
    borderRadius: '4px',
    padding: '9px 12px',
    fontFamily: 'var(--font-sans)',
    fontSize: '13px',
    color: 'var(--text-primary)',
    outline: 'none',
    boxSizing: 'border-box',
  };

  const labelStyle = {
    display: 'block',
    fontFamily: 'var(--font-sans)',
    fontWeight: 500,
    fontSize: '10px',
    color: 'var(--text-tertiary)',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    marginBottom: '6px',
  };

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          zIndex: 299,
          backdropFilter: 'blur(2px)',
        }}
      />

      {/* Modal */}
      <div style={{
        position: 'fixed',
        top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '480px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-default)',
        borderRadius: '12px',
        zIndex: 300,
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px 16px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <div style={{
              fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '15px',
              color: 'var(--text-primary)', marginBottom: '2px',
            }}>
              New Security Scan
            </div>
            <div style={{
              fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--text-tertiary)',
            }}>
              Configure and trigger a scan across selected analyzers
            </div>
          </div>
          <button onClick={onClose} style={{
            background: 'none', border: 'none', cursor: 'pointer', padding: '4px', color: 'var(--text-tertiary)',
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ padding: '20px 24px' }}>
          {/* Repository */}
          <div style={{ marginBottom: '16px' }}>
            <div style={labelStyle}>REPOSITORY</div>
            <select
              value={selectedRepo}
              onChange={e => setSelectedRepo(e.target.value)}
              style={{ ...inputStyle, cursor: 'pointer' }}
            >
              <option value="">Select a repository</option>
              {repos.map(repo => (
                <option key={repo.id} value={repo.id}>{repo.name}</option>
              ))}
            </select>
          </div>

          {/* Branch + Commit */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <div>
              <div style={labelStyle}>BRANCH</div>
              <input
                style={inputStyle}
                value={branch}
                onChange={e => setBranch(e.target.value)}
                placeholder="main"
              />
            </div>
            <div>
              <div style={labelStyle}>COMMIT SHA (optional)</div>
              <input
                style={inputStyle}
                value={commitSha}
                onChange={e => setCommitSha(e.target.value)}
                placeholder="HEAD"
              />
            </div>
          </div>

          {/* Scanners */}
          <div style={{ marginBottom: '20px' }}>
            <div style={labelStyle}>SCANNERS</div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {[
                { id: 'semgrep', label: 'Semgrep', desc: 'SAST rules' },
                { id: 'bandit', label: 'Bandit', desc: 'Python security' },
                { id: 'trivy', label: 'Trivy', desc: 'Dependency scan' },
              ].map(scanner => (
                <div
                  key={scanner.id}
                  onClick={() => setScanners(prev => ({ ...prev, [scanner.id]: !prev[scanner.id] }))}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: scanners[scanner.id] ? 'var(--accent-muted)' : 'var(--bg-elevated)',
                    border: `1px solid ${scanners[scanner.id] ? 'var(--accent-border)' : 'var(--border-subtle)'}`,
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 120ms ease',
                    textAlign: 'center',
                  }}
                >
                  <div style={{
                    fontFamily: 'var(--font-sans)', fontWeight: 600, fontSize: '12px',
                    color: scanners[scanner.id] ? 'var(--accent)' : 'var(--text-secondary)',
                    marginBottom: '2px',
                  }}>
                    {scanner.label}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)', fontSize: '10px',
                    color: 'var(--text-tertiary)',
                  }}>
                    {scanner.desc}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error / Success */}
          {error && (
            <div style={{
              fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--red-text)',
              marginBottom: '12px', padding: '8px 12px',
              backgroundColor: '#1C0808', borderRadius: '4px',
              border: '1px solid #5C1C1C',
            }}>
              {error}
            </div>
          )}
          {success && (
            <div style={{
              fontFamily: 'var(--font-sans)', fontSize: '12px', color: 'var(--green-text)',
              marginBottom: '12px', padding: '8px 12px',
              backgroundColor: '#0A1C0E', borderRadius: '4px',
              border: '1px solid #1C5C2E',
            }}>
              {success}
            </div>
          )}

          {/* Actions */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <Button variant="ghost" onClick={onClose} type="button">Cancel</Button>
            <Button
              variant="primary"
              type="submit"
              loading={submitting}
              disabled={submitting || !selectedRepo || selectedScanners.length === 0}
            >
              Trigger Scan ({selectedScanners.length} scanner{selectedScanners.length !== 1 ? 's' : ''})
            </Button>
          </div>
        </form>
      </div>
    </>
  );
}

export default ScanTriggerModal;
