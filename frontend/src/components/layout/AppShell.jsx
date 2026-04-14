/**
 * AEGISCORE — AppShell Component
 * Main layout: sidebar + header + content area + scan modal.
 */
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import ScanTriggerModal from '../dashboard/ScanTriggerModal';

export function AppShell() {
  const [scanModalOpen, setScanModalOpen] = useState(false);

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
        <Header onNewScan={() => setScanModalOpen(true)} />
        <main style={{
          flex: 1,
          padding: '24px',
          backgroundColor: 'var(--bg-base)',
          overflowY: 'auto',
        }}>
          <Outlet />
        </main>
      </div>

      <ScanTriggerModal
        isOpen={scanModalOpen}
        onClose={() => setScanModalOpen(false)}
        onTriggered={() => setScanModalOpen(false)}
      />
    </div>
  );
}

export default AppShell;
