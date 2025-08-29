// constants/settings.ts
export const DEFAULT_SETTINGS = {
  personalInfo: {
    name: '',
    email: '',
    affiliation: '',
    researchInterests: [],
    orcidId: '',
    bio: '',
    website: '',
    location: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  },
  preferences: {
    theme: 'light' as const,
    language: 'English',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    dateFormat: 'MM/DD/YYYY',
    defaultWordCount: 8000,
    autoSave: true,
    autoSaveInterval: 30, // seconds
    defaultView: 'grid' as const,
    papersPerPage: 12,
    showPreview: true,
    compactMode: false,
  },
  aiPersonalization: {
    labLevel: 7,
    personalLevel: 8,
    globalLevel: 5,
    writingStyle: 'academic' as const,
    researchFocus: [],
    suggestionsEnabled: true,
    contextDepth: 'moderate' as const,
    autoComplete: true,
    smartSuggestions: true,
    citationStyle: 'APA',
  },
  notifications: {
    emailNotifications: true,
    deadlineReminders: true,
    collaborationUpdates: true,
    aiSuggestions: false,
    weeklyReports: true,
    pushNotifications: false,
    reminderFrequency: 'weekly' as const,
    soundEnabled: false,
    browserNotifications: true,
  },
  privacy: {
    profileVisibility: 'institution' as const,
    shareAnalytics: true,
    dataSyncEnabled: true,
    allowResearchSharing: false,
    trackingOptOut: false,
    showOnlineStatus: true,
    allowIndexing: false,
  },
  integrations: {
    googleDrive: false,
    dropbox: false,
    zotero: false,
    mendeley: false,
    latex: false,
    orcid: false,
    github: false,
    overleaf: false,
  },
  editor: {
    fontSize: 14,
    fontFamily: 'Inter',
    lineHeight: 1.6,
    showWordCount: true,
    showReadingTime: true,
    spellCheck: true,
    autoCorrect: false,
    darkMode: false,
    focusMode: false,
  },
  export: {
    defaultFormat: 'pdf' as const,
    includeMetadata: true,
    includeComments: false,
    template: 'standard',
    citationFormat: 'inline',
  }
};

export const THEME_OPTIONS = [
  { value: 'light', label: 'Light', description: 'Light theme for daytime work' },
  { value: 'dark', label: 'Dark', description: 'Dark theme for reduced eye strain' },
  { value: 'auto', label: 'Auto', description: 'Follow system preference' },
] as const;

export const LANGUAGE_OPTIONS = [
  { value: 'English', label: 'English', code: 'en' },
  { value: 'Spanish', label: 'Español', code: 'es' },
  { value: 'French', label: 'Français', code: 'fr' },
  { value: 'German', label: 'Deutsch', code: 'de' },
  { value: 'Italian', label: 'Italiano', code: 'it' },
  { value: 'Portuguese', label: 'Português', code: 'pt' },
  { value: 'Chinese', label: '中文', code: 'zh' },
  { value: 'Japanese', label: '日本語', code: 'ja' },
] as const;

export const TIMEZONE_OPTIONS = [
  { value: 'UTC-12', label: '(GMT-12:00) International Date Line West' },
  { value: 'UTC-11', label: '(GMT-11:00) Coordinated Universal Time-11' },
  { value: 'UTC-10', label: '(GMT-10:00) Hawaii' },
  { value: 'UTC-9', label: '(GMT-09:00) Alaska' },
  { value: 'UTC-8', label: '(GMT-08:00) Pacific Time (US & Canada)' },
  { value: 'UTC-7', label: '(GMT-07:00) Mountain Time (US & Canada)' },
  { value: 'UTC-6', label: '(GMT-06:00) Central Time (US & Canada)' },
  { value: 'UTC-5', label: '(GMT-05:00) Eastern Time (US & Canada)' },
  { value: 'UTC-4', label: '(GMT-04:00) Atlantic Time (Canada)' },
  { value: 'UTC-3', label: '(GMT-03:00) Brasilia' },
  { value: 'UTC-2', label: '(GMT-02:00) Coordinated Universal Time-02' },
  { value: 'UTC-1', label: '(GMT-01:00) Azores' },
  { value: 'UTC+0', label: '(GMT+00:00) Greenwich Mean Time' },
  { value: 'UTC+1', label: '(GMT+01:00) Central European Time' },
  { value: 'UTC+2', label: '(GMT+02:00) Eastern European Time' },
  { value: 'UTC+3', label: '(GMT+03:00) Moscow' },
  { value: 'UTC+4', label: '(GMT+04:00) Abu Dhabi, Muscat' },
  { value: 'UTC+5', label: '(GMT+05:00) Islamabad, Karachi' },
  { value: 'UTC+6', label: '(GMT+06:00) Astana, Dhaka' },
  { value: 'UTC+7', label: '(GMT+07:00) Bangkok, Hanoi, Jakarta' },
  { value: 'UTC+8', label: '(GMT+08:00) Beijing, Perth, Singapore' },
  { value: 'UTC+9', label: '(GMT+09:00) Tokyo, Seoul' },
  { value: 'UTC+10', label: '(GMT+10:00) Eastern Australia' },
  { value: 'UTC+11', label: '(GMT+11:00) Magadan' },
  { value: 'UTC+12', label: '(GMT+12:00) Auckland, Fiji' },
] as const;

export const DATE_FORMAT_OPTIONS = [
  { value: 'MM/DD/YYYY', label: '12/31/2024', example: '12/31/2024' },
  { value: 'DD/MM/YYYY', label: '31/12/2024', example: '31/12/2024' },
  { value: 'YYYY-MM-DD', label: '2024-12-31', example: '2024-12-31' },
  { value: 'DD MMM YYYY', label: '31 Dec 2024', example: '31 Dec 2024' },
  { value: 'MMM DD, YYYY', label: 'Dec 31, 2024', example: 'Dec 31, 2024' },
] as const;

export const WRITING_STYLES = [
  { 
    value: 'academic', 
    label: 'Academic', 
    description: 'Formal, structured, and scholarly tone',
    example: 'The findings demonstrate a significant correlation...'
  },
  { 
    value: 'concise', 
    label: 'Concise', 
    description: 'Brief, clear, and to the point',
    example: 'Results show strong correlation between variables.'
  },
  { 
    value: 'detailed', 
    label: 'Detailed', 
    description: 'Comprehensive and thorough explanations',
    example: 'The extensive analysis reveals multiple interconnected factors...'
  },
  { 
    value: 'collaborative', 
    label: 'Collaborative', 
    description: 'Discussion-oriented and interactive',
    example: 'Let us consider how these findings might inform...'
  },
] as const;

export const CONTEXT_DEPTH_OPTIONS = [
  { 
    value: 'minimal', 
    label: 'Minimal', 
    description: 'Basic context from current paper only' 
  },
  { 
    value: 'moderate', 
    label: 'Moderate', 
    description: 'Context from current and recent papers' 
  },
  { 
    value: 'comprehensive', 
    label: 'Comprehensive', 
    description: 'Full context from all papers and collaborations' 
  },
] as const;

export const CITATION_STYLES = [
  { value: 'APA', label: 'APA (American Psychological Association)' },
  { value: 'MLA', label: 'MLA (Modern Language Association)' },
  { value: 'Chicago', label: 'Chicago Manual of Style' },
  { value: 'Harvard', label: 'Harvard Referencing' },
  { value: 'IEEE', label: 'IEEE Citation Style' },
  { value: 'Nature', label: 'Nature Citation Style' },
] as const;

export const FONT_OPTIONS = [
  { value: 'Inter', label: 'Inter', category: 'Sans-serif' },
  { value: 'Roboto', label: 'Roboto', category: 'Sans-serif' },
  { value: 'Open Sans', label: 'Open Sans', category: 'Sans-serif' },
  { value: 'Source Sans Pro', label: 'Source Sans Pro', category: 'Sans-serif' },
  { value: 'Times New Roman', label: 'Times New Roman', category: 'Serif' },
  { value: 'Georgia', label: 'Georgia', category: 'Serif' },
  { value: 'Source Serif Pro', label: 'Source Serif Pro', category: 'Serif' },
  { value: 'JetBrains Mono', label: 'JetBrains Mono', category: 'Monospace' },
  { value: 'Fira Code', label: 'Fira Code', category: 'Monospace' },
] as const;

export const REMINDER_FREQUENCY_OPTIONS = [
  { value: 'daily', label: 'Daily', description: 'Get reminders every day' },
  { value: 'weekly', label: 'Weekly', description: 'Get reminders once a week' },
  { value: 'monthly', label: 'Monthly', description: 'Get reminders once a month' },
  { value: 'never', label: 'Never', description: 'Turn off all reminders' },
] as const;

export const PROFILE_VISIBILITY_OPTIONS = [
  { 
    value: 'public', 
    label: 'Public', 
    description: 'Visible to everyone on the platform',
    icon: '🌐'
  },
  { 
    value: 'institution', 
    label: 'Institution Only', 
    description: 'Only visible to members of your institution',
    icon: '🏛️'
  },
  { 
    value: 'private', 
    label: 'Private', 
    description: 'Only visible to you',
    icon: '🔒'
  },
] as const;

export const EXPORT_FORMAT_OPTIONS = [
  { 
    value: 'pdf', 
    label: 'PDF', 
    description: 'Portable Document Format',
    extension: '.pdf',
    icon: '📄'
  },
  { 
    value: 'docx', 
    label: 'Word Document', 
    description: 'Microsoft Word format',
    extension: '.docx',
    icon: '📝'
  },
  { 
    value: 'latex', 
    label: 'LaTeX', 
    description: 'LaTeX source code',
    extension: '.tex',
    icon: '📊'
  },
  { 
    value: 'html', 
    label: 'HTML', 
    description: 'Web page format',
    extension: '.html',
    icon: '🌐'
  },
] as const;

// Validation rules
export const VALIDATION_RULES = {
  name: {
    minLength: 2,
    maxLength: 100,
    required: true,
  },
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  affiliation: {
    maxLength: 200,
  },
  bio: {
    maxLength: 500,
  },
  website: {
    pattern: /^https?:\/\/.+/,
  },
  orcidId: {
    pattern: /^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$/,
  },
  targetWordCount: {
    min: 100,
    max: 100000,
  },
  fontSize: {
    min: 10,
    max: 24,
  },
  lineHeight: {
    min: 1.0,
    max: 3.0,
  },
  autoSaveInterval: {
    min: 10,
    max: 300,
  },
} as const;