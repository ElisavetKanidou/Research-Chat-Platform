import { apiClient } from '../utils/apiHelpers';
import type { 
  LoginRequest, 
  LoginResponse, 
  RegisterRequest, 
  UserResponse 
} from '../types/api';

class AuthService {
  private readonly basePath = '/auth';
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_KEY = 'user_data';
  private refreshIntervalId: number | null = null;

  // Login user
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    try {
      console.log('🔍 [AuthService] Starting login...');
      
      // Backend expects OAuth2 form data format
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      
      console.log('🔍 [AuthService] Sending login request...');
      
      const response = await apiClient.postForm<any>(`${this.basePath}/login`, formData, {
        'Content-Type': 'application/x-www-form-urlencoded',
      });
      
      console.log('🔍 [AuthService] Login response:', response);
      
      // Backend returns: { access_token, refresh_token, token_type, expires_in }
      const accessToken = response.access_token || response.accessToken;
      const refreshToken = response.refresh_token || response.refreshToken;
      
      if (!accessToken) {
        console.error('❌ [AuthService] No access token in response:', response);
        throw new Error('No access token received from server');
      }
      
      console.log('🔍 [AuthService] Saving tokens...');
      this.setTokens(accessToken, refreshToken);
      
      console.log('🔍 [AuthService] Token saved:', {
        tokenExists: !!localStorage.getItem('auth_token'),
        tokenPreview: accessToken.substring(0, 20) + '...'
      });
      
      // Fetch user data after login
      console.log('🔍 [AuthService] Fetching user data...');
      const user = await this.getCurrentUser();
      
      console.log('🔍 [AuthService] User data received:', user);
      this.setUserData(user);
      
      console.log('🔍 [AuthService] Login complete!');
      
      return {
        user,
        accessToken,
        refreshToken,
        expiresIn: response.expires_in || response.expiresIn || 3600,
      };
    } catch (error) {
      console.error('❌ [AuthService] Login failed:', error);
      throw error;
    }
  }

  // Register new user
  async register(userData: RegisterRequest): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>(`${this.basePath}/register`, userData);
      this.setTokens(response.accessToken, response.refreshToken);
      this.setUserData(response.user);
      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuthData();
    }
  }

  // Refresh access token
  async refreshToken(): Promise<string> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    try {
      const response = await apiClient.post<{ accessToken: string; refreshToken: string }>(`${this.basePath}/refresh`, {
        refreshToken,
      });
      this.setTokens(response.accessToken, response.refreshToken);
      return response.accessToken;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearAuthData();
      throw error;
    }
  }

  // Get current user - FIXED: Uses /auth/me endpoint
  async getCurrentUser(): Promise<UserResponse> {
    try {
      return await apiClient.get<UserResponse>(`${this.basePath}/me`);
    } catch (error) {
      console.error('Get current user failed:', error);
      const cachedUser = this.getUserData();
      if (cachedUser) {
        return cachedUser;
      }
      throw error;
    }
  }

  // Update user profile
  async updateProfile(updates: Partial<UserResponse>): Promise<UserResponse> {
    try {
      const response = await apiClient.patch<UserResponse>(`${this.basePath}/profile`, updates);
      this.setUserData(response);
      return response;
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  }

  // ✅ FIXED: Change password - Uses correct snake_case field names
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      console.log('🔒 [AuthService] Changing password...');
      
      // ✅ Backend expects snake_case field names (current_password, new_password)
      await apiClient.post(`/users/me/change-password`, {
        current_password: currentPassword,
        new_password: newPassword,
      });
      
      console.log('✅ [AuthService] Password changed successfully');
    } catch (error: any) {
      console.error('❌ [AuthService] Password change failed:', error);
      
      // Extract error message from backend response
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  }

  // Request password reset
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/password-reset`, { email });
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw error;
    }
  }

  // Reset password with token
  async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/password-reset/confirm`, {
        token,
        newPassword,
      });
    } catch (error) {
      console.error('Password reset failed:', error);
      throw error;
    }
  }

  // Verify email
  async verifyEmail(token: string): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/verify-email`, { token });
    } catch (error) {
      console.error('Email verification failed:', error);
      throw error;
    }
  }

  // Resend verification email
  async resendVerificationEmail(): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/resend-verification`);
    } catch (error) {
      console.error('Resend verification failed:', error);
      throw error;
    }
  }

  // Token management
  getAccessToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(this.TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
  }

  clearTokens(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  // User data management
  getUserData(): UserResponse | null {
    const userData = localStorage.getItem(this.USER_KEY);
    try {
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }

  setUserData(user: UserResponse): void {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  clearUserData(): void {
    localStorage.removeItem(this.USER_KEY);
  }

  clearAuthData(): void {
    this.clearTokens();
    this.clearUserData();
  }

  // Auth state checks
  isAuthenticated(): boolean {
    return this.getAccessToken() !== null;
  }

  isTokenExpired(): boolean {
    const token = this.getAccessToken();
    if (!token) return true;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 < Date.now();
    } catch (error) {
      return true;
    }
  }

  shouldRefreshToken(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const timeUntilExpiry = payload.exp * 1000 - Date.now();
      return timeUntilExpiry < 5 * 60 * 1000; // Refresh if less than 5 minutes left
    } catch (error) {
      return false;
    }
  }

  // Auto-refresh token functionality
  setupTokenRefresh(): void {
    if (this.refreshIntervalId !== null) {
      clearInterval(this.refreshIntervalId);
    }
    this.refreshIntervalId = window.setInterval(async () => {
      if (this.shouldRefreshToken()) {
        try {
          await this.refreshToken();
        } catch (error) {
          console.error('Auto token refresh failed:', error);
          if (this.refreshIntervalId !== null) {
            clearInterval(this.refreshIntervalId);
            this.refreshIntervalId = null;
          }
          window.location.href = '/login';
        }
      }
    }, 60 * 1000);

    window.addEventListener('beforeunload', () => {
      if (this.refreshIntervalId !== null) {
        clearInterval(this.refreshIntervalId);
        this.refreshIntervalId = null;
      }
    });
  }

  // Social login methods
  async loginWithGoogle(): Promise<void> {
    console.log('Google login would be implemented here');
    throw new Error('Google login not implemented');
  }

  async loginWithOrcid(): Promise<void> {
    console.log('ORCID login would be implemented here');
    throw new Error('ORCID login not implemented');
  }

  // Two-factor authentication
  async enableTwoFactor(): Promise<{ qrCode: string; secret: string }> {
    try {
      return await apiClient.post<{ qrCode: string; secret: string }>(`${this.basePath}/2fa/enable`);
    } catch (error) {
      console.error('Enable 2FA failed:', error);
      throw error;
    }
  }

  async verifyTwoFactor(code: string): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/2fa/verify`, { code });
    } catch (error) {
      console.error('2FA verification failed:', error);
      throw error;
    }
  }

  async disableTwoFactor(code: string): Promise<void> {
    try {
      await apiClient.post(`${this.basePath}/2fa/disable`, { code });
    } catch (error) {
      console.error('Disable 2FA failed:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();