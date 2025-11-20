// types/user.ts - COMPLETE VERSION
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  lastLoginAt: Date;
  
  personalInfo: {
    name: string;
    email: string;
    affiliation: string;
    researchInterests: string[];
    orcidId?: string;
  };
  
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timezone: string;
    dateFormat: string;
    defaultWordCount: number;
    autoSave: boolean;
    
    notifications: {
      emailNotifications: boolean;
      deadlineReminders: boolean;
      collaborationUpdates: boolean;
      aiSuggestions: boolean;
      weeklyReports: boolean;
      pushNotifications: boolean;
      reminderFrequency: 'daily' | 'weekly' | 'monthly';
    };
    
    privacy: {
      profileVisibility: 'public' | 'private' | 'institution';
      shareAnalytics: boolean;
      dataSyncEnabled: boolean;
      allowResearchSharing: boolean;
      trackingOptOut: boolean;
    };
    
    aiPersonalization: {
      labLevel: number;
      personalLevel: number;
      globalLevel: number;
      writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
      researchFocus: string[];
      suggestionsEnabled: boolean;
      contextDepth: 'minimal' | 'moderate' | 'comprehensive';
    };
    
    integrations?: {
      googleDrive: boolean;
      dropbox: boolean;
      zotero: boolean;
      mendeley: boolean;
      latex: boolean;
    };
  };
  
  subscription: {
    plan: 'free' | 'premium' | 'enterprise';
    status: 'active' | 'inactive' | 'trial' | 'expired';
    startDate: Date;
    endDate?: Date;
    features: string[];
  };
}

// User profile update DTO
export interface UserProfileUpdate {
  name?: string;
  affiliation?: string;
  orcidId?: string;
  researchInterests?: string[];
}

// User preferences update DTO
export interface UserPreferencesUpdate {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  timezone?: string;
  dateFormat?: string;
  defaultWordCount?: number;
  notifications?: Partial<User['preferences']['notifications']>;
  privacy?: Partial<User['preferences']['privacy']>;
  integrations?: Partial<User['preferences']['integrations']>;
}