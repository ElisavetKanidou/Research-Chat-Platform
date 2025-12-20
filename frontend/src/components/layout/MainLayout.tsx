// components/layout/MainLayout.tsx - COMPLETE WITH HEADER
import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import Dashboard from '../Dashboard';
import Analytics from '../Analytics';
import SettingsPanel from '../SettingsPanel';
import PaperWorkspace from '../PaperWorkspace';
import ResearchChatPlatform from '../../paper/ResearchChatPlatform';
import ReferencePapers from '../ReferencePapers';
import UploadReferencePaperForm from '../UploadReferencePaperForm';
import { useGlobalContext } from '../../contexts/GlobalContext';
import type { Paper } from '../../types/paper';

const MainLayout: React.FC = () => {
  const { activePaper, setActivePaper, user } = useGlobalContext();
  const [activeSection, setActiveSection] = useState<string>('dashboard');
  const [showReferencePapers, setShowReferencePapers] = useState(false);
  const [showUploadReferenceForm, setShowUploadReferenceForm] = useState(false);

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    if (section !== 'workspace' && section !== 'chat' && activePaper) {
      setActivePaper(null);
    }
  };

  const handlePaperSelect = (paper: Paper) => {
    setActivePaper(paper);
    setActiveSection('workspace');
  };

  const handleNewPaper = () => {
    console.log('Creating new paper...');
    setActiveSection('papers');
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  const getHeaderTitle = () => {
    switch (activeSection) {
      case 'dashboard':
        return 'Dashboard';
      case 'papers':
        return 'Papers Management';
      case 'reference-papers':
        return 'Reference Papers';
      case 'chat':
        return 'AI Research Assistant';
      case 'analytics':
        return 'Analytics';
      case 'settings':
        return 'Settings';
      case 'workspace':
        return activePaper?.title || 'Paper Workspace';
      default:
        return 'Research Platform';
    }
  };

  const getHeaderSubtitle = () => {
    switch (activeSection) {
      case 'dashboard':
        return "Here's an overview of your research progress and activities";
      case 'papers':
        return 'Manage and organize your research papers';
      case 'reference-papers':
        return 'Manage papers used for AI writing style personalization';
      case 'chat':
        return activePaper ? `Working on: ${activePaper.title}` : 'Select a paper to start';
      case 'analytics':
        return 'Track your research progress and productivity';
      case 'workspace':
        return activePaper ? `Draft • ${activePaper.progress || 0}% complete` : '';
      default:
        return '';
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <Dashboard
            onPaperSelect={handlePaperSelect}
            onNewPaper={handleNewPaper}
            onViewAnalytics={() => setActiveSection('analytics')}
            onManageReferencePapers={() => setShowReferencePapers(true)}
          />
        );

      case 'papers':
        return (
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-7xl mx-auto">
              <p className="text-gray-600">Manage your research papers here.</p>
            </div>
          </div>
        );

      case 'reference-papers':
        return (
          <ReferencePapers onUploadClick={() => setShowUploadReferenceForm(true)} />
        );

      case 'chat':
        return activePaper ? (
          <ResearchChatPlatform paperContext={activePaper} />
        ) : (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">No paper selected</h3>
              <p className="text-gray-600 mb-4">
                Please select a paper to start chatting with AI Assistant.
              </p>
              <button
                onClick={() => setActiveSection('papers')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Go to Papers
              </button>
            </div>
          </div>
        );

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
            onViewAnalytics={() => setActiveSection('analytics')}
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

      {/* Main Content with Header */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header with Notifications */}
        <Header
          title={getHeaderTitle()}
          subtitle={getHeaderSubtitle()}
          showSearch={activeSection !== 'workspace' && activeSection !== 'chat'}
        />

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {renderContent()}
        </div>
      </div>

      {/* Reference Papers Modal */}
      {showReferencePapers && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-xl font-bold">Reference Papers</h2>
              <button
                onClick={() => setShowReferencePapers(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ReferencePapers onUploadClick={() => setShowUploadReferenceForm(true)} />
            </div>
          </div>
        </div>
      )}

      {/* Upload Reference Paper Modal */}
      {showUploadReferenceForm && (
        <UploadReferencePaperForm
          onClose={() => setShowUploadReferenceForm(false)}
          onSuccess={() => {
            setShowUploadReferenceForm(false);
          }}
        />
      )}
    </div>
  );
};

export default MainLayout;
