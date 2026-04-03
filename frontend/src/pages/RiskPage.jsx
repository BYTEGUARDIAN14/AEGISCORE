/**
 * AEGISCORE — RiskPage
 * Risk map with repo selector, heatmap, trend chart, and ML model status.
 */
import { useState, useEffect } from 'react';
import RiskHeatmap from '../components/risk/RiskHeatmap';
import RiskTrendChart from '../components/risk/RiskTrendChart';
import Card from '../components/ui/Card';
import { getRiskHeatmap, getModelStatus } from '../api/risk';
import apiClient from '../api/client';

export function RiskPage() {
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [riskFiles, setRiskFiles] = useState([]);
  const [modelStatus, setModelStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchRepos() {
      try {
        const repoList = await apiClient.get('/repos');
        setRepos(repoList || []);
        if (repoList && repoList.length > 0) {
          setSelectedRepo(repoList[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch repos:', err);
      }
    }
    fetchRepos();
  }, []);

  useEffect(() => {
    async function fetchRiskData() {
      if (!selectedRepo) {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [heatmap, status] = await Promise.all([
          getRiskHeatmap(selectedRepo, 0, 50),
          getModelStatus(),
        ]);
        setRiskFiles(heatmap.files || []);
        setModelStatus(status);
      } catch (err) {
        console.error('Failed to fetch risk data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchRiskData();
  }, [selectedRepo]);

  return (
    <div>
      {/* Repo Selector */}
      <div style={{ marginBottom: '24px' }}>
        <select
          value={selectedRepo}
          onChange={(e) => setSelectedRepo(e.target.value)}
          style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            borderRadius: '4px',
            padding: '8px 14px',
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
            color: 'var(--text-primary)',
            minWidth: '240px',
          }}
        >
          <option value="">Select Repository</option>
          {repos.map((repo) => (
            <option key={repo.id} value={repo.id}>{repo.name}</option>
          ))}
        </select>
      </div>

      {/* Risk Heatmap */}
      <div style={{ marginBottom: '24px' }}>
        <RiskHeatmap files={riskFiles} loading={loading} />
      </div>

      {/* Risk Trend Chart */}
      <div style={{ marginBottom: '24px' }}>
        <RiskTrendChart />
      </div>

      {/* ML Model Status */}
      <Card>
        <div style={{
          fontFamily: 'var(--font-sans)',
          fontWeight: 600,
          fontSize: '13px',
          color: 'var(--text-primary)',
          marginBottom: '16px',
        }}>
          ML Model Status
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              VERSION
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: 'var(--text-primary)',
            }}>
              {modelStatus?.model_version || 'Not trained'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              PRECISION
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: 'var(--text-primary)',
            }}>
              {modelStatus?.precision?.toFixed(3) || '—'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              RECALL
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: 'var(--text-primary)',
            }}>
              {modelStatus?.recall?.toFixed(3) || '—'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)',
              fontWeight: 500,
              fontSize: '10px',
              color: 'var(--text-tertiary)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}>
              F1 SCORE
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '13px',
              color: modelStatus?.f1_score >= 0.8 ? 'var(--green-text)' : modelStatus?.f1_score >= 0.5 ? 'var(--amber-text)' : 'var(--text-primary)',
            }}>
              {modelStatus?.f1_score?.toFixed(3) || '—'}
            </div>
          </div>
        </div>

        <div style={{
          marginTop: '12px',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          color: 'var(--text-tertiary)',
        }}>
          {modelStatus?.is_trained
            ? `Trained on ${modelStatus.training_samples} samples • Next retrain in ${modelStatus.next_retrain_in} scans`
            : 'Model not yet trained — requires minimum 50 scan samples'
          }
        </div>
      </Card>
    </div>
  );
}

export default RiskPage;
