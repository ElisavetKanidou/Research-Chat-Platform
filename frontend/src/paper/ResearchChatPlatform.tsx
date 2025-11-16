import React, { useState, useEffect, useRef } from 'react';
import { Send, Download, Settings, Loader, CheckCircle, XCircle, Plus, ChevronDown } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import type { Paper } from '../types/paper';
import type { ChatMessageRequest, ChatMessageResponse, ChatAttachment } from '../types/api';

// Section types matching backend
type SectionType = 
  | 'abstract' 
  | 'introduction' 
  | 'literature_review' 
  | 'methodology' 
  | 'results' 
  | 'discussion' 
  | 'conclusion';

interface SectionOption {
  value: SectionType;
  label: string;
  icon: string;
}

const SECTION_OPTIONS: SectionOption[] = [
  { value: 'abstract', label: 'Abstract', icon: '📝' },
  { value: 'introduction', label: 'Introduction', icon: '🚀' },
  { value: 'literature_review', label: 'Literature Review', icon: '📚' },
  { value: 'methodology', label: 'Methodology', icon: '🔬' },
  { value: 'results', label: 'Results', icon: '📊' },
  { value: 'discussion', label: 'Discussion', icon: '💬' },
  { value: 'conclusion', label: 'Conclusion', icon: '🎯' },
];

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  needsConfirmation?: boolean;
  confirmed?: boolean;
  attachments?: ChatAttachment[];
  canAddToSection?: boolean;
}

interface PersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
}

interface ResearchChatPlatformProps {
  paperContext?: Paper;
}

const API_URL = 'http://127.0.0.1:8000/api/v1';

const ResearchChatPlatform: React.FC<ResearchChatPlatformProps> = ({ paperContext }) => {
  const { papers, user, addNotification } = useGlobalContext();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [openAddMenu, setOpenAddMenu] = useState<string | null>(null);
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
        timestamp: new Date(),
        canAddToSection: false
      };
      setMessages([welcomeMessage]);
    }
  }, [personalization, paperContext]);

  const getAuthToken = (): string | null => {
    return localStorage.getItem('auth_token') || localStorage.getItem('token');
  };

  const getAuthHeaders = (): HeadersInit => {
    const token = getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);

    // Add user message immediately to UI
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      console.log('🚀 Sending message to AI...', messageContent);
      
      const requestBody = {
        content: messageContent,
        paper_context: paperContext ? {
          id: paperContext.id,
          title: paperContext.title,
          status: paperContext.status,
          progress: paperContext.progress,
          research_area: paperContext.researchArea || '',
          abstract: paperContext.abstract || '',
          co_authors: paperContext.coAuthors || [],
          current_word_count: paperContext.currentWordCount || 0,
          target_word_count: paperContext.targetWordCount || 0,
        } : null,
        personalization_settings: {
          lab_level: personalization.labLevel,
          personal_level: personalization.personalLevel,
          global_level: personalization.globalLevel,
        }
      };

      console.log('📤 Request body:', JSON.stringify(requestBody, null, 2));
      
      const response = await fetch(`${API_URL}/chat/message`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(requestBody),
      });

      console.log('📥 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ AI Response data:', JSON.stringify(data, null, 2));

      // Debug: Check what fields are in the response
      console.log('🔍 Response fields:', Object.keys(data));
      console.log('🔍 messageId:', data.messageId);
      console.log('🔍 responseContent:', data.responseContent);
      console.log('🔍 createdAt:', data.createdAt);

      // Create AI message with fallbacks for field names
      const aiMessage: Message = {
        id: data.messageId || data.message_id || `ai-${Date.now()}`,
        type: 'assistant',
        content: data.responseContent || data.response_content || data.content || 'No response content received',
        timestamp: new Date(),
        needsConfirmation: data.needsConfirmation || data.needs_confirmation || false,
        attachments: data.attachments || [],
        canAddToSection: true
      };

      console.log('💬 Adding AI message to UI:', aiMessage);

      // Add AI response to messages
      setMessages(prev => {
        console.log('📊 Current messages:', prev.length);
        const updated = [...prev, aiMessage];
        console.log('📊 Updated messages:', updated.length);
        return updated;
      });

    } catch (error) {
      console.error('❌ Error sending message:', error);
      
      // Show error message in chat
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to get AI response. Please try again.'}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      addNotification({
        type: 'error',
        title: 'Chat Error',
        message: error instanceof Error ? error.message : 'Failed to send message',
      });
      
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToSection = async (messageId: string, messageContent: string, sectionType: SectionType) => {
    if (!paperContext) {
      addNotification({
        type: 'error',
        title: 'No Paper Selected',
        message: 'Please select a paper before adding content to sections',
      });
      return;
    }

    const token = getAuthToken();
    if (!token) {
      addNotification({
        type: 'error',
        title: 'Authentication Required',
        message: 'Please log in to add content to sections',
      });
      return;
    }

    try {
      const response = await fetch(`${API_URL}/chat/add-to-section`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          message_id: messageId,
          paper_id: paperContext.id,
          section_type: sectionType,
          content: messageContent,
          append: true
        }),
      });

      if (response.status === 401) {
        addNotification({
          type: 'error',
          title: 'Authentication Failed',
          message: 'Your session has expired. Please log in again.',
        });
        return;
      }

      if (response.status === 403) {
        addNotification({
          type: 'error',
          title: 'Access Denied',
          message: 'You do not have permission to edit this paper.',
        });
        return;
      }

      if (response.status === 404) {
        addNotification({
          type: 'error',
          title: 'Not Found',
          message: 'Paper or section not found.',
        });
        return;
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const data = await response.json();

      addNotification({
        type: 'success',
        title: 'Content Added',
        message: `Successfully added to ${SECTION_OPTIONS.find(s => s.value === sectionType)?.label} (${data.wordCount} words)`,
        autoRemove: true,
      });

      setOpenAddMenu(null);

    } catch (error) {
      console.error('Error adding to section:', error);
      addNotification({
        type: 'error',
        title: 'Failed to Add Content',
        message: error instanceof Error ? error.message : 'Could not add content to section. Please try again.',
      });
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
      needsConfirmation: false,
      canAddToSection: false
    };

    setTimeout(() => {
      setMessages(prev => [...prev, followUpMessage]);
    }, 500);
  };

  const downloadFile = (attachment: ChatAttachment) => {
    if (attachment.downloadUrl) {
      window.open(attachment.downloadUrl, '_blank');
    } else {
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
              
              {/* Action Buttons Row */}
              {message.type === 'assistant' && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {/* Confirmation Buttons */}
                  {message.needsConfirmation && message.confirmed === undefined && (
                    <>
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
                    </>
                  )}
                  
                  {/* Add to Section Button */}
                  {message.canAddToSection && paperContext && (
                    <div className="relative">
                      <button
                        onClick={() => setOpenAddMenu(openAddMenu === message.id ? null : message.id)}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
                      >
                        <Plus size={16} /> Add to Section <ChevronDown size={14} />
                      </button>
                      
                      {/* Dropdown Menu */}
                      {openAddMenu === message.id && (
                        <div className="absolute z-10 mt-1 w-56 bg-white border rounded-lg shadow-lg">
                          {SECTION_OPTIONS.map((section) => (
                            <button
                              key={section.value}
                              onClick={() => handleAddToSection(message.id, message.content, section.value)}
                              className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center gap-2"
                            >
                              <span>{section.icon}</span>
                              <span>{section.label}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {/* Confirmation Status */}
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