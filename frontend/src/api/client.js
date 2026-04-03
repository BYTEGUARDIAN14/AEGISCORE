/**
 * AEGISCORE — API Client
 * Centralized HTTP client for all API calls.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE;
  }

  getToken() {
    return localStorage.getItem('aegiscore_token');
  }

  setToken(token) {
    localStorage.setItem('aegiscore_token', token);
  }

  setRefreshToken(token) {
    localStorage.setItem('aegiscore_refresh_token', token);
  }

  getRefreshToken() {
    return localStorage.getItem('aegiscore_refresh_token');
  }

  clearTokens() {
    localStorage.removeItem('aegiscore_token');
    localStorage.removeItem('aegiscore_refresh_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const token = this.getToken();

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    let response;
    try {
      response = await fetch(url, config);
    } catch (networkError) {
      throw new Error(`Network error: Unable to reach ${url}`);
    }

    // Handle 401 — attempt token refresh
    if (response.status === 401 && endpoint !== '/auth/login' && endpoint !== '/auth/refresh') {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${this.getToken()}`;
        response = await fetch(url, { ...config, headers });
      } else {
        this.clearTokens();
        window.location.href = '/login';
        throw new Error('Session expired');
      }
    }

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      const error = new Error(errorData.detail || `HTTP ${response.status}`);
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      this.setToken(data.access_token);
      return true;
    } catch {
      return false;
    }
  }

  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v != null && v !== '')
    ).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, body) {
    return this.request(endpoint, { method: 'POST', body });
  }

  put(endpoint, body) {
    return this.request(endpoint, { method: 'PUT', body });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

const apiClient = new ApiClient();
export default apiClient;
