// frontend/src/components/ResearchChatPlatform.tsx

import React, { useState, useEffect, useRef } from 'react';
import { Send, FileText, Download, Settings, Loader, CheckCircle, XCircle, BarChart } from 'lucide-react';
import axios from 'axios';
import CurrentPaperComponent from './CurrentPaperComponent';
import ResearchProgressComponent from './ResearchProgressComponent';

// Interfaces for TypeScript type safety
interface Attachment {
  type: 'excel' | 'pdf' | 'references';
  name: string;
  size: string;
  data?: any;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  needsConfirmation?: boolean;
  confirmed?: boolean;
  attachments?: Attachment[];
}

interface PersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
}

// API Endpoint
const API_URL = 'http://127.0.0.1:8000/api/chat/message';

const ResearchChatPlatform = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [personalization, setPersonalization] = useState<PersonalizationSettings>({
    labLevel: 7,
    personalLevel: 8,
    globalLevel: 5
  });
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [activeSection, setActiveSection] = useState<'chat' | 'paper' | 'progress'>('chat');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (activeSection === 'chat' && messages.length === 0) {
      const welcomeMessage: Message = {
        id: 'welcome',
        type: 'assistant',
        content: `Welcome to ResearchChat-AI! I'm your personalized research assistant. I can help you develop research ideas, find related papers, identify gaps, and guide you through the entire paper writing process.

Current personalization settings:
- Lab papers influence: ${personalization.labLevel}/10
- Your personal papers influence: ${personalization.personalLevel}/10  
- Global literature influence: ${personalization.globalLevel}/10

What research idea would you like to explore today?`,
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [activeSection, messages.length, personalization]);

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
      const FAKE_USER_ID = "123e4567-e89b-12d3-a456-426614174000";

      const response = await axios.post(API_URL, {
        content: currentInput,
        user_id: FAKE_USER_ID
      });

      const assistantMessage: Message = {
        id: response.data.message_id,
        type: 'assistant',
        content: response.data.response_content,
        timestamp: new Date(response.data.created_at),
        needsConfirmation: response.data.needs_confirmation,
        attachments: response.data.attachments || []
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error("Error fetching AI response:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I could not connect to the server. Please make sure it is running and check the console for errors.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
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

  const downloadFile = (attachment: Attachment) => {
    console.log("Downloading:", attachment);
    const blob = new Blob([`Mock ${attachment.type} file content for ${attachment.name}`], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = attachment.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const PersonalizationSettingsComponent = () => (
    <div className="bg-white p-6 rounded-lg shadow-lg border">
      <h3 className="text-lg font-bold mb-6">Personalization Settings</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lab Papers Influence: {personalization.labLevel}/10
          </label>
          <input type="range" min="1" max="10" value={personalization.labLevel}
            onChange={(e) => setPersonalization(prev => ({ ...prev, labLevel: parseInt(e.target.value) }))}
            className="w-full" />
          <p className="text-xs text-gray-500">How much to consider your lab's research patterns</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Personal Papers Influence: {personalization.personalLevel}/10
          </label>
          <input type="range" min="1" max="10" value={personalization.personalLevel}
            onChange={(e) => setPersonalization(prev => ({ ...prev, personalLevel: parseInt(e.target.value) }))}
            className="w-full" />
          <p className="text-xs text-gray-500">How much to adapt to your individual writing style</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Global Literature Influence: {personalization.globalLevel}/10
          </label>
          <input type="range" min="1" max="10" value={personalization.globalLevel}
            onChange={(e) => setPersonalization(prev => ({ ...prev, globalLevel: parseInt(e.target.value) }))}
            className="w-full" />
          <p className="text-xs text-gray-500">How much to consider broader field trends</p>
        </div>
      </div>
      <button onClick={() => setShowSettings(false)}
        className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700">
        Apply Settings
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <div className="w-80 bg-white shadow-lg p-6 flex flex-col">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-gray-900">ResearchChat-AI</h1>
          <p className="text-sm text-gray-600">Your Personalized Research Assistant</p>
        </div>
        <div className="space-y-4">
          <button
            onClick={() => setActiveSection('chat')}
            className={`w-full flex items-center gap-2 p-3 text-left rounded-lg transition-colors ${
              activeSection === 'chat' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
            }`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span>Chat</span>
          </button>
          <button
            onClick={() => setActiveSection('paper')}
            className={`w-full flex items-center gap-2 p-3 text-left rounded-lg transition-colors ${
              activeSection === 'paper' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
            }`}
          >
            <FileText size={20} /> <span>Current Paper</span>
          </button>
          <button
            onClick={() => setActiveSection('progress')}
            className={`w-full flex items-center gap-2 p-3 text-left rounded-lg transition-colors ${
              activeSection === 'progress' ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
            }`}
          >
            <BarChart size={20} /> <span>Research Progress</span>
          </button>
           <button onClick={() => setShowSettings(!showSettings)} className="w-full flex items-center gap-2 p-3 text-left hover:bg-gray-50 rounded-lg">
            <Settings size={20} /> <span>Personalization Settings</span>
          </button>
        </div>
        {showSettings && (
          <div className="mt-6">
            <PersonalizationSettingsComponent />
          </div>
        )}
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {activeSection === 'chat' && (
          <>
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message, index) => (
                <div key={message.id || index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-3xl p-4 rounded-lg ${message.type === 'user' ? 'bg-blue-600 text-white' : 'bg-white border shadow-sm'}`}>
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
                            <button onClick={() => downloadFile(attachment)} className="text-blue-600 hover:text-blue-800 text-sm">
                              Download
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                    {message.needsConfirmation && message.confirmed === undefined && (
                      <div className="mt-3 flex gap-2">
                        <button onClick={() => handleConfirmation(message.id, true)} className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200">
                          <CheckCircle size={16} /> Yes, I agree
                        </button>
                        <button onClick={() => handleConfirmation(message.id, false)} className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm hover:bg-red-200">
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
            <div className="border-t bg-white p-6">
              <div className="flex gap-4">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about your research idea, request paper analysis, or ask me to find gaps..."
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed">
                  <Send size={20} />
                </button>
              </div>
            </div>
          </>
        )}

        {activeSection === 'paper' && (
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            <CurrentPaperComponent />
          </div>
        )}

        {activeSection === 'progress' && (
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            <ResearchProgressComponent />
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchChatPlatform;