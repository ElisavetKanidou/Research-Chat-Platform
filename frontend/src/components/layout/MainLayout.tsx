// components/layout/MainLayout.tsx
import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import Dashboard from '../Dashboard';
import Analytics from '../Analytics';
import SettingsPanel from '../SettingsPanel';
import PaperWorkspace from '../PaperWorkspace';
import ResearchChatPlatform from '../../paper/ResearchChatPlatform';
import { useGlobalContext } from '../../contexts/GlobalContext';
import type { Paper } from '../../types/paper';

const MainLayout: React.FC = () => {
  const { activePaper, setActivePaper } = useGlobalContext();
  const [activeSection, setActiveSection] = useState<string>('dashboard');

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    // Clear active paper when switching sections (except workspace)
    if (section !== 'workspace' && activePaper) {
      setActivePaper(null);
    }
  };

  const handlePaperSelect = (paper: Paper) => {
    setActivePaper(paper);
    setActiveSection('workspace');
  };

  const handleNewPaper = () => {
    // Logic to create new paper would go here
    console.log('Creating new paper...');
    setActiveSection('papers');
  };

  const handleLogout = () => {
    console.log('Logging out...');
    // Logout logic would go here
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <Dashboard 
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
          />
        );
      
      case 'papers':
        return (
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-7xl mx-auto">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">Papers Management</h1>
              <p className="text-gray-600">Manage your research papers here.</p>
              {/* Add your Papers component here */}
            </div>
          </div>
        );
      
      case 'chat':
        return <ResearchChatPlatform />;
      
      case 'analytics':
        return <Analytics />;
      
      case 'settings':
        return <SettingsPanel />;
      
      case 'workspace':
        return activePaper ? (
          <PaperWorkspace onClose={() => setActiveSection('papers')} />
        ) : (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No paper selected</h3>
              <p className="text-gray-600">Please select a paper to work on.</p>
            </div>
          </div>
        );
      
      default:
        return (
          <Dashboard 
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
          />
        );
    }
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <Sidebar
        activeSection={activeSection}
        onSectionChange={handleSectionChange}
        onNewPaper={handleNewPaper}
        onLogout={handleLogout}
      />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {renderContent()}
      </div>
    </div>
  );
};

export default MainLayout;