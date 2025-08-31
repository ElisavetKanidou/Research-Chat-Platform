import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, Download, Settings, Loader, CheckCircle, XCircle, BarChart } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import type { Paper } from '../types/paper';
import type { ChatMessageRequest, ChatMessageResponse, ChatAttachment } from '../types/api';

// Interfaces for TypeScript type safety
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

interface ResearchChatPlatformProps {
  paperContext?: Paper;
}

// API Endpoint
const API_URL = 'http://127.0.0.1:8000/api/chat/message';

const ResearchChatPlatform: React.FC<ResearchChatPlatformProps> = ({ paperContext }) => {
  const { papers, user, addNotification } = useGlobalContext();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [personalization, setPersonalization] = useState<PersonalizationSettings>({
    labLevel: user?.preferences?.aiPersonalization?.labLevel || 7,
    personalLevel: user?.preferences?.aiPersonalization?.personalLevel || 8,
    globalLevel: user?.preferences?.aiPersonalization?.globalLevel || 5
  });
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'assistant',
        content: `Welcome to ResearchChat-AI! I'm your personalized research assistant. I can help you develop research ideas, find related papers, identify gaps, and guide you through the entire paper writing process.

Current personalization settings:
- Lab papers influence: ${personalization.labLevel}/10
- Your personal papers influence: ${personalization.personalLevel}/10  
- Global literature influence: ${personalization.globalLevel}/10

${paperContext ? `Currently working on: "${paperContext.title}"` : 'No active paper selected.'}

What research idea would you like to explore today?`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [personalization, paperContext]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const requestData: ChatMessageRequest = {
        content: currentInput,
        paperContext: paperContext ? {
          id: paperContext.id,
          title: paperContext.title,
          status: paperContext.status,
          progress: paperContext.progress,
          researchArea: paperContext.researchArea,
          abstract: paperContext.abstract,
          coAuthors: paperContext.coAuthors,
          currentWordCount: paperContext.currentWordCount,
          targetWordCount: paperContext.targetWordCount,
        } : undefined,
        userPapersContext: papers.map(p => ({
          id: p.id,
          title: p.title,
          researchArea: p.researchArea,
          status: p.status,
        })),
        personalizationSettings: {
          labLevel: personalization.labLevel,
          personalLevel: personalization.personalLevel,
          globalLevel: personalization.globalLevel,
          writingStyle: user?.preferences?.aiPersonalization?.writingStyle || 'academic',
          researchFocus: user?.preferences?.aiPersonalization?.researchFocus || [],
        },
      };

      // For development, use a mock user ID
      const FAKE_USER_ID = "123e4567-e89b-12d3-a456-426614174000";
      
      // Fix: Remove duplicate content property - use only requestData
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: FAKE_USER_ID,
          ...requestData,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ChatMessageResponse = await response.json();

      const assistantMessage: Message = {
        id: data.messageId,
        type: 'assistant',
        content: data.responseContent,
        timestamp: new Date(data.createdAt),
        needsConfirmation: data.needsConfirmation,
        attachments: data.attachments || []
      };
      
      setMessages(prev => [...prev, assistantMessage]);

      if (data.attachments && data.attachments.length > 0) {
        addNotification({
          type: 'info',
          title: 'Files Generated',
          message: `AI generated ${data.attachments.length} file(s) for download`,
        });
      }

    } catch (error) {
      console.error("Error fetching AI response:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I could not connect to the server. Please make sure the backend is running on http://127.0.0.1:8000',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);

      addNotification({
        type: 'error',
        title: 'Connection Error',
        message: 'Could not connect to AI service',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmation = (messageId: string, confirmed: boolean) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId
          ? { ...msg, confirmed, needsConfirmation: false }
          : msg
      )
    );

    const followUpMessage: Message = {
      id: Date.now().toString(),
      type: 'assistant',
      content: confirmed
        ? "Perfect! Let's continue building on this foundation. What would you like to explore next?"
        : "No problem! Let me know what you'd like me to adjust or approach differently.",
      timestamp: new Date(),
      needsConfirmation: false
    };

    setTimeout(() => {
      setMessages(prev => [...prev, followUpMessage]);
    }, 500);
  };

  const downloadFile = (attachment: ChatAttachment) => {
    console.log("Downloading:", attachment);
    
    if (attachment.downloadUrl) {
      // Use the actual download URL if available
      window.open(attachment.downloadUrl, '_blank');
    } else {
      // Fallback: create mock file for development
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
    }

    addNotification({
      type: 'success',
      title: 'Download Started',
      message: `Downloading ${attachment.name}`,
      autoRemove: true,
    });
  };

  const PersonalizationSettingsComponent = () => (
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
            onChange={(e) => setPersonalization(prev => ({ ...prev, labLevel: parseInt(e.target.value) }))}
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
            onChange={(e) => setPersonalization(prev => ({ ...prev, personalLevel: parseInt(e.target.value) }))}
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
            onChange={(e) => setPersonalization(prev => ({ ...prev, globalLevel: parseInt(e.target.value) }))}
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
        {messages.map((message, index) => (
          <div key={message.id || index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-lg ${
              message.type === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white border shadow-sm'
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {message.attachments && message.attachments.length > 0 && (
                <div className="mt-3 space-y-2">
                  {message.attachments.map((attachment, idx) => (
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
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm p-4 rounded-lg">
              <div className="flex items-center gap-2 text-gray-600">
                <Loader className="animate-spin" size={16} />
                <span>AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="border-t bg-gray-50 p-4">
          <PersonalizationSettingsComponent />
        </div>
      )}

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center gap-2 mb-3">
          {paperContext && (
            <div className="text-sm text-gray-600 bg-blue-50 px-2 py-1 rounded">
              Context: {paperContext.title}
            </div>
          )}
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
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            placeholder="Ask about your research idea, request paper analysis, or ask me to find gaps..."
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage} 
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResearchChatPlatform;