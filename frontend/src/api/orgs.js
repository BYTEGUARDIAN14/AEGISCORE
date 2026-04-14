/**
 * AEGISCORE — Orgs API
 */
import apiClient from './client';

export async function createOrg(name, slug, plan = 'community') {
  return apiClient.post('/orgs', { name, slug, plan });
}

export async function getOrg(orgId) {
  return apiClient.get(`/orgs/${orgId}`);
}

export async function listTeams(orgId) {
  return apiClient.get(`/orgs/${orgId}/teams`);
}

export async function createTeam(orgId, name, slug) {
  return apiClient.post(`/orgs/${orgId}/teams`, { name, slug });
}

export async function addTeamMember(orgId, teamId, userId, role = 'member') {
  return apiClient.post(`/orgs/${orgId}/teams/${teamId}/members`, {
    user_id: userId,
    role,
  });
}

export async function removeTeamMember(orgId, teamId, userId) {
  return apiClient.delete(`/orgs/${orgId}/teams/${teamId}/members/${userId}`);
}
