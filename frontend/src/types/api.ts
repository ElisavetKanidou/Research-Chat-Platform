export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
}

// Paper API types
export interface CreatePaperRequest {
  title: string;
  abstract?: string;
  researchArea?: string;
  targetWordCount?: number;
  coAuthors?: string[];
  tags?: string[];
  isPublic?: boolean;
}

export interface UpdatePaperRequest {
  title?: string;
  abstract?: string;
  researchArea?: string;
  targetWordCount?: number;
  coAuthors?: string[];
  tags?: string[];
  isPublic?: boolean;
  status?: string;
}

export interface PaperResponse {
  id: string;
  title: string;
  abstract: string;
  status: string;
  createdAt: string;
  lastModified: string;
  progress: number;
  targetWordCount: number;
  currentWordCount: number;
  coAuthors: string[];
  researchArea: string;
  sections: SectionResponse[];
  tags: string[];
  isPublic: boolean;
  owner: UserSummary;
}

export interface SectionResponse {
  id: string;
  title: string;
  content: string;
  status: string;
  lastModified: string;
  wordCount: number;
  order: number;
}

// Chat API types
export interface ChatMessageRequest {
  content: string;
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
  personalizationSettings: {
    labLevel: number;
    personalLevel: number;
    globalLevel: number;
    writingStyle: string;
    researchFocus: string[];
  };
}

export interface ChatMessageResponse {
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
    relatedPapers?: string[];
  };
}

export interface ChatAttachment {
  type: 'excel' | 'pdf' | 'references' | 'data' | 'image';
  name: string;
  size: string;
  url?: string;
  downloadUrl?: string;
}

// Auth API types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: UserResponse;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  affiliation?: string;
  researchInterests?: string[];
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: string;
  lastLoginAt: string;
  isActive: boolean;
  personalInfo: {
    name: string;
    email: string;
    affiliation: string;
    researchInterests: string[];
    orcidId?: string;
  };
}

export interface UserSummary {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

// Analytics API types
export interface AnalyticsRequest {
  timeframe: 'day' | 'week' | 'month' | 'quarter' | 'year';
  startDate?: string;
  endDate?: string;
  paperIds?: string[];
  metrics: string[];
}

export interface AnalyticsResponse {
  userId: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  metrics: AnalyticsMetric[];
  insights: InsightResponse[];
  generatedAt: string;
}

export interface AnalyticsMetric {
  name: string;
  value: number;
  unit: string;
  change: number;
  changeType: 'increase' | 'decrease' | 'stable';
  trend: number[];
}

export interface InsightResponse {
  id: string;
  type: string;
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  actionable: boolean;
  suggestions: string[];
}

// Search API types
export interface SearchRequest {
  query: string;
  filters?: {
    type?: 'papers' | 'collaborators' | 'references';
    status?: string[];
    researchArea?: string[];
    dateRange?: {
      start: string;
      end: string;
    };
  };
  sort?: {
    field: string;
    order: 'asc' | 'desc';
  };
  pagination?: {
    page: number;
    limit: number;
  };
}

export interface SearchResponse<T> {
  results: T[];
  totalResults: number;
  query: string;
  filters: any;
  facets?: SearchFacet[];
  suggestions?: string[];
  executionTime: number;
}

export interface SearchFacet {
  name: string;
  values: Array<{
    value: string;
    count: number;
  }>;
}

// Export API types
export interface ExportRequest {
  format: 'pdf' | 'docx' | 'latex' | 'json';
  paperIds: string[];
  options?: {
    includeComments?: boolean;
    includeMetadata?: boolean;
    template?: string;
  };
}

export interface ExportResponse {
  exportId: string;
  status: 'processing' | 'completed' | 'failed';
  downloadUrl?: string;
  createdAt: string;
  expiresAt: string;
}

// Collaboration API types
export interface InviteCollaboratorRequest {
  paperId: string;
  email: string;
  role: 'viewer' | 'editor' | 'co-author';
  message?: string;
}

export interface CollaboratorResponse {
  id: string;
  paperId: string;
  userId: string;
  name: string;
  email: string;
  role: 'viewer' | 'editor' | 'co-author';
  status: 'pending' | 'accepted' | 'declined';
  invitedAt: string;
  joinedAt?: string;
  lastActivity?: string;
}

// File upload types
export interface FileUploadRequest {
  file: File;
  type: 'document' | 'reference' | 'data' | 'image';
  paperId?: string;
}

export interface FileUploadResponse {
  id: string;
  filename: string;
  originalName: string;
  size: number;
  mimeType: string;
  url: string;
  uploadedAt: string;
}

// Notification types
export interface NotificationResponse {
  id: string;
  type: 'deadline' | 'collaboration' | 'ai_suggestion' | 'system';
  title: string;
  message: string;
  isRead: boolean;
  createdAt: string;
  actionUrl?: string;
  metadata?: any;
}

// Settings API types
export interface UpdateSettingsRequest {
  preferences?: {
    theme?: 'light' | 'dark' | 'auto';
    language?: string;
    timezone?: string;
    dateFormat?: string;
    defaultWordCount?: number;
    autoSave?: boolean;
  };
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
  aiPersonalization?: {
    labLevel?: number;
    personalLevel?: number;
    globalLevel?: number;
    writingStyle?: string;
    researchFocus?: string[];
  };
}

// Webhook types
export interface WebhookEvent {
  id: string;
  type: string;
  data: any;
  timestamp: string;
  signature: string;
}

export interface WebhookSubscription {
  id: string;
  url: string;
  events: string[];
  isActive: boolean;
  createdAt: string;
  lastDelivery?: string;
}

// Rate limiting types
export interface RateLimitInfo {
  limit: number;
  remaining: number;
  reset: number;
  retryAfter?: number;
}

// Headers types
export type ApiHeaders = Record<string, string> & {
  'X-Rate-Limit-Limit'?: string;
  'X-Rate-Limit-Remaining'?: string;
  'X-Rate-Limit-Reset'?: string;
  'X-Request-ID'?: string;
};

// Generic API utilities
export type ApiMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}

export interface RequestConfig {
  method: ApiMethod;
  url: string;
  data?: any;
  params?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface ApiError {
  code: string;
  message: string;
  status: number;
  details?: any;
  timestamp: string;
}

export type ApiResponseType = 'json' | 'text' | 'blob' | 'arraybuffer';

// ... (all your existing interfaces remain the same)

// Status and error codes - Alternative approach with objects
export const HttpStatus = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
} as const;

export const ApiErrorCode = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',
  RESOURCE_CONFLICT: 'RESOURCE_CONFLICT',
  RATE_LIMIT_EXCEEDED: 'RATE_LIMIT_EXCEEDED',
  SERVER_ERROR: 'SERVER_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
} as const;

// Type aliases for better type safety
export type HttpStatusValue = typeof HttpStatus[keyof typeof HttpStatus];
export type ApiErrorCodeValue = typeof ApiErrorCode[keyof typeof ApiErrorCode];