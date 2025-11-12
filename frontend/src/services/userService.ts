// services/userService.ts - FIXED PREFERENCES HANDLING
import { apiClient } from '../utils/apiHelpers';

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  affiliation?: string;
  orcidId?: string;
  researchInterests?: string[];
  bio?: string;
  website?: string;
  location?: string;
  avatarUrl?: string;
  isActive: boolean;
  isVerified: boolean;
  preferences?: {
    // Basic preferences
    theme?: 'light' | 'dark' | 'auto';
    language?: string;
    timezone?: string;
    dateFormat?: string;
    defaultWordCount?: number;
    autoSave?: boolean;
    
    // Nested preferences (if backend returns nested)
    notifications?: {
      emailNotifications?: boolean;
      deadlineReminders?: boolean;
      collaborationUpdates?: boolean;
      aiSuggestions?: boolean;
      weeklyReports?: boolean;
    };
    privacy?: {
      profileVisibility?: 'public' | 'private' | 'institution';
      shareAnalytics?: boolean;
      dataSyncEnabled?: boolean;
    };
    integrations?: {
      googleDrive?: boolean;
      dropbox?: boolean;
      zotero?: boolean;
      mendeley?: boolean;
      latex?: boolean;
    };
  };
  subscriptionPlan?: string;
  subscriptionStatus?: string;
  createdAt?: string;
  updatedAt?: string;
  lastLoginAt?: string;
}

export interface UserPreferences {
  theme?: 'light' | 'dark' | 'auto';
  language?: string;
  timezone?: string;
  dateFormat?: string;
  defaultWordCount?: number;
  autoSave?: boolean;
  notifications?: {
    emailNotifications?: boolean;
    deadlineReminders?: boolean;
    collaborationUpdates?: boolean;
    aiSuggestions?: boolean;
    weeklyReports?: boolean;
  };
  privacy?: {
    profileVisibility?: 'public' | 'private' | 'institution';
    shareAnalytics?: boolean;
    dataSyncEnabled?: boolean;
  };
  integrations?: {
    googleDrive?: boolean;
    dropbox?: boolean;
    zotero?: boolean;
    mendeley?: boolean;
    latex?: boolean;
  };
}

class UserService {
  private readonly basePath = '/users';

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<UserProfile> {
    try {
      console.log('📞 [userService.getCurrentUser] Fetching profile...');
      const response = await apiClient.get<UserProfile>(`${this.basePath}/me`);
      
      console.log('📥 [userService.getCurrentUser] Profile received');
      console.log('📊 Preferences keys:', response.preferences ? Object.keys(response.preferences) : 'none');
      
      // ✅ Ensure preferences structure exists with defaults
      if (!response.preferences) {
        response.preferences = {};
      }
      
      // ✅ Initialize nested objects if they don't exist
      if (!response.preferences.notifications) {
        response.preferences.notifications = {
          emailNotifications: true,
          deadlineReminders: true,
          collaborationUpdates: true,
          aiSuggestions: false,
          weeklyReports: true
        };
      }
      
      if (!response.preferences.privacy) {
        response.preferences.privacy = {
          profileVisibility: 'institution',
          shareAnalytics: true,
          dataSyncEnabled: true
        };
      }
      
      if (!response.preferences.integrations) {
        response.preferences.integrations = {
          googleDrive: false,
          dropbox: false,
          zotero: false,
          mendeley: false,
          latex: false
        };
      }
      
      console.log('✅ [userService.getCurrentUser] Profile with defaults ready');
      return response;
      
    } catch (error) {
      console.error('❌ Failed to fetch user profile:', error);
      throw error;
    }
  }

  /**
   * Update user profile (basic fields)
   */
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    try {
      console.log('📞 [userService.updateProfile] Updating profile...');
      console.log('📤 Updates:', updates);
      
      const response = await apiClient.patch<UserProfile>(`${this.basePath}/me`, updates);
      
      console.log('✅ [userService.updateProfile] Profile updated');
      return response;
      
    } catch (error) {
      console.error('❌ Failed to update profile:', error);
      throw error;
    }
  }

  /**
   * Update user preferences (theme, notifications, privacy, integrations)
   */
  async updatePreferences(preferences: UserPreferences): Promise<any> {
    try {
      console.log('📞 [userService.updatePreferences] Updating preferences...');
      console.log('📤 Preferences to update:', preferences);
      console.log('📤 Keys:', Object.keys(preferences));
      
      // Log nested objects
      if (preferences.notifications) {
        console.log('  📧 Notifications:', Object.keys(preferences.notifications));
      }
      if (preferences.privacy) {
        console.log('  🔒 Privacy:', Object.keys(preferences.privacy));
      }
      if (preferences.integrations) {
        console.log('  🔌 Integrations:', Object.keys(preferences.integrations));
      }
      
      const response = await apiClient.patch<any>(
        `${this.basePath}/me/preferences`,
        preferences
      );
      
      console.log('📥 [userService.updatePreferences] Response:', response);
      console.log('✅ [userService.updatePreferences] Preferences updated');
      
      return response;
      
    } catch (error) {
      console.error('❌ Failed to update preferences:', error);
      throw error;
    }
  }

  /**
   * Get user preferences
   */
  async getPreferences(): Promise<UserPreferences> {
    try {
      console.log('📞 [userService.getPreferences] Fetching preferences...');
      
      const response = await apiClient.get<{ preferences: UserPreferences }>(
        `${this.basePath}/me/preferences`
      );
      
      console.log('✅ [userService.getPreferences] Preferences received');
      return response.preferences;
      
    } catch (error) {
      console.error('❌ Failed to fetch preferences:', error);
      throw error;
    }
  }

  /**
   * Get user statistics
   */
  async getStatistics(): Promise<any> {
    try {
      const response = await apiClient.get(`${this.basePath}/me/stats`);
      return response;
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      throw error;
    }
  }

  /**
   * Export user data (GDPR)
   */
  async exportData(): Promise<any> {
    try {
      const response = await apiClient.post(`${this.basePath}/me/export-data`, {});
      return response;
    } catch (error) {
      console.error('Failed to export data:', error);
      throw error;
    }
  }

  /**
   * Update research interests
   */
  async updateResearchInterests(interests: string[]): Promise<any> {
    try {
      console.log('📞 [userService.updateResearchInterests] Updating interests...');
      console.log('📤 Interests:', interests);
      
      const response = await apiClient.patch(
        `${this.basePath}/me/research-interests`,
        interests
      );
      
      console.log('✅ [userService.updateResearchInterests] Updated');
      return response;
      
    } catch (error) {
      console.error('❌ Failed to update research interests:', error);
      throw error;
    }
  }
}

export const userService = new UserService();