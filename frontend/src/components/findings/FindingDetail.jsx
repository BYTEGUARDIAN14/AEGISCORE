import { useState, useEffect } from 'react';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import apiClient from '../../api/client';

export function FindingDetail({ finding, onClose }) {
  const [fixData, setFixData] = useState(finding?.fix || null);
  const [generating, setGenerating] = useState(false);
  const [applying, setApplying] = useState(false);
  const [applied, setApplied] = useState(finding?.fix?.applied || false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setFixData(finding?.fix || null);
    setApplied(finding?.fix?.applied || false);
    setError(null);
  }, [finding]);

  if (!finding) return null;

  const handleGenerateFix = async () => {
    setGenerating(true);
    setError(null);
    try {
      const res = await apiClient.post('/fixes/generate', { finding_id: finding.id });
      setFixData(res);
      setApplied(res.applied);
    } catch (err) {
      setError(err.message || 'Failed to generate fix');
    } finally {
      setGenerating(false);
    }
  };

  const handleApplyFix = async () => {
    if (!fixData?.id) return;
    setApplying(true);
    setError(null);
    try {
      await apiClient.post(`/fixes/${fixData.id}/apply`);
      setApplied(true);
    } catch (err) {
      setError(err.message || 'Failed to apply fix');
    } finally {
      setApplying(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '480px',
      backgroundColor: 'var(--bg-surface)',
      borderLeft: '1px solid var(--border-subtle)',
      zIndex: 200,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{
          fontFamily: 'var(--font-sans)',
          fontWeight: 600,
          fontSize: '13px',
          color: 'var(--text-primary)',
        }}>
          Finding Detail
        </span>
        <button
          onClick={onClose}
          style={{
            width: '28px',
            height: '28px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            borderRadius: '4px',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>
        {/* Severity + Rule */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <Badge severity={finding.severity} />
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: 'var(--text-secondary)',
          }}>
            {finding.rule_id}
          </span>
        </div>

        {/* File */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '10px',
            color: 'var(--text-tertiary)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}>
            FILE
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '12px',
            color: 'var(--text-primary)',
          }}>
            {finding.file_path}:{finding.line_number}
          </div>
        </div>

        {/* Scanner */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '10px',
            color: 'var(--text-tertiary)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}>
            SCANNER
          </div>
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
        </div>

        {/* CWE */}
        {finding.cwe && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              CWE
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--text-secondary)',
            }}>
              {finding.cwe}
            </div>
          </div>
        )}

        {/* Message */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontWeight: 500,
            fontSize: '10px',
            color: 'var(--text-tertiary)',
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}>
            MESSAGE
          </div>
          <div style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
            color: 'var(--text-primary)',
            lineHeight: 1.6,
          }}>
            {finding.message}
          </div>
        </div>

        {/* AI Fix Section */}
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid var(--border-subtle)',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '10px',
          }}>
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 600,
              fontSize: '13px',
              color: 'var(--text-primary)',
            }}>
              AI Remediation
            </span>
            {fixData && (
              <Badge status={applied ? 'completed' : fixData.confidence}>
                {applied ? 'Applied' : `${fixData.confidence} confidence`}
              </Badge>
            )}
          </div>

          {fixData ? (
            <div>
              <pre style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                borderRadius: '6px',
                padding: '12px',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                lineHeight: 1.5,
                overflowX: 'auto',
                whiteSpace: 'pre-wrap',
                margin: '8px 0',
              }}>
                {fixData.unified_diff}
              </pre>
              <p style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                lineHeight: 1.5,
                marginBottom: '12px',
              }}>
                {fixData.explanation}
              </p>

              {!applied ? (
                <Button
                  variant="primary"
                  loading={applying}
                  onClick={handleApplyFix}
                  style={{ width: '100%' }}
                >
                  Mark Fix as Applied
                </Button>
              ) : (
                <div style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: '12px',
                  color: 'var(--green-text)',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}>
                  ✓ Fix marked as applied to repository
                </div>
              )}
            </div>
          ) : (
            <div>
              <p style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                marginBottom: '10px',
              }}>
                No fix suggestion currently saved. You can generate a private fix using local Ollama LLM.
              </p>
              <Button
                variant="primary"
                loading={generating}
                onClick={handleGenerateFix}
                style={{ width: '100%' }}
              >
                Generate Local AI Fix
              </Button>
            </div>
          )}

          {error && (
            <div style={{
              marginTop: '8px',
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              color: 'var(--red-text)',
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Correlations */}
        {finding.correlations && finding.correlations.length > 0 && (
          <div style={{
            marginTop: '16px',
            paddingTop: '16px',
            borderTop: '1px solid var(--border-subtle)',
          }}>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 600,
              fontSize: '13px',
              color: 'var(--text-primary)',
              marginBottom: '8px',
            }}>
              Cross-Repo Correlations
            </div>
            {finding.correlations.map((corr, i) => (
              <div key={i} style={{
                padding: '8px 0',
                borderBottom: i < finding.correlations.length - 1 ? '1px solid var(--border-subtle)' : 'none',
              }}>
                <div style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: '12px',
                  color: 'var(--text-primary)',
                }}>
                  {corr.repo_name}
                </div>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--text-tertiary)',
                }}>
                  {corr.file_path}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default FindingDetail;
