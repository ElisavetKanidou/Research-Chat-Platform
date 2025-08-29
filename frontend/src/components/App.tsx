// App.tsx - Complete Main Application
import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { UserProvider } from './contexts/UserContext';
import ResearchPlatform from './components/ResearchPlatform';
import './styles/globals.css';

function App() {
  return (
    <ThemeProvider>
      <UserProvider>
        <div className="App">
          <ResearchPlatform />
        </div>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;

// components/ResearchPlatform.tsx - Updated Main Platform Component
import React, { useState } from 'react';
import { Home, FileText, MessageSquare, BarChart3, Settings, Plus } from 'lucide-react';
import { usePaperManagement } from '../hooks/usePaperManagement';
import { useUser } from '../contexts/UserContext';
import Dashboard from './Dashboard';
import PapersManagement from './PapersManagement';
import ResearchChatPlatform from './paper/ResearchChatPlatform';
import Analytics from './Analytics';
import SettingsPanel from './SettingsPanel';
import PaperWorkspace from './PaperWorkspace';
import { LoadingSpinner } from './common/LoadingSpinner';

const ResearchPlatform = () => {
  const [activeSection, setActiveSection] = useState<'dashboard' | 'papers' | 'chat' | 'analytics' | 'settings' | 'workspace'>('dashboard');
  const { isAuthenticated, user } = useUser();
  const {
    papers,
    activePaper,
    loading,
    error,
    createPaper,
    updatePaper,
    deletePaper,
    selectPaper,
  } = usePaperManagement();

  // Mock authentication for development
  React.useEffect(() => {
    if (!isAuthenticated) {
      // Auto-login for development
      // In production, this would redirect to login page
    }
  }, [isAuthenticated]);

  const handlePaperSelect = (paper: any) => {
    selectPaper(paper);
    setActiveSection('workspace');
  };

  const handleNewPaper = async () => {
    try {
      const newPaper = await createPaper({
        title: 'Untitled Research Paper',
        researchArea: '',
      });
      selectPaper(newPaper);
      setActiveSection('workspace');
    } catch (error) {
      console.error('Error creating new paper:', error);
    }
  };

  const navigateToSection = (section: typeof activeSection) => {
    if (section === 'workspace' && !activePaper) {
      setActiveSection('papers');
      return;
    }
    setActiveSection(section);
  };

  const renderContent = () => {
    if (loading && papers.length === 0) {
      return (
        <div className="flex-1 flex items-center justify-center">
          <LoadingSpinner size="lg" text="Loading your research workspace..." />
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-red-600 mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      );
    }

    switch (activeSection) {
      case 'dashboard':
        return <Dashboard onPaperSelect={handlePaperSelect} onNewPaper={handleNewPaper} />;
      case 'papers':
        return <PapersManagement onPaperSelect={handlePaperSelect} onNewPaper={handleNewPaper} />;
      case 'chat':
        return <ResearchChatPlatform />;
      case 'analytics':
        return <Analytics />;
      case 'settings':
        return <SettingsPanel />;
      case 'workspace':
        return activePaper ? <PaperWorkspace /> : <PapersManagement onPaperSelect={handlePaperSelect} onNewPaper={handleNewPaper} />;
      default:
        return <Dashboard onPaperSelect={handlePaperSelect} onNewPaper={handleNewPaper} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar Navigation */}
      <div className="w-80 bg-white shadow-lg flex flex-col">
        {/* Header */}
        <div className="p-6 border-b">
          <h1 className="text-xl font-bold text-gray-900">ResearchHub</h1>
          <p className="text-sm text-gray-600">Comprehensive Research Management</p>
          {user && (
            <div className="mt-2 text-xs text-gray-500">
              Welcome back, {user.name}
            </div>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-6">
          <div className="space-y-2">
            <button
              onClick={() => navigateToSection('dashboard')}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === 'dashboard' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <Home size={20} />
              <span>Dashboard</span>
            </button>

            <button
              onClick={() => navigateToSection('papers')}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === 'papers' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <FileText size={20} />
              <div className="flex items-center justify-between flex-1">
                <span>Papers Management</span>
                {papers.length > 0 && (
                  <span className="text-xs bg-gray-200 px-2 py-1 rounded-full">
                    {papers.length}
                  </span>
                )}
              </div>
            </button>

            {activePaper && (
              <div className="ml-4 mt-2">
                <button
                  onClick={() => navigateToSection('workspace')}
                  className={`w-full flex items-center gap-3 p-2 text-left rounded-lg transition-colors text-sm ${
                    activeSection === 'workspace' ? 'bg-blue-50 text-blue-600' : 'hover:bg-gray-50 text-gray-600'
                  }`}
                >
                  <div className="w-2 h-2 bg-blue-500 rounded-full" />
                  <span className="truncate">{activePaper.title}</span>
                </button>
              </div>
            )}

            <button
              onClick={() => navigateToSection('chat')}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === 'chat' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <MessageSquare size={20} />
              <span>AI Research Assistant</span>
            </button>

            <button
              onClick={() => navigateToSection('analytics')}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === 'analytics' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <BarChart3 size={20} />
              <span>Analytics & Insights</span>
            </button>

            <button
              onClick={() => navigateToSection('settings')}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === 'settings' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </div>
        </nav>

        {/* Quick Actions */}
        <div className="p-6 border-t">
          <button
            onClick={handleNewPaper}
            className="w-full flex items-center justify-center gap-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            disabled={loading}
          >
            <Plus size={20} />
            <span>New Paper</span>
          </button>
          
          {activePaper && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Active Paper</div>
              <div className="text-sm font-medium text-gray-900 truncate">{activePaper.title}</div>
              <div className="text-xs text-gray-500 mt-1">{activePaper.progress}% complete</div>
              <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
                <div
                  className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                  style={{ width: `${activePaper.progress}%` }}
                />
              </div>
            </div>
          )}

          {papers.length > 0 && (
            <div className="mt-3 text-xs text-gray-500 text-center">
              Total: {papers.length} papers • {papers.reduce((sum, p) => sum + p.currentWordCount, 0).toLocaleString()} words
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {renderContent()}
      </div>
    </div>
  );
};

export default ResearchPlatform;