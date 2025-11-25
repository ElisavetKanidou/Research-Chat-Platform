// components/PaperWorkspace.tsx - UPDATED WITH SETTINGS NAVIGATION

import React, { useState } from 'react';
import { ArrowLeft, FileText, MessageSquare, BarChart3, Settings } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';

import CurrentPaperComponent from '../paper/CurrentPaperComponent';
import ResearchChatPlatform from '../paper/ResearchChatPlatform';
import ResearchProgressComponent from '../paper/ResearchProgressComponent';
import PaperAISettingsComponent from '../paper/PaperAISettings';

interface PaperWorkspaceProps {
  onClose?: () => void;
}

const PaperWorkspace: React.FC<PaperWorkspaceProps> = ({ onClose }) => {
  const { activePaper, setActivePaper } = useGlobalContext();
  const [workspaceTab, setWorkspaceTab] = useState<'paper' | 'chat' | 'progress' | 'ai-settings'>('paper');

  const handleBack = () => {
    setActivePaper(null);
    if (onClose) {
      onClose();
    }
  };

  // ✅ NEW: Function to navigate to AI Settings tab (called from chat)
  const handleNavigateToAISettings = () => {
    setWorkspaceTab('ai-settings');
  };

  if (!activePaper) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center">
          <FileText size={64} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No paper selected</h3>
          <p className="text-gray-600">Please select a paper to work on from the Papers Management section.</p>
        </div>
      </div>
    );
  }

  // Helper to get date safely
  const getLastModified = () => {
    const date = (activePaper as any).updated_at || activePaper.lastModified || activePaper.createdAt;
    return date instanceof Date ? date : new Date(date);
  };

  // Helper to get word count safely
  const getCurrentWordCount = () => {
    return (activePaper as any).current_word_count || activePaper.currentWordCount || 0;
  };

  const lastModified = getLastModified();
  const currentWordCount = getCurrentWordCount();

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Workspace Header */}
      <div className="bg-white border-b p-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Back to Papers"
            >
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 truncate max-w-md lg:max-w-xl">
                {activePaper.title}
              </h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                <span className="capitalize">{activePaper.status.replace('-', ' ')}</span>
                <span>{activePaper.progress}% complete</span>
                <span>{currentWordCount.toLocaleString()} words</span>
                <span>Modified {lastModified.toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div className="bg-white border-b flex-shrink-0">
        <div className="flex">
          <button
            onClick={() => setWorkspaceTab('paper')}
            className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium transition-colors ${
              workspaceTab === 'paper'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText size={18} />
            <span>Paper Editor</span>
          </button>
          
          <button
            onClick={() => setWorkspaceTab('chat')}
            className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium transition-colors ${
              workspaceTab === 'chat'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <MessageSquare size={18} />
            <span>AI Assistant</span>
          </button>
          
          <button
            onClick={() => setWorkspaceTab('progress')}
            className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium transition-colors ${
              workspaceTab === 'progress'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <BarChart3 size={18} />
            <span>Progress</span>
          </button>
          
          <button
            onClick={() => setWorkspaceTab('ai-settings')}
            className={`flex items-center gap-2 px-6 py-3 border-b-2 font-medium transition-colors ${
              workspaceTab === 'ai-settings'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Settings size={18} />
            <span>AI Settings</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {workspaceTab === 'paper' && (
          <div className="h-full overflow-y-auto p-6 bg-gray-50">
            <CurrentPaperComponent />
          </div>
        )}
        
        {workspaceTab === 'chat' && (
          <div className="h-full overflow-hidden">
            {/* ✅ UPDATED: Pass navigation callback to chat component */}
            <ResearchChatPlatform 
              paperContext={activePaper}
              onNavigateToSettings={handleNavigateToAISettings}
            />
          </div>
        )}
        
        {workspaceTab === 'progress' && (
          <div className="h-full overflow-y-auto p-6 bg-gray-50">
            <ResearchProgressComponent paperId={activePaper.id} />
          </div>
        )}
        
        {workspaceTab === 'ai-settings' && (
          <div className="h-full overflow-y-auto p-6 bg-gray-50">
            <PaperAISettingsComponent paperId={activePaper.id} />
          </div>
        )}
      </div>
    </div>
  );
};

export default PaperWorkspace;