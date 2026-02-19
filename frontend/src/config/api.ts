/**
 * API Configuration
 * Centralized API URL configuration with environment support
 */

/**
 * Get the API base URL based on environment
 * Priority:
 * 1. VITE_API_URL environment variable (build-time)
 * 2. Auto-detect from window.location (runtime)
 * 3. Fallback to localhost:8090
 */
export function getApiBaseUrl(): string {
  // 1. Check environment variable (set during build)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 2. Auto-detect from window.location (runtime)
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    return `${protocol}//${hostname}:8090/api/v1`;
  }

  // 3. Fallback for SSR or non-browser environments
  return 'http://localhost:8090/api/v1';
}

/**
 * Get WebSocket URL
 */
export function getWebSocketUrl(): string {
  const apiUrl = getApiBaseUrl();
  // Replace http with ws
  return apiUrl.replace(/^http/, 'ws').replace('/api/v1', '/api/v1/ws');
}

// Export as constants
export const API_BASE_URL = getApiBaseUrl();
export const WS_URL = getWebSocketUrl();
