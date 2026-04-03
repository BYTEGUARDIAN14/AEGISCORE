/**
 * AEGISCORE — Correlations API
 */
import apiClient from './client';

export async function listCorrelations(params = {}) {
  return apiClient.get('/correlations', params);
}
