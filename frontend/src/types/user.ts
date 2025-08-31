// types/user.ts

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: Date;
  lastLoginAt: Date;
  isActive: boolean;
  personalInfo: PersonalInfo;
  preferences: UserPreferences;
  subscription: UserSubscription;
}

export interface PersonalInfo {
  name: string;
  email: string;
  affiliation: string;
  researchInterests: string[];
  orcidId?: string;
  bio?: string;
  website?: string;
  location?: string;
  // Removed duplicate timezone - it belongs in UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  dateFormat: string;
  defaultWordCount: number;
  autoSave: boolean;
  notifications: NotificationPreferences;
  privacy: PrivacySettings;
  aiPersonalization: AIPersonalizationSettings;
}

export interface NotificationPreferences {
  emailNotifications: boolean;
  deadlineReminders: boolean;
  collaborationUpdates: boolean;
  aiSuggestions: boolean;
  weeklyReports: boolean;
  pushNotifications: boolean;
  reminderFrequency: 'daily' | 'weekly' | 'monthly';
}

export interface PrivacySettings {
  profileVisibility: 'public' | 'private' | 'institution';
  shareAnalytics: boolean;
  dataSyncEnabled: boolean;
  allowResearchSharing: boolean;
  trackingOptOut: boolean;
}

export interface AIPersonalizationSettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
  writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
  researchFocus: string[];
  suggestionsEnabled: boolean;
  contextDepth: 'minimal' | 'moderate' | 'comprehensive';
}

export interface UserSubscription {
  plan: 'free' | 'pro' | 'academic' | 'enterprise';
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  startDate: Date;
  endDate?: Date;
  features: SubscriptionFeature[];
}

export interface SubscriptionFeature {
  name: string;
  enabled: boolean;
  limit?: number;
  used?: number;
}

export interface UserSession {
  userId: string;
  sessionId: string;
  createdAt: Date;
  lastActivity: Date;
  ipAddress?: string;
  userAgent?: string;
}

export interface UserAnalytics {
  userId: string;
  totalPapers: number;
  publishedPapers: number;
  totalWords: number;
  collaborators: number;
  researchAreas: string[];
  avgCompletionTime: number;
  productivityScore: number;
  lastUpdated: Date;
}

export interface UserIntegration {
  id: string;
  userId: string;
  service: 'google_drive' | 'dropbox' | 'zotero' | 'mendeley' | 'latex' | 'orcid';
  isConnected: boolean;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: Date;
  lastSync?: Date;
  settings?: Record<string, any>;
}

export interface APIKey {
  id: string;
  userId: string;
  name: string;
  key: string;
  permissions: APIPermission[];
  createdAt: Date;
  lastUsed?: Date;
  isActive: boolean;
  expiresAt?: Date;
}

export interface APIPermission {
  resource: 'papers' | 'analytics' | 'chat' | 'all';
  actions: ('read' | 'write' | 'delete')[];
}

export interface UserActivity {
  id: string;
  userId: string;
  action: string;
  resource: string;
  resourceId: string;
  metadata?: Record<string, any>;
  timestamp: Date;
  ipAddress?: string;
}

export interface UserCollaboration {
  userId: string;
  collaboratorId: string;
  relationship: 'colleague' | 'mentor' | 'student' | 'co_author';
  sharedPapers: string[];
  createdAt: Date;
}

export type Theme = UserPreferences['theme'];
export type Language = UserPreferences['language'];
export type WritingStyle = AIPersonalizationSettings['writingStyle'];
export type SubscriptionPlan = UserSubscription['plan'];