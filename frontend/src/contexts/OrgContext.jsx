/**
 * AEGISCORE — Org Context
 * Global organization selection state.
 */
import { createContext, useCallback, useState } from 'react';

export const OrgContext = createContext(null);

export function OrgProvider({ children }) {
  const [currentOrg, setCurrentOrg] = useState(() => {
    const saved = localStorage.getItem('aegiscore_org');
    return saved ? JSON.parse(saved) : null;
  });

  const selectOrg = useCallback((org) => {
    setCurrentOrg(org);
    if (org) {
      localStorage.setItem('aegiscore_org', JSON.stringify(org));
    } else {
      localStorage.removeItem('aegiscore_org');
    }
  }, []);

  const value = {
    currentOrg,
    selectOrg,
    orgId: currentOrg?.id || null,
    orgName: currentOrg?.name || 'Select Organization',
  };

  return (
    <OrgContext.Provider value={value}>
      {children}
    </OrgContext.Provider>
  );
}
