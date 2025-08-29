// contexts/GlobalContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { Paper } from '../types/paper';
import { User } from '../types/user';
import { usePaperManagement } from '../hooks/usePaperManagement';
import { authService } from '../services/authService';

interface GlobalContextType {
  // Paper management
  papers: Paper[];
  activePaper: Paper | null;
  loading: boolean;
  error: string | null;
  
  // Paper operations
  createPaper: (paperData: Partial<Paper>) => Promise<Paper>;
  updatePaper: (paperId: string, updates: Partial<Paper>) => Promise<Paper>;
  deletePaper: (paperId: string) => Promise<void>;
  setActivePaper: (paper: Paper | null) => void;
  
  // User management
  user: User | null;
  isAuthenticated: boolean;
  
  // UI state
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  
  // Notifications
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  
  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchResults: any[];
  
  // Settings
  settings: GlobalSettings;
  updateSettings: (updates: Partial<GlobalSettings>) => void;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoRemove?: boolean;
}

interface GlobalSettings {
  autoSave: boolean;
  defaultView: 'grid' | 'list';
  papersPerPage: number;
  showPreview: boolean;
  enableNotifications: boolean;
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined);

export const useGlobalContext = () => {
  const context = useContext(GlobalContext);
  if (!context) {
    throw new Error('useGlobalContext must be used within a GlobalProvider');
  }
  return context;
};

export const GlobalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Paper management from custom hook
  const paperManagement = usePaperManagement();
  
  // User state
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // UI state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  // Notifications
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  
  // Settings
  const [settings, setSettings] = useState<GlobalSettings>({
    autoSave: true,
    defaultView: 'grid',
    papersPerPage: 12,
    showPreview: true,
    enableNotifications: true,
  });

  // Initialize user data
  useEffect(() => {
    const initializeUser = async () => {
      const token = authService.getAccessToken();
      const userData = authService.getUserData();
      
      if (token && userData) {
        setUser(userData as User);
        setIsAuthenticated(true);
        
        try {
          // Verify token is still valid
          await authService.getCurrentUser();
        } catch (error) {
          // Token invalid, clear auth data
          authService.clearAuthData();
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    };

    initializeUser();
  }, []);

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('app-settings');
    if (savedSettings) {
      try {
        setSettings({ ...settings, ...JSON.parse(savedSettings) });
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    }

    const savedTheme = localStorage.getItem('app-theme') as 'light' | 'dark';
    if (savedTheme) {
      setTheme(savedTheme);
    }

    const savedSidebarState = localStorage.getItem('sidebar-collapsed');
    if (savedSidebarState) {
      setSidebarCollapsed(JSON.parse(savedSidebarState));
    }
  }, []);

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem('app-settings', JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('sidebar-collapsed', JSON.stringify(sidebarCollapsed));
  }, [sidebarCollapsed]);

  // Notification management
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
    };

    setNotifications(prev => [...prev, newNotification]);

    // Auto remove notification after 5 seconds if autoRemove is true
    if (notification.autoRemove !== false) {
      setTimeout(() => {
        removeNotification(newNotification.id);
      }, 5000);
    }
  };

  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  // Settings management
  const updateSettings = (updates: Partial<GlobalSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
  };

  // Enhanced paper operations with notifications
  const createPaperWithNotification = async (paperData: Partial<Paper>): Promise<Paper> => {
    try {
      const paper = await paperManagement.createPaper(paperData);
      addNotification({
        type: 'success',
        title: 'Paper Created',
        message: `Successfully created "${paper.title}"`,
      });
      return paper;
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Creation Failed',
        message: 'Failed to create paper. Please try again.',
      });
      throw error;
    }
  };

  const updatePaperWithNotification = async (paperId: string, updates: Partial<Paper>): Promise<Paper> => {
    try {
      const paper = await paperManagement.updatePaper(paperId, updates);
      
      if (settings.enableNotifications) {
        addNotification({
          type: 'success',
          title: 'Paper Updated',
          message: `Changes saved successfully`,
          autoRemove: true,
        });
      }
      
      return paper;
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'Failed to save changes. Please try again.',
      });
      throw error;
    }
  };

  const deletePaperWithNotification = async (paperId: string): Promise<void> => {
    try {
      await paperManagement.deletePaper(paperId);
      addNotification({
        type: 'success',
        title: 'Paper Deleted',
        message: 'Paper has been permanently deleted',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Deletion Failed',
        message: 'Failed to delete paper. Please try again.',
      });
      throw error;
    }
  };

  // Auto-save functionality
  useEffect(() => {
    if (!settings.autoSave || !paperManagement.activePaper) return;

    const autoSaveInterval = setInterval(async () => {
      try {
        // Auto-save active paper changes
        await paperManagement.updatePaper(paperManagement.activePaper!.id, {
          lastModified: new Date(),
        });
      } catch (error) {
        console.error('Auto-save failed:', error);
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearInterval(autoSaveInterval);
  }, [settings.autoSave, paperManagement.activePaper]);

  // Search functionality
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const searchTimer = setTimeout(() => {
      const results = paperManagement.papers.filter(paper =>
        paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        paper.abstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
        paper.researchArea.toLowerCase().includes(searchQuery.toLowerCase()) ||
        paper.coAuthors.some(author => 
          author.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
      setSearchResults(results);
    }, 300);

    return () => clearTimeout(searchTimer);
  }, [searchQuery, paperManagement.papers]);

  const contextValue: GlobalContextType = {
    // Paper management
    papers: paperManagement.papers,
    activePaper: paperManagement.activePaper,
    loading: paperManagement.loading,
    error: paperManagement.error,
    
    // Enhanced paper operations
    createPaper: createPaperWithNotification,
    updatePaper: updatePaperWithNotification,
    deletePaper: deletePaperWithNotification,
    setActivePaper: paperManagement.setActivePaper,
    
    // User management
    user,
    isAuthenticated,
    
    // UI state
    sidebarCollapsed,
    setSidebarCollapsed,
    theme,
    setTheme,
    
    // Notifications
    notifications,
    addNotification,
    removeNotification,
    
    // Search
    searchQuery,
    setSearchQuery,
    searchResults,
    
    // Settings
    settings,
    updateSettings,
  };

  return (
    <GlobalContext.Provider value={contextValue}>
      {children}
    </GlobalContext.Provider>
  );
};