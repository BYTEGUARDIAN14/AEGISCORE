/**
 * AEGISCORE — Repos API
 */
import apiClient from './client';

export async function listRepos(params = {}) {
  return apiClient.get('/repos', params);
}

export async function getRepo(repoId) {
  return apiClient.get(`/repos/${repoId}`);
}

export async function connectRepo(teamId, name, githubUrl, defaultBranch = 'main') {
  return apiClient.post('/repos', {
    team_id: teamId,
    name,
    github_url: githubUrl,
    default_branch: defaultBranch,
  });
}

export async function updateRepo(repoId, data) {
  return apiClient.put(`/repos/${repoId}`, data);
}

export async function deleteRepo(repoId) {
  return apiClient.delete(`/repos/${repoId}`);
}
