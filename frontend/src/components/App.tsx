// components/App.tsx - COMPLETE FIXED VERSION
import React, { useState, useEffect } from 'react';
import { GlobalProvider, useGlobalContext } from '../contexts/GlobalContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { authService } from '../services/authService';
import type { Paper } from '../types/paper';
import Dashboard from './Dashboard';
import PapersManagement from './PapersManagement';
import Analytics from './Analytics';
import SettingsPanel from './SettingsPanel';
import PaperWorkspace from './PaperWorkspace';
import ReferencePapers from './ReferencePapers';
import UploadReferencePaperForm from './UploadReferencePaperForm';
import LoginPage from './auth/LoginPage';
import NotificationBell from './layout/NotificationBell';
import { Search, Menu, X, LogOut } from 'lucide-react';

type ViewType = 'dashboard' | 'papers' | 'workspace' | 'analytics' | 'settings' | 'reference-papers';

// Notification Component
const NotificationCenter: React.FC = () => {
  const { notifications, removeNotification } = useGlobalContext();

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg shadow-lg border ${
            notification.type === 'success' ? 'bg-green-50 border-green-200' :
            notification.type === 'error' ? 'bg-red-50 border-red-200' :
            notification.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
            'bg-blue-50 border-blue-200'
          }`}
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className={`font-medium text-sm ${
                notification.type === 'success' ? 'text-green-800' :
                notification.type === 'error' ? 'text-red-800' :
                notification.type === 'warning' ? 'text-yellow-800' :
                'text-blue-800'
              }`}>
                {notification.title}
              </h4>
              <p className={`text-sm mt-1 ${
                notification.type === 'success' ? 'text-green-600' :
                notification.type === 'error' ? 'text-red-600' :
                notification.type === 'warning' ? 'text-yellow-600' :
                'text-blue-600'
              }`}>
                {notification.message}
              </p>
            </div>
            <button
              onClick={() => removeNotification(notification.id)}
              className="ml-2 text-gray-400 hover:text-gray-600"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

// Main Research Platform component
const ResearchPlatform: React.FC = () => {
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');
  const [showUploadReferenceForm, setShowUploadReferenceForm] = useState(false);
  const [referencePapersRefreshTrigger, setReferencePapersRefreshTrigger] = useState(0);

  const {
    user,
    searchQuery,
    setSearchQuery,
    searchResults,
    createPaper,
    sidebarCollapsed,
    setSidebarCollapsed,
    theme,
    setTheme,
    setActivePaper,
  } = useGlobalContext();

  // Handle logout
  const handleLogout = async () => {
    await authService.logout();
    window.location.reload(); // Reload to reset auth state
  };

  // Handle paper selection
  const handlePaperSelect = (paper: Paper) => {
    setActivePaper(paper);
    setCurrentView('workspace');
  };

  // Handle new paper creation
  const handleNewPaper = async () => {
    try {
      const newPaper = await createPaper({
        title: 'Untitled Research Paper',
        researchArea: 'General',
        targetWordCount: 8000,
      });
      setActivePaper(newPaper);
      setCurrentView('workspace');
    } catch (error) {
      console.error('Failed to create new paper:', error);
    }
  };

  // Navigation items
  const navigationItems = [
    { key: 'dashboard', label: 'Dashboard', icon: '📊' },
    { key: 'papers', label: 'Papers', icon: '📄' },
    { key: 'reference-papers', label: 'Reference Papers', icon: '📚' },
    { key: 'analytics', label: 'Analytics', icon: '📈' },
    { key: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  // Render current view
  const renderCurrentView = () => {
    switch (currentView) {
      case 'dashboard':
        return (
          <Dashboard
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
            onViewAnalytics={() => setCurrentView('analytics')}
            onManageReferencePapers={() => setCurrentView('reference-papers')}
          />
        );
      case 'papers':
        return (
          <PapersManagement
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
          />
        );
      case 'reference-papers':
        return (
          <ReferencePapers
            onUploadClick={() => setShowUploadReferenceForm(true)}
            refreshTrigger={referencePapersRefreshTrigger}
          />
        );
      case 'workspace':
        return <PaperWorkspace onClose={() => setCurrentView('dashboard')} />;
      case 'analytics':
        return <Analytics />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return (
          <Dashboard
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
            onViewAnalytics={() => setCurrentView('analytics')}
          />
        );
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Left side */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <Menu size={20} />
              </button>
              <div className="flex items-center">
                <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Research Platform</h1>
              </div>
            </div>

            {/* Center - Search */}
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
                <input
                  type="text"
                  placeholder="Search papers, collaborators, or content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                />
                {searchResults.length > 0 && searchQuery && (
                  <div className="absolute top-full mt-1 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
                    {searchResults.map((paper) => (
                      <button
                        key={paper.id}
                        onClick={() => {
                          handlePaperSelect(paper);
                          setSearchQuery('');
                        }}
                        className="w-full px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                      >
                        <div className="font-medium text-gray-900 dark:text-white truncate">{paper.title}</div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">{paper.researchArea}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {theme === 'light' ? '🌙' : '☀️'}
              </button>
              
              <div className="relative z-50">
                <NotificationBell />
              </div>
              
              {user && (
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    {user.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
                    {user.name}
                  </span>
                </div>
              )}

              <button
                onClick={handleLogout}
                className="p-2 rounded-md text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <nav className={`bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-64'
        }`}>
          <div className="p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => setCurrentView(item.key as ViewType)}
                  className={`w-full flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    currentView === item.key
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className="text-lg mr-3">{item.icon}</span>
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Main content */}
        <main className="flex-1 overflow-hidden">
          {renderCurrentView()}
        </main>
      </div>

      {/* Notifications */}
      <NotificationCenter />

      {/* Upload Reference Paper Modal */}
      {showUploadReferenceForm && (
        <UploadReferencePaperForm
          onClose={() => setShowUploadReferenceForm(false)}
          onSuccess={() => {
            setShowUploadReferenceForm(false);
            // Trigger refresh of Reference Papers list
            setReferencePapersRefreshTrigger(prev => prev + 1);
          }}
        />
      )}
    </div>
  );
};

// Auth wrapper component
const AuthenticatedApp: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = authService.getAccessToken();
      
      if (!token || authService.isTokenExpired()) {
        setIsAuthenticated(false);
        setIsCheckingAuth(false);
        return;
      }

      try {
        await authService.getCurrentUser();
        setIsAuthenticated(true);
        authService.setupTokenRefresh();
      } catch (error) {
        console.error('Auth check failed:', error);
        authService.clearAuthData();
        setIsAuthenticated(false);
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <GlobalProvider>
      <NotificationProvider>
        <ResearchPlatform />
      </NotificationProvider>
    </GlobalProvider>
  );
};

// Main App component
const App: React.FC = () => {
  return <AuthenticatedApp />;
};

export default App;