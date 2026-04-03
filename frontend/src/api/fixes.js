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
