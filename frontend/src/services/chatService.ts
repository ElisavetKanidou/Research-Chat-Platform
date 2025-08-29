// services/chatService.ts

import { Paper } from '../types/paper';

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  needsConfirmation?: boolean;
  confirmed?: boolean;
  attachments?: ChatAttachment[];
  paperContext?: string;
}

export interface ChatAttachment {
  type: 'excel' | 'pdf' | 'references' | 'data' | 'image';
  name: string;
  size: string;
  url?: string;
  data?: any;
}

export interface PersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
  writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
  researchFocus: string[];
}

export interface ChatRequest {
  content: string;
  userId: string;
  paperContext?: {
    id: string;
    title: string;
    status: string;
    progress: number;
    researchArea: string;
    abstract: string;
    coAuthors: string[];
    currentWordCount: number;
    targetWordCount: number;
  };
  userPapersContext?: Array<{
    id: string;
    title: string;
    researchArea: string;
    status: string;
  }>;
  personalizationSettings: PersonalizationSettings;
  conversationHistory?: ChatMessage[];
}

export interface ChatResponse {
  messageId: string;
  responseContent: string;
  needsConfirmation: boolean;
  attachments: ChatAttachment[];
  suggestions: string[];
  createdAt: string;
  metadata?: {
    sources?: string[];
    confidence?: number;
    reasoningSteps?: string[];
  };
}

class ChatService {
  private readonly apiUrl = 'http://127.0.0.1:8000/api/chat';
  private conversationHistory: Map<string, ChatMessage[]> = new Map();

  // Send message to AI assistant
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.apiUrl}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({
          ...request,
          conversationHistory: this.getConversationHistory(request.userId, request.paperContext?.id),
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat API error: ${response.status} ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      
      // Store conversation history
      this.addToConversationHistory(
        request.userId,
        request.paperContext?.id,
        {
          id: Date.now().toString(),
          type: 'user',
          content: request.content,
          timestamp: new Date(),
          paperContext: request.paperContext?.title,
        },
        {
          id: data.messageId,
          type: 'assistant',
          content: data.responseContent,
          timestamp: new Date(data.createdAt),
          needsConfirmation: data.needsConfirmation,
          attachments: data.attachments,
          paperContext: request.paperContext?.title,
        }
      );

      return data;
    } catch (error) {
      console.error('Chat service error:', error);
      
      // Fallback response for offline/error scenarios
      return this.getFallbackResponse(request);
    }
  }

  // Get conversation history for user/paper context
  getConversationHistory(userId: string, paperId?: string): ChatMessage[] {
    const key = paperId ? `${userId}-${paperId}` : userId;
    return this.conversationHistory.get(key) || [];
  }

  // Add messages to conversation history
  private addToConversationHistory(
    userId: string,
    paperId: string | undefined,
    userMessage: ChatMessage,
    assistantMessage: ChatMessage
  ): void {
    const key = paperId ? `${userId}-${paperId}` : userId;
    const history = this.conversationHistory.get(key) || [];
    
    history.push(userMessage, assistantMessage);
    
    // Keep only last 50 messages to prevent memory issues
    if (history.length > 50) {
      history.splice(0, history.length - 50);
    }
    
    this.conversationHistory.set(key, history);
    
    // Also save to localStorage for persistence
    this.saveConversationToStorage(key, history);
  }

  // Clear conversation history
  clearConversationHistory(userId: string, paperId?: string): void {
    const key = paperId ? `${userId}-${paperId}` : userId;
    this.conversationHistory.delete(key);
    localStorage.removeItem(`chat_history_${key}`);
  }

  // Get chat suggestions based on paper context
  async getChatSuggestions(paperContext?: Paper): Promise<string[]> {
    const defaultSuggestions = [
      "Help me brainstorm research questions for this paper",
      "What are the current trends in this research area?",
      "Suggest improvements for my abstract",
      "Find potential collaboration opportunities",
      "Help me identify research gaps",
    ];

    if (!paperContext) return defaultSuggestions;

    const contextSuggestions = [
      `Help me improve the methodology section for "${paperContext.title}"`,
      `What are recent papers similar to my work in ${paperContext.researchArea}?`,
      `Suggest citations for my literature review on ${paperContext.researchArea}`,
      `Help me structure the results section better`,
      `Review my abstract and suggest improvements`,
    ];

    return contextSuggestions;
  }

  // Update personalization settings
  async updatePersonalizationSettings(
    userId: string,
    settings: PersonalizationSettings
  ): Promise<void> {
    try {
      await fetch(`${this.apiUrl}/personalization`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({ userId, settings }),
      });
    } catch (error) {
      console.error('Failed to update personalization settings:', error);
      // Store locally as fallback
      localStorage.setItem(`personalization_${userId}`, JSON.stringify(settings));
    }
  }

  // Get research insights for a paper
  async getResearchInsights(paperId: string): Promise<{
    gaps: string[];
    suggestions: string[];
    relatedPapers: string[];
    methodologyTips: string[];
  }> {
    try {
      const response = await fetch(`${this.apiUrl}/insights/${paperId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Insights API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting research insights:', error);
      return this.getFallbackInsights();
    }
  }

  // Generate paper outline
  async generatePaperOutline(
    title: string,
    researchArea: string,
    abstract?: string
  ): Promise<{
    sections: Array<{ title: string; description: string; estimatedWords: number }>;
    timeline: Array<{ phase: string; duration: string; description: string }>;
  }> {
    try {
      const response = await fetch(`${this.apiUrl}/generate-outline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify({ title, researchArea, abstract }),
      });

      if (!response.ok) {
        throw new Error(`Outline generation error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating outline:', error);
      return this.getFallbackOutline();
    }
  }

  // Export conversation history
  exportConversationHistory(userId: string, paperId?: string, format: 'json' | 'txt' = 'json'): string {
    const history = this.getConversationHistory(userId, paperId);
    
    if (format === 'txt') {
      return history
        .map(msg => `[${msg.timestamp.toISOString()}] ${msg.type.toUpperCase()}: ${msg.content}`)
        .join('\n\n');
    }
    
    return JSON.stringify(history, null, 2);
  }

  // Private helper methods
  private getFallbackResponse(request: ChatRequest): ChatResponse {
    const responses = [
      "I understand you're working on your research. While I can't connect to the server right now, I'd suggest focusing on your current section and we can discuss it when the connection is restored.",
      "It looks like there's a connectivity issue. In the meantime, you might want to review your recent progress and outline next steps for your paper.",
      "I'm having trouble connecting to provide personalized assistance. Consider working on your literature review or methodology section while we resolve this.",
    ];

    return {
      messageId: Date.now().toString(),
      responseContent: responses[Math.floor(Math.random() * responses.length)],
      needsConfirmation: false,
      attachments: [],
      suggestions: [
        "Review your current progress",
        "Work on the next section",
        "Update your references",
      ],
      createdAt: new Date().toISOString(),
    };
  }

  private getFallbackInsights() {
    return {
      gaps: [
        "Consider exploring recent methodological advances in your field",
        "Look into cross-disciplinary applications of your research",
        "Investigate long-term implications of your findings",
      ],
      suggestions: [
        "Strengthen your literature review with more recent papers",
        "Consider adding a limitations section",
        "Include more visual representations of your data",
      ],
      relatedPapers: [
        "Search for recent publications in your research area",
        "Look for systematic reviews in related fields",
        "Check citation patterns of key papers in your bibliography",
      ],
      methodologyTips: [
        "Ensure your sample size is adequately justified",
        "Consider potential confounding variables",
        "Include validity and reliability measures",
      ],
    };
  }

  private getFallbackOutline() {
    return {
      sections: [
        { title: "Introduction", description: "Background, problem statement, and objectives", estimatedWords: 1000 },
        { title: "Literature Review", description: "Critical analysis of existing research", estimatedWords: 1500 },
        { title: "Methodology", description: "Research design and data collection methods", estimatedWords: 1200 },
        { title: "Results", description: "Presentation of findings", estimatedWords: 1500 },
        { title: "Discussion", description: "Interpretation and implications", estimatedWords: 1300 },
        { title: "Conclusion", description: "Summary and future directions", estimatedWords: 500 },
      ],
      timeline: [
        { phase: "Planning", duration: "2 weeks", description: "Literature review and methodology design" },
        { phase: "Data Collection", duration: "4 weeks", description: "Gather and validate research data" },
        { phase: "Analysis", duration: "3 weeks", description: "Process data and generate results" },
        { phase: "Writing", duration: "4 weeks", description: "Draft and revise manuscript" },
        { phase: "Review", duration: "2 weeks", description: "Final review and submission preparation" },
      ],
    };
  }

  private saveConversationToStorage(key: string, history: ChatMessage[]): void {
    try {
      localStorage.setItem(`chat_history_${key}`, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving conversation to storage:', error);
    }
  }

  private loadConversationFromStorage(key: string): ChatMessage[] {
    try {
      const stored = localStorage.getItem(`chat_history_${key}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
      }
    } catch (error) {
      console.error('Error loading conversation from storage:', error);
    }
    return [];
  }

  private getAuthToken(): string {
    return localStorage.getItem('auth_token') || 'fake-token';
  }

  // Initialize conversation history from storage
  initializeFromStorage(userId: string): void {
    const userKeys = Object.keys(localStorage).filter(key => 
      key.startsWith('chat_history_') && key.includes(userId)
    );

    userKeys.forEach(storageKey => {
      const key = storageKey.replace('chat_history_', '');
      const history = this.loadConversationFromStorage(key);
      if (history.length > 0) {
        this.conversationHistory.set(key, history);
      }
    });
  }
}

export const chatService = new ChatService();