// hooks/useGlobalContext.ts
import { useContext } from 'react';
import { GlobalContext } from '../contexts/GlobalContext';

export const useGlobalContext = () => {
  const context = useContext(GlobalContext);
  if (!context) {
    throw new Error('useGlobalContext must be used within a GlobalProvider');
  }
  return context;
};

// Re-export for convenience
export * from '../contexts/GlobalContext';