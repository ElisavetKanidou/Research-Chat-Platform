// paper/ResearchChatPlatform.tsx - UPDATED WITH TAB NAVIGATION
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
  userApproved?: boolean | null;
}

interface PersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
}

interface ResearchChatPlatformProps {
  paperContext?: Paper;
  onNavigateToSettings?: () => void; // ✅ NEW: Callback to navigate to settings tab
}

const API_URL = 'http://127.0.0.1:8000/api/v1';

const ResearchChatPlatform: React.FC<ResearchChatPlatformProps> = ({ 
  paperContext: paperContextProp,
  onNavigateToSettings // ✅ NEW: Receive callback from parent
}) => {
  const { papers, user, addNotification } = useGlobalContext();
  
  const [currentPaper, setCurrentPaper] = useState<Paper | undefined>(paperContextProp);
  
  useEffect(() => {
    if (paperContextProp) {
      setCurrentPaper(paperContextProp);
      console.log('📄 Using paper from prop:', paperContextProp.title);
      return;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    const paperIdFromUrl = urlParams.get('paperId');
    
    if (paperIdFromUrl && papers) {
      const paperFromUrl = papers.find(p => p.id === paperIdFromUrl);
      if (paperFromUrl) {
        setCurrentPaper(paperFromUrl);
        console.log('📄 Using paper from URL:', paperFromUrl.title);
        return;
      }
    }
    
    if (papers && papers.length > 0) {
      setCurrentPaper(papers[0]);
      console.log('📄 Using first available paper:', papers[0].title);
    }
  }, [paperContextProp, papers]);
  
  const paperContext = currentPaper;
  
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [openAddMenu, setOpenAddMenu] = useState<string | null>(null);
  const [personalization, setPersonalization] = useState<PersonalizationSettings>({
    labLevel: user?.preferences?.aiPersonalization?.labLevel || 7,
    personalLevel: user?.preferences?.aiPersonalization?.personalLevel || 8,
    globalLevel: user?.preferences?.aiPersonalization?.globalLevel || 5
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load chat history on mount and when paper changes
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const token = getAuthToken();
        if (!token) {
          setMessages([createWelcomeMessage()]);
          return;
        }

        console.log('📜 Loading chat history for paper:', paperContext?.id || 'all papers');
        
        setMessages([]);
        
        const response = await fetch(
          `${API_URL}/chat/history${paperContext ? `?paper_id=${paperContext.id}` : ''}`,
          {
            method: 'GET',
            headers: getAuthHeaders(),
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to load history: ${response.status}`);
        }

        const historyData = await response.json();
        console.log('✅ Chat history loaded:', historyData.length, 'messages for paper:', paperContext?.title);

        if (historyData.length === 0) {
          console.log('📭 No history found, showing welcome message');
          setMessages([createWelcomeMessage()]);
          return;
        }

        const loadedMessages: Message[] = historyData.map((msg: any) => ({
          id: msg.id || `msg-${Date.now()}-${Math.random()}`,
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content,
          timestamp: new Date(msg.created_at),
          needsConfirmation: false,
          userApproved: null,
          canAddToSection: msg.role === 'assistant',
        }));

        setMessages(loadedMessages);

      } catch (error) {
        console.error('❌ Error loading chat history:', error);
        setMessages([createWelcomeMessage()]);
      }
    };

    loadChatHistory();
  }, [paperContext?.id]);

  const createWelcomeMessage = (): Message => ({
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
    needsConfirmation: false,
    userApproved: null,
    canAddToSection: false
  });

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
          target_word_count: paperContext.targetWordCount || 8000,
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

      const aiMessage: Message = {
        id: data.messageId || data.message_id || `ai-${Date.now()}`,
        type: 'assistant',
        content: data.responseContent || data.response_content || data.content || 'No response content received',
        timestamp: new Date(),
        needsConfirmation: true,
        userApproved: null,
        attachments: data.attachments || [],
        canAddToSection: true
      };

      console.log('💬 Adding AI message to UI:', aiMessage);

      setMessages(prev => {
        console.log('📊 Current messages:', prev.length);
        const updated = [...prev, aiMessage];
        console.log('📊 Updated messages:', updated.length);
        return updated;
      });

    } catch (error) {
      console.error('❌ Error sending message:', error);
      
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

  const handleConfirmation = (messageId: string, approved: boolean) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId
          ? { ...msg, userApproved: approved }
          : msg
      )
    );

    const followUpMessage: Message = {
      id: `followup-${Date.now()}`,
      type: 'assistant',
      content: approved
        ? "Great! I'm glad this helped. You can add this to your paper using the 'Add to Section' button, or ask me anything else!"
        : "No problem! Let me know how I can adjust or improve this response.",
      timestamp: new Date(),
      needsConfirmation: false,
      userApproved: null,
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

  // ✅ NEW: Handle settings button click
  const handleSettingsClick = () => {
    if (onNavigateToSettings) {
      // If parent provided navigation callback, use it
      onNavigateToSettings();
    } else {
      // Fallback: show notification to guide user
      addNotification({
        type: 'info',
        title: 'AI Settings',
        message: 'Click the "AI Settings" tab above to configure personalization settings for this paper',
        autoRemove: true,
      });
    }
  };

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
                  {message.userApproved === null && (
                    <>
                      <button 
                        onClick={() => handleConfirmation(message.id, true)} 
                        className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200 transition-colors"
                      >
                        <CheckCircle size={16} /> Yes, helpful
                      </button>
                      <button 
                        onClick={() => handleConfirmation(message.id, false)} 
                        className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm hover:bg-red-200 transition-colors"
                      >
                        <XCircle size={16} /> No, adjust
                      </button>
                    </>
                  )}
                  
                  {/* Show status after user answered */}
                  {message.userApproved !== null && (
                    <div className="flex items-center gap-1 text-sm px-3 py-1 rounded-full bg-gray-50">
                      {message.userApproved ? (
                        <>
                          <CheckCircle size={16} className="text-green-600" />
                          <span className="text-green-600 font-medium">Marked as helpful</span>
                        </>
                      ) : (
                        <>
                          <XCircle size={16} className="text-orange-600" />
                          <span className="text-orange-600 font-medium">Needs adjustment</span>
                        </>
                      )}
                    </div>
                  )}
                  
                  {/* Add to Section Button */}
                  {message.canAddToSection && (
                    <div className="relative">
                      <button
                        onClick={() => {
                          if (!paperContext) {
                            addNotification({
                              type: 'warning',
                              title: 'No Paper Selected',
                              message: 'Please select or create a paper first to add content to sections.',
                            });
                            return;
                          }
                          setOpenAddMenu(openAddMenu === message.id ? null : message.id);
                        }}
                        className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm transition-colors ${
                          paperContext 
                            ? 'bg-blue-100 text-blue-700 hover:bg-blue-200' 
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                        }`}
                        title={!paperContext ? 'Select a paper first' : 'Add this content to a paper section'}
                      >
                        <Plus size={16} /> Add to Section <ChevronDown size={14} />
                      </button>
                      
                      {/* Dropdown Menu */}
                      {openAddMenu === message.id && paperContext && (
                        <div className="absolute z-10 mt-1 w-56 bg-white border rounded-lg shadow-lg">
                          {SECTION_OPTIONS.map((section) => (
                            <button
                              key={section.value}
                              onClick={() => handleAddToSection(message.id, message.content, section.value)}
                              className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 flex items-center gap-2 border-b last:border-b-0"
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

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center gap-2 mb-3">
          {paperContext && (
            <div className="text-sm text-gray-600 bg-blue-50 px-2 py-1 rounded">
              Context: {paperContext.title}
            </div>
          )}
          {/* ✅ UPDATED: Settings button now navigates to AI Settings tab */}
          <button
            onClick={handleSettingsClick}
            className="flex items-center gap-1 px-2 py-1 text-sm rounded text-gray-600 hover:bg-gray-100 transition-colors"
            title="Open AI Settings tab"
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