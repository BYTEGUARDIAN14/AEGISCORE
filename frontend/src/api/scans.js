/**
 * AEGISCORE — Scans API
 */
import apiClient from './client';

export async function triggerScan(repoId, commitSha, branch, scanners = ['semgrep', 'bandit', 'trivy']) {
  return apiClient.post('/scans/trigger', {
    repo_id: repoId,
    commit_sha: commitSha,
    branch,
    scanners,
  });
}

export async function listScans(params = {}) {
  return apiClient.get('/scans', params);
}

export async function getScan(scanId) {
  return apiClient.get(`/scans/${scanId}`);
}

export async function getScanStatus(scanId) {
  return apiClient.get(`/scans/${scanId}/status`);
}
