/**
 * AEGISCORE — RiskPage
 * Risk map with repo selector, heatmap, trend chart, and ML model status.
 */
import { useState, useEffect } from 'react';
import RiskHeatmap from '../components/risk/RiskHeatmap';
import RiskTrendChart from '../components/risk/RiskTrendChart';
import Card from '../components/ui/Card';
import { getRiskHeatmap, getRiskHistory, getModelStatus } from '../api/risk';
import apiClient from '../api/client';

export function RiskPage() {
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [riskFiles, setRiskFiles] = useState([]);
  const [modelStatus, setModelStatus] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [trendFiles, setTrendFiles] = useState([]);
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
        const files = heatmap.files || [];
        setRiskFiles(files);
        setModelStatus(status);

        // Fetch risk history for top 5 riskiest files
        const topFiles = files.slice(0, 5);
        if (topFiles.length > 0) {
          const historyPromises = topFiles.map(f =>
            getRiskHistory(selectedRepo, f.file_path, 30).catch(() => ({ history: [] }))
          );
          const histories = await Promise.all(historyPromises);

          // Build trend chart data from histories
          const dateMap = {};
          const fileNames = topFiles.map(f => f.file_path);
          setTrendFiles(fileNames);

          histories.forEach((hist, fileIdx) => {
            const points = hist.history || [];
            points.forEach(point => {
              const dateKey = new Date(point.recorded_at).toLocaleDateString('en-US', {
                month: 'short', day: 'numeric',
              });
              if (!dateMap[dateKey]) {
                dateMap[dateKey] = { date: dateKey };
              }
              dateMap[dateKey][`file${fileIdx + 1}`] = point.score;
            });
          });

          const chartData = Object.values(dateMap).sort((a, b) => {
            const da = new Date(a.date + ' 2025');
            const db = new Date(b.date + ' 2025');
            return da - db;
          });

          if (chartData.length > 0) {
            setTrendData(chartData);
          }
        }
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

      {/* Risk Trend Chart — wired to real data */}
      <div style={{ marginBottom: '24px' }}>
        <RiskTrendChart data={trendData} files={trendFiles} />
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
              fontFamily: 'var(--font-sans)', fontWeight: 500, fontSize: '10px',
              color: 'var(--text-tertiary)', letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: '4px',
            }}>
              VERSION
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-primary)' }}>
              {modelStatus?.model_version || 'Not trained'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)', fontWeight: 500, fontSize: '10px',
              color: 'var(--text-tertiary)', letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: '4px',
            }}>
              PRECISION
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-primary)' }}>
              {modelStatus?.precision?.toFixed(3) || '—'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)', fontWeight: 500, fontSize: '10px',
              color: 'var(--text-tertiary)', letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: '4px',
            }}>
              RECALL
            </div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', color: 'var(--text-primary)' }}>
              {modelStatus?.recall?.toFixed(3) || '—'}
            </div>
          </div>

          <div>
            <div style={{
              fontFamily: 'var(--font-sans)', fontWeight: 500, fontSize: '10px',
              color: 'var(--text-tertiary)', letterSpacing: '0.08em',
              textTransform: 'uppercase', marginBottom: '4px',
            }}>
              F1 SCORE
            </div>
            <div style={{
              fontFamily: 'var(--font-mono)', fontSize: '13px',
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
