import React, { useState } from 'react';
import { ArrowLeft, FileText, MessageSquare, BarChart3, Settings } from 'lucide-react';
import { useGlobalContext } from '../App';
import CurrentPaperComponent from './CurrentPaperComponent';
import ResearchChatPlatform from './ResearchChatPlatform';
import ResearchProgressComponent from './ResearchProgressComponent';

const PaperWorkspace = () => {
  const { activePaper, setActivePaper } = useGlobalContext();
  const [workspaceTab, setWorkspaceTab] = useState<'paper' | 'chat' | 'progress'>('paper');

  if (!activePaper) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <FileText size={64} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No paper selected</h3>
          <p className="text-gray-600">Please select a paper to work on from the Papers Management section.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Workspace Header */}
      <div className="bg-white border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setActivePaper(null)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Back to Papers"
            >
              <ArrowLeft size={20} className="text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900 truncate max-w-96">
                {activePaper.title}
              </h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                <span className="capitalize">{activePaper.status.replace('-', ' ')}</span>
                <span>{activePaper.progress}% complete</span>
                <span>{activePaper.currentWordCount.toLocaleString()} words</span>
                <span>Modified {activePaper.lastModified.toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          {/* Paper-specific quick stats */}
          <div className="flex items-center gap-6 text-sm">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">{activePaper.progress}%</div>
              <div className="text-xs text-gray-500">Progress</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">
                {Math.round((activePaper.currentWordCount / activePaper.targetWordCount) * 100)}%
              </div>
              <div className="text-xs text-gray-500">Words</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">{activePaper.coAuthors.length}</div>
              <div className="text-xs text-gray-500">Authors</div>
            </div>
          </div>
        </div>
      </div>

      {/* Workspace Tabs */}
      <div className="bg-white border-b">
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
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {workspaceTab === 'paper' && (
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            <CurrentPaperComponent />
          </div>
        )}
        {workspaceTab === 'chat' && (
          <div className="flex-1 overflow-hidden">
            <ResearchChatPlatform paperContext={activePaper} />
          </div>
        )}
        {workspaceTab === 'progress' && (
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            <ResearchProgressComponent paperId={activePaper.id} />
          </div>
        )}
      </div>
    </div>
  );
};

export default PaperWorkspace;