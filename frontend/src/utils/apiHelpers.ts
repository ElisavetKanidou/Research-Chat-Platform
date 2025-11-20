// utils/apiHelpers.ts

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  meta?: {
    page?: number;
    totalPages?: number;
    totalItems?: number;
  };
}

export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

export interface RequestInterceptor {
  (config: RequestInit): RequestInit | Promise<RequestInit>;
}

export interface ResponseInterceptor {
  (response: Response): Response | Promise<Response>;
}

// Single ApiError class (removed duplicate interface)
export class ApiError extends Error {
  public status: number;
  public code?: string;
  public message: string;

  constructor({ message, status, code }: { message: string; status: number; code?: string }) {
    super(message);
    this.name = 'ApiError';
    this.message = message;
    this.status = status;
    this.code = code;
  }
}

export class ApiClient {
  private baseUrl: string;
  private defaultHeaders: HeadersInit;
  private timeout: number;

  constructor(config: Partial<ApiConfig> = {}) {
    this.baseUrl = config.baseURL || 'http://127.0.0.1:8000/api/v1';
    this.timeout = config.timeout || 10000;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.headers,
    };
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('auth_token');
    console.log('🔍 [ApiClient] Getting auth headers, token exists:', !!token);
    if (token) {
      console.log('🔍 [ApiClient] Token preview:', token.substring(0, 20) + '...');
    }
    return token ? { ...this.defaultHeaders, Authorization: `Bearer ${token}` } : this.defaultHeaders;
  }  

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError({
        message: errorData.message || `HTTP Error: ${response.status}`,
        status: response.status,
        code: errorData.code,
      });
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }
    
    return response.text() as unknown as T;
  }
  private async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
      const headers = this.getAuthHeaders();
      
      console.log(`🔍 [ApiClient] ${method} ${url}`);
      console.log('🔍 [ApiClient] Headers:', Object.keys(headers));
      
      const response = await fetch(url, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
      });

      console.log(`🔍 [ApiClient] Response status: ${response.status}`);
      
      clearTimeout(timeoutId);
      return this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);
      
      console.error('🔍 [ApiClient] Request failed:', error);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError({
          message: 'Request timeout',
          status: 408,
          code: 'TIMEOUT'
        });
      }
      
      throw error;
    }
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    let url = endpoint;
    
    if (params) {
      const urlObj = new URL(endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`);
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          urlObj.searchParams.append(key, String(value));
        }
      });
      url = endpoint.startsWith('http') ? urlObj.toString() : urlObj.pathname + urlObj.search;
    }

    return this.request<T>('GET', url);
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('POST', endpoint, data);
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('PATCH', endpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>('PUT', endpoint, data);
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint);
  }

  async upload<T>(endpoint: string, file: File, additionalData?: Record<string, any>): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const token = localStorage.getItem('auth_token');
      const headers: HeadersInit = token ? { Authorization: `Bearer ${token}` } : {};

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new ApiError({
          message: 'Upload timeout',
          status: 408,
          code: 'TIMEOUT'
        });
      }
      
      throw error;
    }
  }
  async postForm<T>(endpoint: string, data: URLSearchParams | FormData, customHeaders?: Record<string, string>): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), this.timeout);

  try {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
    const token = localStorage.getItem('auth_token');
    
    const headers: HeadersInit = {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...customHeaders,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: data,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);
    return this.handleResponse<T>(response);
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError({
        message: 'Request timeout',
        status: 408,
        code: 'TIMEOUT'
      });
    }
    
    throw error;
  }
}
}

// Singleton instance
export const apiClient = new ApiClient();

// Error handling utilities
export const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

export const isNetworkError = (error: unknown): boolean => {
  return error instanceof TypeError && error.message.includes('fetch');
};

export const retryWithBackoff = async <T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> => {
  let lastError: unknown;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      if (!isNetworkError(error)) {
        throw error;
      }
      
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  } 
  throw lastError;
  
};

// ==================== CHAT API HELPERS ====================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  paper_id?: string;
}

export const getChatHistory = async (paperId?: string, limit: number = 50): Promise<ChatMessage[]> => {
  try {
    const params: Record<string, any> = { limit };
    if (paperId) {
      params.paper_id = paperId;
    }
    
    const response = await apiClient.get<ChatMessage[]>('/chat/history', params);
    console.log('📜 Chat history loaded:', response.length, 'messages');
    return response;
  } catch (error) {
    console.error('❌ Failed to load chat history:', error);
    return []; // Return empty array on error
  }
};



