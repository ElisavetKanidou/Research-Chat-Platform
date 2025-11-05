// contexts/GlobalContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import type { Paper } from '../types/paper';
import type { User } from '../types/user';
import { usePaperManagement } from '../hooks/usePaperManagement';
import { authService } from '../services/authService';
import type { UserResponse } from '../types/api';
import { paperService } from '../services/paperService';


// Local interfaces to avoid conflicts
export interface AppNotification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  autoRemove?: boolean;
}

export interface AppGlobalSettings {
  autoSave: boolean;
  defaultView: 'grid' | 'list';
  papersPerPage: number;
  showPreview: boolean;
  enableNotifications: boolean;
}

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
  refreshActivePaper: () => Promise<void>; 
  
  // User management
  user: User | null;
  isAuthenticated: boolean;
  
  // UI state
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  theme: 'light' | 'dark';
  setTheme: (theme: 'light' | 'dark') => void;
  
  // Notifications
  notifications: AppNotification[];
  addNotification: (notification: Omit<AppNotification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  
  // Search
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchResults: Paper[];
  
  // Settings
  settings: AppGlobalSettings;
  updateSettings: (updates: Partial<AppGlobalSettings>) => void;
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined);

export const useGlobalContext = () => {
  const context = useContext(GlobalContext);
  if (!context) {
    throw new Error('useGlobalContext must be used within a GlobalProvider');
  }
  return context;
};

// ΑΝΤΙΚΑΤΑΣΤΗΣΤΕ τη συνάρτηση convertUserResponseToUser στο GlobalContext.tsx
// (Γραμμές περίπου 70-120)

const convertUserResponseToUser = (userData: UserResponse): User => {
  // Safe access to nested properties with fallbacks
  const researchInterests = userData.personalInfo?.researchInterests || 
                            (userData as any).research_interests || 
                            [];
  
  const affiliation = (userData as any).affiliation || 
                      userData.personalInfo?.affiliation || 
                      '';
  
  const subscriptionPlan = (userData as any).subscription_plan || 'free';
  const subscriptionStatus = (userData as any).subscription_status || 'active';
  
  return {
    ...userData,
    createdAt: new Date(userData.createdAt),
    lastLoginAt: new Date(userData.lastLoginAt),
    personalInfo: {
      name: userData.name || '',
      email: userData.email || '',
      affiliation: affiliation,
      researchInterests: researchInterests,
    },
    preferences: {
      theme: 'light',
      language: 'en',
      timezone: 'UTC',
      dateFormat: 'MM/dd/yyyy',
      defaultWordCount: 8000,
      autoSave: true,
      notifications: {
        emailNotifications: true,
        deadlineReminders: true,
        collaborationUpdates: true,
        aiSuggestions: true,
        weeklyReports: false,
        pushNotifications: true,
        reminderFrequency: 'weekly',
      },
      privacy: {
        profileVisibility: 'private',
        shareAnalytics: false,
        dataSyncEnabled: true,
        allowResearchSharing: false,
        trackingOptOut: false,
      },
      aiPersonalization: {
        labLevel: 3,
        personalLevel: 2,
        globalLevel: 1,
        writingStyle: 'academic',
        researchFocus: researchInterests,
        suggestionsEnabled: true,
        contextDepth: 'moderate',
      },
    },
    subscription: {
      plan: subscriptionPlan,
      status: subscriptionStatus,
      startDate: new Date(),
      features: [],
    },
  };
};


export const GlobalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Paper management from custom hook
  const paperManagement = usePaperManagement();
  
  // User state
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // UI state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem('sidebar-collapsed');
      return saved ? JSON.parse(saved) : false;
    } catch {
      return false;
    }
  });
  
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    try {
      const saved = localStorage.getItem('app-theme') as 'light' | 'dark';
      return saved || 'light';
    } catch {
      return 'light';
    }
  });
  
  // Notifications
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  
  // Search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Paper[]>([]);
  
  // Settings
  const [settings, setSettings] = useState<AppGlobalSettings>(() => {
    try {
      const saved = localStorage.getItem('app-settings');
      return saved ? { ...{
        autoSave: true,
        defaultView: 'grid' as const,
        papersPerPage: 12,
        showPreview: true,
        enableNotifications: true,
      }, ...JSON.parse(saved) } : {
        autoSave: true,
        defaultView: 'grid' as const,
        papersPerPage: 12,
        showPreview: true,
        enableNotifications: true,
      };
    } catch {
      return {
        autoSave: true,
        defaultView: 'grid' as const,
        papersPerPage: 12,
        showPreview: true,
        enableNotifications: true,
      };
    }
  });

  // Initialize user data
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const token = authService.getAccessToken();
        const userData = authService.getUserData();
        
        if (token && userData) {
          const userWithDates = convertUserResponseToUser(userData);
          setUser(userWithDates);
          setIsAuthenticated(true);
          
          try {
            // Verify token is still valid
            await authService.getCurrentUser();
          } catch (error) {
            console.warn('Token validation failed:', error);
            // Token invalid, clear auth data
            authService.clearAuthData();
            setUser(null);
            setIsAuthenticated(false);
          }
        }
      } catch (error) {
        console.error('Failed to initialize user:', error);
        setIsAuthenticated(false);
      }
    };

    initializeUser();
  }, []);

  // Persist settings to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('app-settings', JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  }, [settings]);

  useEffect(() => {
    try {
      localStorage.setItem('app-theme', theme);
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  }, [theme]);

  useEffect(() => {
    try {
      localStorage.setItem('sidebar-collapsed', JSON.stringify(sidebarCollapsed));
    } catch (error) {
      console.error('Failed to save sidebar state:', error);
    }
  }, [sidebarCollapsed]);

  // Notification management
  const addNotification = (notification: Omit<AppNotification, 'id' | 'timestamp'>) => {
    const newNotification: AppNotification = {
      ...notification,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };

    setNotifications(prev => [...prev, newNotification]);

    // Auto remove notification after 5 seconds if autoRemove is not explicitly false
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
  const updateSettings = (updates: Partial<AppGlobalSettings>) => {
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
        autoRemove: true,
      });
      return paper;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addNotification({
        type: 'error',
        title: 'Creation Failed',
        message: `Failed to create paper: ${errorMessage}`,
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
          message: 'Changes saved successfully',
          autoRemove: true,
        });
      }
      
      return paper;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: `Failed to save changes: ${errorMessage}`,
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
        autoRemove: true,
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      addNotification({
        type: 'error',
        title: 'Deletion Failed',
        message: `Failed to delete paper: ${errorMessage}`,
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
  }, [settings.autoSave, paperManagement.activePaper, paperManagement.updatePaper]);

  // Search functionality with safe field access
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    const searchTimer = setTimeout(() => {
      const results = paperManagement.papers.filter(paper => {
        const title = paper.title || '';
        const abstract = paper.abstract || '';
        const researchArea = (paper as any).research_area || paper.researchArea || '';
        const coAuthors = (paper as any).co_authors || paper.coAuthors || [];
        
        const query = searchQuery.toLowerCase();
        
        return (
          title.toLowerCase().includes(query) ||
          abstract.toLowerCase().includes(query) ||
          researchArea.toLowerCase().includes(query) ||
          coAuthors.some((author: string) => 
            (author || '').toLowerCase().includes(query)
          )
        );
      });
      setSearchResults(results);
    }, 300);

    return () => clearTimeout(searchTimer);
  }, [searchQuery, paperManagement.papers]);

  // Enhanced setActivePaper to load full paper data
  const setActivePaperEnhanced = async (paper: Paper | null) => {
    if (paper) {
      try {
        // Load full paper with sections from backend
        const fullPaper = await paperService.getPaper(paper.id);
        paperManagement.setActivePaper(fullPaper);
      } catch (error) {
        console.error('Failed to load full paper, using cached data:', error);
        paperManagement.setActivePaper(paper);
      }
    } else {
      paperManagement.setActivePaper(null);
    }
  };
  // Refresh active paper from backend
  const refreshActivePaper = async () => {
    if (paperManagement.activePaper) {
      try {
        const refreshedPaper = await paperService.getPaper(paperManagement.activePaper.id);
        paperManagement.setActivePaper(refreshedPaper);
      } catch (error) {
        console.error('Failed to refresh active paper:', error);
      }
    }
  };

  const contextValue: GlobalContextType = {
    // Paper management
    papers: paperManagement.papers,
    activePaper: paperManagement.activePaper,
    loading: paperManagement.loading,
    error: paperManagement.error,
    refreshActivePaper,
    
    // Enhanced paper operations
    createPaper: createPaperWithNotification,
    updatePaper: updatePaperWithNotification,
    deletePaper: deletePaperWithNotification,
    setActivePaper: setActivePaperEnhanced,
    
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

// Export only the context types with unique names
export type { GlobalContextType };