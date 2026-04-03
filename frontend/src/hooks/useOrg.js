/**
 * AEGISCORE — useOrg Hook
 * Convenience wrapper for OrgContext.
 */
import { useContext } from 'react';
import { OrgContext } from '../contexts/OrgContext';

export function useOrg() {
  const context = useContext(OrgContext);
  if (!context) {
    throw new Error('useOrg must be used within an OrgProvider');
  }
  return context;
}

export default useOrg;
