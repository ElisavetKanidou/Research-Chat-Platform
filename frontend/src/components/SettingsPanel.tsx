// components/SettingsPanel.tsx  
import React, { useState } from 'react';
import { User, Bell, Database, Shield, Palette, Globe, Save, Eye, EyeOff } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';

interface UserSettings {
  personalInfo: {
    name: string;
    email: string;
    affiliation: string;
    researchInterests: string[];
    orcidId: string;
  };
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timezone: string;
    dateFormat: string;
    defaultWordCount: number;
  };
  aiPersonalization: {
    labLevel: number;
    personalLevel: number;
    globalLevel: number;
    writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
    researchFocus: string[];
  };
  notifications: {
    emailNotifications: boolean;
    deadlineReminders: boolean;
    collaborationUpdates: boolean;
    aiSuggestions: boolean;
    weeklyReports: boolean;
  };
  privacy: {
    profileVisibility: 'public' | 'private' | 'institution';
    shareAnalytics: boolean;
    dataSyncEnabled: boolean;
  };
  integrations: {
    googleDrive: boolean;
    dropbox: boolean;
    zotero: boolean;
    mendeley: boolean;
    latex: boolean;
  };
}

const SettingsPanel: React.FC = () => {
  const { user, theme, setTheme, settings, updateSettings, addNotification } = useGlobalContext();
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'ai' | 'notifications' | 'privacy' | 'integrations'>('profile');
  const [showPassword, setShowPassword] = useState(false);
  
  const [localSettings, setLocalSettings] = useState<UserSettings>({
    personalInfo: {
      name: user?.name || 'Dr. Jane Smith',
      email: user?.email || 'jane.smith@university.edu',
      affiliation: user?.personalInfo?.affiliation || 'University of Technology',
      researchInterests: user?.personalInfo?.researchInterests || ['Machine Learning', 'Natural Language Processing', 'Computer Vision'],
      orcidId: user?.personalInfo?.orcidId || '0000-0000-0000-0000'
    },
    preferences: {
      theme: theme || 'light',
      language: user?.preferences?.language || 'English',
      timezone: user?.preferences?.timezone || 'UTC-5 (EST)',
      dateFormat: user?.preferences?.dateFormat || 'MM/DD/YYYY',
      defaultWordCount: user?.preferences?.defaultWordCount || 8000
    },
    aiPersonalization: {
      labLevel: user?.preferences?.aiPersonalization?.labLevel || 7,
      personalLevel: user?.preferences?.aiPersonalization?.personalLevel || 8,
      globalLevel: user?.preferences?.aiPersonalization?.globalLevel || 5,
      writingStyle: user?.preferences?.aiPersonalization?.writingStyle || 'academic',
      researchFocus: user?.preferences?.aiPersonalization?.researchFocus || ['Machine Learning', 'Data Science']
    },
    notifications: {
      emailNotifications: user?.preferences?.notifications?.emailNotifications ?? true,
      deadlineReminders: user?.preferences?.notifications?.deadlineReminders ?? true,
      collaborationUpdates: user?.preferences?.notifications?.collaborationUpdates ?? true,
      aiSuggestions: user?.preferences?.notifications?.aiSuggestions ?? false,
      weeklyReports: user?.preferences?.notifications?.weeklyReports ?? true
    },
    privacy: {
      profileVisibility: user?.preferences?.privacy?.profileVisibility || 'institution',
      shareAnalytics: user?.preferences?.privacy?.shareAnalytics ?? true,
      dataSyncEnabled: user?.preferences?.privacy?.dataSyncEnabled ?? true
    },
    integrations: {
      googleDrive: true,
      dropbox: false,
      zotero: true,
      mendeley: false,
      latex: true
    }
  });

  const updateLocalSettings = (section: keyof UserSettings, field: string, value: any) => {
    setLocalSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const saveSettings = () => {
    console.log('Saving settings:', localSettings);
    
    // Update theme immediately
    if (localSettings.preferences.theme !== theme) {
      setTheme(localSettings.preferences.theme as 'light' | 'dark');
    }
    
    // Update global settings
    updateSettings({
      autoSave: settings.autoSave,
      defaultView: settings.defaultView,
      papersPerPage: settings.papersPerPage,
      showPreview: settings.showPreview,
      enableNotifications: localSettings.notifications.emailNotifications,
    });

    addNotification({
      type: 'success',
      title: 'Settings Saved',
      message: 'Your preferences have been updated successfully',
    });
  };

  const ProfileTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
            <input
              type="text"
              value={localSettings.personalInfo.name}
              onChange={(e) => updateLocalSettings('personalInfo', 'name', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input
              type="email"
              value={localSettings.personalInfo.email}
              onChange={(e) => updateLocalSettings('personalInfo', 'email', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Institution/Affiliation</label>
            <input
              type="text"
              value={localSettings.personalInfo.affiliation}
              onChange={(e) => updateLocalSettings('personalInfo', 'affiliation', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">ORCID ID</label>
            <input
              type="text"
              value={localSettings.personalInfo.orcidId}
              onChange={(e) => updateLocalSettings('personalInfo', 'orcidId', e.target.value)}
              placeholder="0000-0000-0000-0000"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Research Interests</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {localSettings.personalInfo.researchInterests.map((interest, index) => (
              <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1">
                {interest}
                <button
                  onClick={() => {
                    const newInterests = localSettings.personalInfo.researchInterests.filter((_, i) => i !== index);
                    updateLocalSettings('personalInfo', 'researchInterests', newInterests);
                  }}
                  className="text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            placeholder="Add research interest (press Enter)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const value = (e.target as HTMLInputElement).value.trim();
                if (value && !localSettings.personalInfo.researchInterests.includes(value)) {
                  updateLocalSettings('personalInfo', 'researchInterests', [...localSettings.personalInfo.researchInterests, value]);
                  (e.target as HTMLInputElement).value = '';
                }
              }
            }}
          />
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Security</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12"
                placeholder="Enter current password"
              />
              <button
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
            <input
              type="password"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter new password"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
            <input
              type="password"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Confirm new password"
            />
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Update Password
          </button>
        </div>
      </div>
    </div>
  );

  const PreferencesTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Display Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
            <select
              value={localSettings.preferences.theme}
              onChange={(e) => updateLocalSettings('preferences', 'theme', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select
              value={localSettings.preferences.language}
              onChange={(e) => updateLocalSettings('preferences', 'language', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="English">English</option>
              <option value="Spanish">Spanish</option>
              <option value="French">French</option>
              <option value="German">German</option>
              <option value="Chinese">Chinese</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
            <select
              value={localSettings.preferences.timezone}
              onChange={(e) => updateLocalSettings('preferences', 'timezone', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="UTC-5 (EST)">UTC-5 (EST)</option>
              <option value="UTC-8 (PST)">UTC-8 (PST)</option>
              <option value="UTC+0 (GMT)">UTC+0 (GMT)</option>
              <option value="UTC+1 (CET)">UTC+1 (CET)</option>
              <option value="UTC+8 (CST)">UTC+8 (CST)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Format</label>
            <select
              value={localSettings.preferences.dateFormat}
              onChange={(e) => updateLocalSettings('preferences', 'dateFormat', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Default Target Word Count</label>
          <input
            type="number"
            value={localSettings.preferences.defaultWordCount}
            onChange={(e) => updateLocalSettings('preferences', 'defaultWordCount', parseInt(e.target.value))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            min="1000"
            max="50000"
            step="500"
          />
          <p className="text-xs text-gray-500 mt-1">Default word count for new papers</p>
        </div>
      </div>
    </div>
  );

  const AITab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Personalization</h3>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lab Papers Influence: {localSettings.aiPersonalization.labLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={localSettings.aiPersonalization.labLevel}
              onChange={(e) => updateLocalSettings('aiPersonalization', 'labLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500">How much the AI considers your lab's research patterns</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Personal Papers Influence: {localSettings.aiPersonalization.personalLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={localSettings.aiPersonalization.personalLevel}
              onChange={(e) => updateLocalSettings('aiPersonalization', 'personalLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500">How much the AI adapts to your individual writing style</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Global Literature Influence: {localSettings.aiPersonalization.globalLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={localSettings.aiPersonalization.globalLevel}
              onChange={(e) => updateLocalSettings('aiPersonalization', 'globalLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500">How much the AI considers broader field trends</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Writing Style</label>
            <select
              value={localSettings.aiPersonalization.writingStyle}
              onChange={(e) => updateLocalSettings('aiPersonalization', 'writingStyle', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="academic">Academic - Formal and structured</option>
              <option value="concise">Concise - Brief and to the point</option>
              <option value="detailed">Detailed - Comprehensive and thorough</option>
              <option value="collaborative">Collaborative - Discussion-oriented</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Primary Research Focus Areas</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {localSettings.aiPersonalization.researchFocus.map((focus, index) => (
                <span key={index} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm flex items-center gap-1">
                  {focus}
                  <button
                    onClick={() => {
                      const newFocus = localSettings.aiPersonalization.researchFocus.filter((_, i) => i !== index);
                      updateLocalSettings('aiPersonalization', 'researchFocus', newFocus);
                    }}
                    className="text-purple-500 hover:text-purple-700"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              type="text"
              placeholder="Add research focus area (press Enter)"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const value = (e.target as HTMLInputElement).value.trim();
                  if (value && !localSettings.aiPersonalization.researchFocus.includes(value)) {
                    updateLocalSettings('aiPersonalization', 'researchFocus', [...localSettings.aiPersonalization.researchFocus, value]);
                    (e.target as HTMLInputElement).value = '';
                  }
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );

  const NotificationsTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          {Object.entries(localSettings.notifications).map(([key, value]) => {
            const labels = {
              emailNotifications: 'Email Notifications',
              deadlineReminders: 'Deadline Reminders',
              collaborationUpdates: 'Collaboration Updates',
              aiSuggestions: 'AI Suggestions',
              weeklyReports: 'Weekly Progress Reports'
            };
            const descriptions = {
              emailNotifications: 'Receive email notifications for important updates',
              deadlineReminders: 'Get reminded about upcoming deadlines',
              collaborationUpdates: 'Notifications when collaborators make changes',
              aiSuggestions: 'Receive AI-generated research suggestions',
              weeklyReports: 'Weekly summary of your research progress'
            };
            return (
              <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">{labels[key as keyof typeof labels]}</div>
                  <div className="text-sm text-gray-600">{descriptions[key as keyof typeof descriptions]}</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={value}
                    onChange={(e) => updateLocalSettings('notifications', key, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );

  const PrivacyTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Privacy Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Profile Visibility</label>
            <select
              value={localSettings.privacy.profileVisibility}
              onChange={(e) => updateLocalSettings('privacy', 'profileVisibility', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="public">Public - Visible to everyone</option>
              <option value="institution">Institution - Visible to institution members</option>
              <option value="private">Private - Only visible to you</option>
            </select>
          </div>
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <div className="font-medium text-gray-900">Share Analytics Data</div>
              <div className="text-sm text-gray-600">Help improve the platform by sharing anonymous usage data</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={localSettings.privacy.shareAnalytics}
                onChange={(e) => updateLocalSettings('privacy', 'shareAnalytics', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div>
              <div className="font-medium text-gray-900">Cloud Data Sync</div>
              <div className="text-sm text-gray-600">Sync your data across devices securely</div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={localSettings.privacy.dataSyncEnabled}
                onChange={(e) => updateLocalSettings('privacy', 'dataSyncEnabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Management</h3>
        <div className="space-y-3">
          <button className="w-full text-left p-3 border rounded-lg hover:bg-gray-50">
            <div className="font-medium text-gray-900">Export Your Data</div>
            <div className="text-sm text-gray-600">Download all your research data</div>
          </button>
          <button className="w-full text-left p-3 border rounded-lg hover:bg-red-50 text-red-600 border-red-200">
            <div className="font-medium">Delete Account</div>
            <div className="text-sm">Permanently delete your account and all data</div>
          </button>
        </div>
      </div>
    </div>
  );

  const IntegrationsTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">External Integrations</h3>
        <div className="space-y-4">
          {Object.entries(localSettings.integrations).map(([key, value]) => {
            const integrationInfo = {
              googleDrive: { name: 'Google Drive', desc: 'Sync papers with Google Drive' },
              dropbox: { name: 'Dropbox', desc: 'Backup papers to Dropbox' },
              zotero: { name: 'Zotero', desc: 'Import references from Zotero' },
              mendeley: { name: 'Mendeley', desc: 'Import references from Mendeley' },
              latex: { name: 'LaTeX Export', desc: 'Export papers in LaTeX format' }
            };
            const info = integrationInfo[key as keyof typeof integrationInfo];
            return (
              <div key={key} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    value ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    <div className={`w-6 h-6 rounded ${value ? 'bg-green-500' : 'bg-gray-400'}`} />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{info.name}</div>
                    <div className="text-sm text-gray-600">{info.desc}</div>
                  </div>
                </div>
                <button
                  onClick={() => updateLocalSettings('integrations', key, !value)}
                  className={`px-4 py-2 rounded-lg font-medium ${
                    value
                      ? 'bg-red-100 text-red-700 hover:bg-red-200'
                      : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                  }`}
                >
                  {value ? 'Disconnect' : 'Connect'}
                </button>
              </div>
            );
          })}
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">API Access</h3>
        <p className="text-sm text-gray-600 mb-4">
          Generate API keys to integrate ResearchHub with your custom tools and workflows.
        </p>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <div className="font-medium text-gray-900">Personal API Key</div>
              <div className="text-sm text-gray-600 font-mono">rh_••••••••••••••••••</div>
            </div>
            <button className="px-3 py-1 text-sm bg-gray-200 rounded hover:bg-gray-300">
              Regenerate
            </button>
          </div>
          <button className="w-full text-left p-3 border border-dashed border-gray-300 rounded-lg hover:bg-gray-50">
            <div className="text-center text-gray-500">
              + Create New API Key
            </div>
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Customize your ResearchHub experience</p>
          </div>
          <button
            onClick={saveSettings}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Save size={18} />
            Save Changes
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="flex overflow-x-auto">
            {[
              { id: 'profile', label: 'Profile', icon: User },
              { id: 'preferences', label: 'Preferences', icon: Palette },
              { id: 'ai', label: 'AI Settings', icon: Globe },
              { id: 'notifications', label: 'Notifications', icon: Bell },
              { id: 'privacy', label: 'Privacy', icon: Shield },
              { id: 'integrations', label: 'Integrations', icon: Database }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                <Icon size={18} />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'profile' && <ProfileTab />}
        {activeTab === 'preferences' && <PreferencesTab />}
        {activeTab === 'ai' && <AITab />}
        {activeTab === 'notifications' && <NotificationsTab />}
        {activeTab === 'privacy' && <PrivacyTab />}
        {activeTab === 'integrations' && <IntegrationsTab />}
      </div>
    </div>
  );
};

export default SettingsPanel;