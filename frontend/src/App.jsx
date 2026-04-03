/**
 * AEGISCORE — App Component
 * Root component with routing configuration.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { OrgProvider } from './contexts/OrgContext';
import { useAuth } from './hooks/useAuth';
import AppShell from './components/layout/AppShell';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import RepoPage from './pages/RepoPage';
import FindingsPage from './pages/FindingsPage';
import RiskPage from './pages/RiskPage';
import FixesPage from './pages/FixesPage';
import CorrelationsPage from './pages/CorrelationsPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--bg-base)',
      }}>
        <div style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '13px',
          color: 'var(--text-tertiary)',
        }}>
          Loading...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/repos" element={<RepoPage />} />
        <Route path="/repos/:repoId" element={<RepoPage />} />
        <Route path="/findings" element={<FindingsPage />} />
        <Route path="/risk" element={<RiskPage />} />
        <Route path="/fixes" element={<FixesPage />} />
        <Route path="/correlations" element={<CorrelationsPage />} />
        <Route path="/settings" element={<div style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-sans)', fontSize: '13px' }}>Settings — Coming soon</div>} />
        <Route path="/docs" element={<div style={{ color: 'var(--text-tertiary)', fontFamily: 'var(--font-sans)', fontSize: '13px' }}>Documentation — Visit byteaegis.in</div>} />
      </Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <OrgProvider>
          <AppRoutes />
        </OrgProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
