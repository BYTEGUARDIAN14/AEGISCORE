/**
 * AEGISCORE — Findings API
 */
import apiClient from './client';

export async function listFindings(params = {}) {
  return apiClient.get('/findings', params);
}

export async function getFinding(findingId) {
  return apiClient.get(`/findings/${findingId}`);
}
