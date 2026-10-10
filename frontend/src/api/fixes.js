/**
 * AEGISCORE — Fixes API
 */
import apiClient from './client';

export async function listFixes(params = {}) {
  return apiClient.get('/fixes', params);
}

export async function applyFix(fixId) {
  return apiClient.post(`/fixes/${fixId}/apply`);
}

export async function generateFix(findingId) {
  return apiClient.post('/fixes/generate', { finding_id: findingId });
}
