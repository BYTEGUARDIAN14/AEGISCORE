/**
 * AEGISCORE — Auth API
 */
import apiClient from './client';

export async function login(email, password) {
  const data = await apiClient.post('/auth/login', { email, password });
  apiClient.setToken(data.access_token);
  apiClient.setRefreshToken(data.refresh_token);
  return data;
}

export async function register(email, password, fullName) {
  return apiClient.post('/auth/register', { email, password, full_name: fullName });
}

export async function getMe() {
  return apiClient.get('/auth/me');
}

export async function refreshToken() {
  return apiClient.refreshAccessToken();
}

export function logout() {
  apiClient.clearTokens();
}

export function isAuthenticated() {
  return !!apiClient.getToken();
}
