// components/SettingsPanel.tsx - COMPLETE WITH PASSWORD FIX
import React, { useState, useEffect, useRef } from 'react';
import { User, Bell, Database, Shield, Palette, Save, Eye, EyeOff, Loader } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import { userService } from '../services/userService';
import { authService } from '../services/authService';

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

// ✅ Separate memoized component for password section
const PasswordSection: React.FC<{
  showPassword: boolean;
  setShowPassword: (show: boolean) => void;
  onChangePassword: (current: string, newPass: string, confirm: string) => Promise<void>;
  changingPassword: boolean;
}> = React.memo(({ showPassword, setShowPassword, onChangePassword, changingPassword }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = async () => {
    await onChangePassword(currentPassword, newPassword, confirmPassword);
    // Clear fields after successful change
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Security</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-12"
              placeholder="Enter current password"
            />
            <button
              type="button"
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
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter new password"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Confirm Password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Confirm new password"
          />
        </div>
        <button
          onClick={handleSubmit}
          disabled={changingPassword}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {changingPassword ? (
            <>
              <Loader className="animate-spin" size={18} />
              Updating Password...
            </>
          ) : (
            'Update Password'
          )}
        </button>
      </div>
    </div>
  );
});

PasswordSection.displayName = 'PasswordSection';

const SettingsPanel: React.FC = () => {
  const { theme, setTheme, settings, updateSettings, addNotification } = useGlobalContext();
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'notifications' | 'privacy' | 'integrations'>('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const hasLoadedRef = useRef(false);
  
  const [localSettings, setLocalSettings] = useState<UserSettings>({
    personalInfo: {
      name: '',
      email: '',
      affiliation: '',
      researchInterests: [],
      orcidId: ''
    },
    preferences: {
      theme: 'light',
      language: 'English',
      timezone: 'UTC-5 (EST)',
      dateFormat: 'MM/DD/YYYY',
      defaultWordCount: 8000
    },
    notifications: {
      emailNotifications: true,
      deadlineReminders: true,
      collaborationUpdates: true,
      aiSuggestions: false,
      weeklyReports: true
    },
    privacy: {
      profileVisibility: 'institution',
      shareAnalytics: true,
      dataSyncEnabled: true
    },
    integrations: {
      googleDrive: false,
      dropbox: false,
      zotero: false,
      mendeley: false,
      latex: false
    }
  });

  // Load profile ONCE
  useEffect(() => {
    if (hasLoadedRef.current) return;
    
    const loadProfile = async () => {
      try {
        setLoading(true);
        const profile = await userService.getCurrentUser();
        
        setLocalSettings({
          personalInfo: {
            name: profile.name || '',
            email: profile.email || '',
            affiliation: profile.affiliation || '',
            researchInterests: profile.researchInterests || [],
            orcidId: profile.orcidId || ''
          },
          preferences: {
            theme: (profile.preferences?.theme || 'light') as any,
            language: profile.preferences?.language || 'English',
            timezone: profile.preferences?.timezone || 'UTC-5 (EST)',
            dateFormat: profile.preferences?.dateFormat || 'MM/DD/YYYY',
            defaultWordCount: profile.preferences?.defaultWordCount || 8000
          },
          notifications: {
            emailNotifications: profile.preferences?.notifications?.emailNotifications ?? true,
            deadlineReminders: profile.preferences?.notifications?.deadlineReminders ?? true,
            collaborationUpdates: profile.preferences?.notifications?.collaborationUpdates ?? true,
            aiSuggestions: profile.preferences?.notifications?.aiSuggestions ?? false,
            weeklyReports: profile.preferences?.notifications?.weeklyReports ?? true
          },
          privacy: {
            profileVisibility: (profile.preferences?.privacy?.profileVisibility || 'institution') as any,
            shareAnalytics: profile.preferences?.privacy?.shareAnalytics ?? true,
            dataSyncEnabled: profile.preferences?.privacy?.dataSyncEnabled ?? true
          },
          integrations: {
            googleDrive: profile.preferences?.integrations?.googleDrive ?? false,
            dropbox: profile.preferences?.integrations?.dropbox ?? false,
            zotero: profile.preferences?.integrations?.zotero ?? false,
            mendeley: profile.preferences?.integrations?.mendeley ?? false,
            latex: profile.preferences?.integrations?.latex ?? false
          }
        });
        
        hasLoadedRef.current = true;
      } catch (error) {
        console.error('Failed to load profile:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, []);

  const saveSettings = async () => {
    try {
      setSaving(true);
      console.log('💾 Saving settings...');
      
      // Save profile info
      await userService.updateProfile({
        name: localSettings.personalInfo.name,
        affiliation: localSettings.personalInfo.affiliation,
        orcidId: localSettings.personalInfo.orcidId,
        researchInterests: localSettings.personalInfo.researchInterests,
      });

      // Save ALL preferences
      const preferencesPayload = {
        theme: localSettings.preferences.theme,
        language: localSettings.preferences.language,
        timezone: localSettings.preferences.timezone,
        dateFormat: localSettings.preferences.dateFormat,
        defaultWordCount: localSettings.preferences.defaultWordCount,
        notifications: localSettings.notifications,
        privacy: localSettings.privacy,
        integrations: localSettings.integrations,
      };

      await userService.updatePreferences(preferencesPayload);

      if (localSettings.preferences.theme !== theme) {
        setTheme(localSettings.preferences.theme as any);
      }
      
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
    } catch (error) {
      console.error('Failed to save settings:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to save settings',
      });
    } finally {
      setSaving(false);
    }
  };

  // ✅ Password change handler
  const handleChangePassword = async (currentPassword: string, newPassword: string, confirmPassword: string) => {
    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Please fill in all password fields',
      });
      throw new Error('Missing fields');
    }

    if (newPassword !== confirmPassword) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'New passwords do not match',
      });
      throw new Error('Passwords do not match');
    }

    if (newPassword.length < 8) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Password must be at least 8 characters',
      });
      throw new Error('Password too short');
    }

    try {
      setChangingPassword(true);
      console.log('🔒 Changing password...');
      
      await authService.changePassword(currentPassword, newPassword);

      addNotification({
        type: 'success',
        title: 'Password Changed',
        message: 'Your password has been changed successfully',
      });
      
      console.log('✅ Password changed successfully');
    } catch (error: any) {
      console.error('Failed to change password:', error);
      
      // Handle specific error messages from backend
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to change password';
      
      addNotification({
        type: 'error',
        title: 'Password Change Failed',
        message: errorMessage,
      });
      
      throw error;
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  const ProfileTab = () => {
    // ✅ Local state for input fields to avoid re-renders
    const [nameInput, setNameInput] = useState(localSettings.personalInfo.name);
    const [affiliationInput, setAffiliationInput] = useState(localSettings.personalInfo.affiliation);
    const [orcidInput, setOrcidInput] = useState(localSettings.personalInfo.orcidId);

    // Update parent state only on blur
    const handleNameBlur = () => {
      setLocalSettings(prev => ({
        ...prev,
        personalInfo: { ...prev.personalInfo, name: nameInput }
      }));
    };

    const handleAffiliationBlur = () => {
      setLocalSettings(prev => ({
        ...prev,
        personalInfo: { ...prev.personalInfo, affiliation: affiliationInput }
      }));
    };

    const handleOrcidBlur = () => {
      setLocalSettings(prev => ({
        ...prev,
        personalInfo: { ...prev.personalInfo, orcidId: orcidInput }
      }));
    };

    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
                onBlur={handleNameBlur}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                value={localSettings.personalInfo.email}
                disabled
                className="w-full p-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Institution/Affiliation</label>
              <input
                type="text"
                value={affiliationInput}
                onChange={(e) => setAffiliationInput(e.target.value)}
                onBlur={handleAffiliationBlur}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">ORCID ID</label>
              <input
                type="text"
                value={orcidInput}
                onChange={(e) => setOrcidInput(e.target.value)}
                onBlur={handleOrcidBlur}
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
                      setLocalSettings(prev => ({
                        ...prev,
                        personalInfo: { ...prev.personalInfo, researchInterests: newInterests }
                      }));
                    }}
                    className="text-blue-500 hover:text-blue-700 font-bold"
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
                    setLocalSettings(prev => ({
                      ...prev,
                      personalInfo: {
                        ...prev.personalInfo,
                        researchInterests: [...prev.personalInfo.researchInterests, value]
                      }
                    }));
                    (e.target as HTMLInputElement).value = '';
                  }
                }
              }}
            />
          </div>
        </div>

        {/* ✅ Password section as separate component */}
        <PasswordSection
          showPassword={showPassword}
          setShowPassword={setShowPassword}
          onChangePassword={handleChangePassword}
          changingPassword={changingPassword}
        />
      </div>
    );
  };

  const PreferencesTab = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Display Preferences</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
            <select
              value={localSettings.preferences.theme}
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                preferences: { ...prev.preferences, theme: e.target.value as any }
              }))}
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
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                preferences: { ...prev.preferences, language: e.target.value }
              }))}
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
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                preferences: { ...prev.preferences, timezone: e.target.value }
              }))}
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
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                preferences: { ...prev.preferences, dateFormat: e.target.value }
              }))}
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
            onChange={(e) => setLocalSettings(prev => ({
              ...prev,
              preferences: { ...prev.preferences, defaultWordCount: parseInt(e.target.value) }
            }))}
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
                    onChange={(e) => setLocalSettings(prev => ({
                      ...prev,
                      notifications: { ...prev.notifications, [key]: e.target.checked }
                    }))}
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
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                privacy: { ...prev.privacy, profileVisibility: e.target.value as any }
              }))}
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
                onChange={(e) => setLocalSettings(prev => ({
                  ...prev,
                  privacy: { ...prev.privacy, shareAnalytics: e.target.checked }
                }))}
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
                onChange={(e) => setLocalSettings(prev => ({
                  ...prev,
                  privacy: { ...prev.privacy, dataSyncEnabled: e.target.checked }
                }))}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
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
                  onClick={() => setLocalSettings(prev => ({
                    ...prev,
                    integrations: { ...prev.integrations, [key]: !value }
                  }))}
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
    </div>
  );

  return (
    <div className="h-full overflow-hidden flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-gray-600">Customize your ResearchHub experience</p>
          </div>
          <button
            onClick={saveSettings}
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border mb-6">
          <div className="flex overflow-x-auto">
            {[
              { id: 'profile', label: 'Profile', icon: User },
              { id: 'preferences', label: 'Preferences', icon: Palette },
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

        {activeTab === 'profile' && <ProfileTab />}
        {activeTab === 'preferences' && <PreferencesTab />}
        {activeTab === 'notifications' && <NotificationsTab />}
        {activeTab === 'privacy' && <PrivacyTab />}
        {activeTab === 'integrations' && <IntegrationsTab />}
      </div>
    </div>
  );
};

export default SettingsPanel;