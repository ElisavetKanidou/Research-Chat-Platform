// paper/PaperAISettings.tsx - FIXED RESEARCH FOCUS SAVING
import React, { useState, useEffect } from 'react';
import { Loader, Save } from 'lucide-react';
import { paperService } from '../services/paperService';
import { useGlobalContext } from '../contexts/GlobalContext';

interface PaperAISettingsProps {
  paperId: string;
}

interface AISettings {
  labLevel: number;
  personalLevel: number;
  globalLevel: number;
  writingStyle: 'academic' | 'concise' | 'detailed' | 'collaborative';
  contextDepth: 'minimal' | 'moderate' | 'comprehensive';
  researchFocus: string[];
  suggestionsEnabled: boolean;
}

const PaperAISettings: React.FC<PaperAISettingsProps> = ({ paperId }) => {
  const { addNotification } = useGlobalContext();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [settings, setSettings] = useState<AISettings>({
    labLevel: 7,
    personalLevel: 8,
    globalLevel: 5,
    writingStyle: 'academic',
    contextDepth: 'moderate',
    researchFocus: [],
    suggestionsEnabled: true,
  });

  useEffect(() => {
    loadSettings();
  }, [paperId]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await paperService.getPaperAISettings(paperId);
      
      console.log('📥 Loaded AI settings response:', response);
      
      const settingsData = response.settings || response;
      
      console.log('📝 Settings data:', settingsData);
      
      setSettings({
        labLevel: settingsData.labLevel ?? 7,
        personalLevel: settingsData.personalLevel ?? 8,
        globalLevel: settingsData.globalLevel ?? 5,
        writingStyle: settingsData.writingStyle ?? 'academic',
        contextDepth: settingsData.contextDepth ?? 'moderate',
        // ✅ FIXED: Ensure researchFocus is always an array
        researchFocus: Array.isArray(settingsData.researchFocus) ? settingsData.researchFocus : [],
        suggestionsEnabled: settingsData.suggestionsEnabled ?? true,
      });
      
      console.log('✅ Settings loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load AI settings:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load AI settings. Using defaults.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      console.log('💾 Saving AI settings:', settings);
      
      // ✅ FIXED: Explicitly include researchFocus in save
      const settingsToSave = {
        labLevel: settings.labLevel,
        personalLevel: settings.personalLevel,
        globalLevel: settings.globalLevel,
        writingStyle: settings.writingStyle,
        contextDepth: settings.contextDepth,
        researchFocus: settings.researchFocus, // ✅ Explicitly send array
        suggestionsEnabled: settings.suggestionsEnabled,
      };
      
      console.log('📤 Sending to backend:', settingsToSave);
      
      await paperService.updatePaperAISettings(paperId, settingsToSave);
      
      addNotification({
        type: 'success',
        title: 'Settings Saved',
        message: 'Paper AI settings updated successfully',
      });
    } catch (error) {
      console.error('❌ Failed to save AI settings:', error);
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to save AI settings',
      });
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = <K extends keyof AISettings>(
    key: K,
    value: AISettings[K]
  ) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="animate-spin h-8 w-8 text-blue-600" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Paper AI Settings</h2>
          <p className="text-gray-600">Customize AI behavior for this specific paper</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? <Loader className="animate-spin" size={18} /> : <Save size={18} />}
          Save Changes
        </button>
      </div>

      {/* AI Influence Levels */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Influence Levels</h3>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Lab Papers Influence: {settings.labLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={settings.labLevel}
              onChange={(e) => updateSetting('labLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              How much the AI considers your lab's research patterns for this paper
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Personal Papers Influence: {settings.personalLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={settings.personalLevel}
              onChange={(e) => updateSetting('personalLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              How much the AI adapts to your individual writing style for this paper
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Global Literature Influence: {settings.globalLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={settings.globalLevel}
              onChange={(e) => updateSetting('globalLevel', parseInt(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              How much the AI considers broader field trends for this paper
            </p>
          </div>
        </div>
      </div>

      {/* Writing Preferences */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Writing Preferences</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Writing Style
            </label>
            <select
              value={settings.writingStyle}
              onChange={(e) => updateSetting('writingStyle', e.target.value as any)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="academic">Academic - Formal and structured</option>
              <option value="concise">Concise - Brief and to the point</option>
              <option value="detailed">Detailed - Comprehensive and thorough</option>
              <option value="collaborative">Collaborative - Discussion-oriented</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Context Depth
            </label>
            <select
              value={settings.contextDepth}
              onChange={(e) => updateSetting('contextDepth', e.target.value as any)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="minimal">Minimal - Quick, high-level responses</option>
              <option value="moderate">Moderate - Balanced detail</option>
              <option value="comprehensive">Comprehensive - In-depth analysis</option>
            </select>
          </div>
        </div>
      </div>

      {/* Research Focus */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Focus for This Paper</h3>
        
        <div className="flex flex-wrap gap-2 mb-3">
          {settings.researchFocus.map((focus, index) => (
            <span key={index} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm flex items-center gap-1">
              {focus}
              <button
                onClick={() => {
                  const newFocus = settings.researchFocus.filter((_, i) => i !== index);
                  updateSetting('researchFocus', newFocus);
                  console.log('🗑️ Removed focus:', focus, 'New array:', newFocus);
                }}
                className="text-purple-500 hover:text-purple-700 font-bold"
              >
                ×
              </button>
            </span>
          ))}
          {settings.researchFocus.length === 0 && (
            <span className="text-gray-400 text-sm italic">No research focus areas added yet</span>
          )}
        </div>
        
        <input
          type="text"
          placeholder="Add research focus area (press Enter)"
          className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              const value = (e.target as HTMLInputElement).value.trim();
              if (value && !settings.researchFocus.includes(value)) {
                const newFocus = [...settings.researchFocus, value];
                updateSetting('researchFocus', newFocus);
                (e.target as HTMLInputElement).value = '';
                console.log('➕ Added focus:', value, 'New array:', newFocus);
              }
            }
          }}
        />
        <p className="text-xs text-gray-500 mt-2">
          Specify research areas for paper-specific AI guidance (e.g., "quantum computing", "machine learning")
        </p>
      </div>

      {/* AI Suggestions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">AI Suggestions</h3>
            <p className="text-sm text-gray-600">Enable real-time AI suggestions while writing</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={settings.suggestionsEnabled}
              onChange={(e) => updateSetting('suggestionsEnabled', e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>
    </div>
  );
};

export default PaperAISettings;