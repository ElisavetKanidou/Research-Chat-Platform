import React, { useState } from 'react';
import { Send, Download, Settings, CheckCircle, XCircle } from 'lucide-react';

// Types
interface ChatAttachment {
  name: string;
  type: string;
  size: string;
  downloadUrl: string | null;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  needsConfirmation?: boolean;
  confirmed?: boolean;
  attachments?: ChatAttachment[];
}

interface PersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
}

const ResearchChatDemo: React.FC = () => {
  const [inputMessage, setInputMessage] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [personalization] = useState<PersonalizationSettings>({
    labLevel: 7,
    personalLevel: 8,
    globalLevel: 5
  });

  // Initialize messages with proper typing
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      type: 'assistant',
      content: `Welcome to ResearchChat-AI! I'm your personalized research assistant. I can help you develop research ideas, find related papers, identify gaps, and guide you through the entire paper writing process.

Current personalization settings:
- Lab papers influence: 7/10
- Your personal papers influence: 8/10  
- Global literature influence: 5/10

Currently working on: "Machine Learning in Healthcare: A Comprehensive Survey"

What research idea would you like to explore today?`,
      timestamp: new Date('2024-09-08T05:55:00'),
      needsConfirmation: false
    },
    {
      id: 'user1',
      type: 'user',
      content: 'I want to explore the integration of federated learning with electronic health records for privacy-preserving medical research',
      timestamp: new Date('2024-09-08T05:56:30')
    },
    {
      id: 'assistant1',
      type: 'assistant',
      content: `Excellent research direction! Federated learning with EHRs is a cutting-edge area that addresses critical privacy concerns in healthcare AI.

Based on your current survey on ML in healthcare, I can see strong connections. Here's my analysis:

**Key Research Opportunities:**
1. **Privacy-Preserving Architectures**: Developing novel federated learning protocols specifically for heterogeneous EHR data
2. **Cross-Institutional Collaboration**: Enabling multi-hospital research without data sharing
3. **Regulatory Compliance**: Ensuring HIPAA and GDPR compliance in federated medical AI

**Identified Gaps:**
- Limited work on handling missing data across federated EHR systems
- Insufficient research on federated learning with temporal medical data
- Need for standardized evaluation metrics across institutions

**Suggested Next Steps:**
1. Literature review on federated EHR systems (2020-2024)
2. Identify key technical challenges in data heterogeneity
3. Propose novel aggregation algorithms for medical data

Would you like me to generate a detailed research proposal outline and identify the top 20 most relevant papers in this area?`,
      timestamp: new Date('2024-09-08T05:57:15'),
      needsConfirmation: true,
      attachments: [
        {
          name: 'federated_learning_ehr_literature_review.pdf',
          type: 'pdf',
          size: '2.3 MB',
          downloadUrl: null
        },
        {
          name: 'research_proposal_outline.docx',
          type: 'document',
          size: '456 KB',
          downloadUrl: null
        }
      ]
    }
  ]);

  const handleConfirmation = (messageId: string, confirmed: boolean) => {
    setMessages((prevMessages: Message[]) =>
      prevMessages.map((msg: Message) =>
        msg.id === messageId
          ? { ...msg, confirmed, needsConfirmation: false }
          : msg
      )
    );

    // Add follow-up message
    setTimeout(() => {
      const followUpMessage: Message = {
        id: 'followup1',
        type: 'assistant',
        content: confirmed
          ? "Perfect! I'll start preparing the literature review and research proposal. Let me also search for recent conference papers from ICLR, NeurIPS, and ICML on this topic."
          : "No problem! Let me know what aspects you'd like me to adjust or approach differently. Would you prefer to focus more on the technical implementation or the clinical applications?",
        timestamp: new Date(),
        needsConfirmation: false
      };

      setMessages((prevMessages: Message[]) => [...prevMessages, followUpMessage]);
    }, 1000);
  };

  const downloadFile = (attachment: ChatAttachment) => {
    // Mock download for demo
    const blob = new Blob([`Mock ${attachment.type} file content for ${attachment.name}`], { 
      type: attachment.type === 'pdf' ? 'application/pdf' : 'text/plain' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = attachment.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const PersonalizationSettings: React.FC = () => (
    <div className="bg-white p-6 rounded-lg shadow-lg border">
      <h3 className="text-lg font-bold mb-6">Personalization Settings</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lab Papers Influence: {personalization.labLevel}/10
          </label>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={personalization.labLevel}
            readOnly
            className="w-full" 
          />
          <p className="text-xs text-gray-500">How much to consider your lab's research patterns</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Personal Papers Influence: {personalization.personalLevel}/10
          </label>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={personalization.personalLevel}
            readOnly
            className="w-full" 
          />
          <p className="text-xs text-gray-500">How much to adapt to your individual writing style</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Global Literature Influence: {personalization.globalLevel}/10
          </label>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={personalization.globalLevel}
            readOnly
            className="w-full" 
          />
          <p className="text-xs text-gray-500">How much to consider broader field trends</p>
        </div>
      </div>
      <button 
        onClick={() => setShowSettings(false)}
        className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
      >
        Apply Settings
      </button>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message: Message, index: number) => (
          <div key={message.id || index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-lg ${
              message.type === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white border shadow-sm'
            }`}>
              <div className="whitespace-pre-wrap text-sm">{message.content}</div>
              
              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-3 space-y-2">
                  {message.attachments.map((attachment: ChatAttachment, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-2">
                        <Download size={16} />
                        <span className="text-sm font-medium">{attachment.name}</span>
                        <span className="text-xs text-gray-500">({attachment.size})</span>
                      </div>
                      <button 
                        onClick={() => downloadFile(attachment)} 
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              {message.needsConfirmation && message.confirmed === undefined && (
                <div className="mt-3 flex gap-2">
                  <button 
                    onClick={() => handleConfirmation(message.id, true)} 
                    className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200"
                  >
                    <CheckCircle size={16} /> Yes, I agree
                  </button>
                  <button 
                    onClick={() => handleConfirmation(message.id, false)} 
                    className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm hover:bg-red-200"
                  >
                    <XCircle size={16} /> No, let's adjust
                  </button>
                </div>
              )}
              
              {message.confirmed !== undefined && (
                <div className="mt-2 flex items-center gap-1 text-sm">
                  {message.confirmed ? (
                    <><CheckCircle size={16} className="text-green-600" /> <span className="text-green-600">Confirmed</span></>
                  ) : (
                    <><XCircle size={16} className="text-red-600" /> <span className="text-red-600">Needs adjustment</span></>
                  )}
                </div>
              )}
              
              <div className="text-xs mt-2 opacity-70 text-right">
                {message.timestamp.toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="border-t bg-gray-50 p-4">
          <PersonalizationSettings />
        </div>
      )}

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center gap-2 mb-3">
          <div className="text-sm text-gray-600 bg-blue-50 px-2 py-1 rounded">
            Context: Machine Learning in Healthcare: A Comprehensive Survey
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`flex items-center gap-1 px-2 py-1 text-sm rounded ${
              showSettings ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Settings size={16} />
            Settings
          </button>
        </div>
        
        <div className="flex gap-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask about your research idea, request paper analysis, or ask me to find gaps..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResearchChatDemo;