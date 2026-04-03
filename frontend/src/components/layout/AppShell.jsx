/**
 * AEGISCORE — AppShell Component
 * Main layout: sidebar + header + content area.
 */
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

export function AppShell() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{
        marginLeft: 'var(--sidebar-width)',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
      }}>
        <Header />
        <main style={{
          flex: 1,
          padding: '24px',
          backgroundColor: 'var(--bg-base)',
          overflowY: 'auto',
        }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppShell;
