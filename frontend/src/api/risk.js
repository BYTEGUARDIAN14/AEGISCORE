/**
 * AEGISCORE — Risk API
 */
import apiClient from './client';

export async function getRiskHeatmap(repoId, minScore = 0.0, limit = 50) {
  return apiClient.get('/risk/heatmap', { repo_id: repoId, min_score: minScore, limit });
}

export async function getRiskHistory(repoId, filePath, days = 30) {
  return apiClient.get('/risk/history', { repo_id: repoId, file_path: filePath, days });
}

export async function getModelStatus() {
  return apiClient.get('/risk/model/status');
}
