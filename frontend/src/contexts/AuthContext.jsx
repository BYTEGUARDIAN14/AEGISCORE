/**
 * AEGISCORE — Auth Context
 * Global authentication state management.
 */
import { createContext, useCallback, useEffect, useState } from 'react';
import { getMe, login as apiLogin, logout as apiLogout, isAuthenticated } from '../api/auth';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadUser = useCallback(async () => {
    if (!isAuthenticated()) {
      setLoading(false);
      return;
    }
    try {
      const userData = await getMe();
      setUser(userData);
      setError(null);
    } catch (err) {
      setUser(null);
      if (err.status === 401) {
        apiLogout();
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      await apiLogin(email, password);
      await loadUser();
      return true;
    } catch (err) {
      setError(err.message || 'Login failed');
      return false;
    }
  }, [loadUser]);

  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
