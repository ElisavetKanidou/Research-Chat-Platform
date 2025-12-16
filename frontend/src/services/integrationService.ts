// services/integrationService.ts
import { apiClient } from '../utils/apiHelpers';

export interface OAuthResponse {
  auth_url: string;
}

export interface IntegrationResponse {
  message: string;
  integration: string;
  connected: boolean;
}

class IntegrationService {
  private readonly basePath = '/integrations';

  // ==================== GOOGLE DRIVE ====================

  /**
   * Get Google Drive OAuth authorization URL
   */
  async getGoogleDriveAuthUrl(): Promise<string> {
    try {
      console.log('🔐 [IntegrationService] Getting Google Drive auth URL...');
      const response = await apiClient.get<OAuthResponse>(`${this.basePath}/google-drive/authorize`);
      console.log('✅ [IntegrationService] Got Google Drive auth URL');
      return response.auth_url;
    } catch (error) {
      console.error('❌ Failed to get Google Drive auth URL:', error);
      throw error;
    }
  }

  /**
   * Complete Google Drive OAuth callback
   */
  async completeGoogleDriveCallback(code: string, state: string): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Completing Google Drive OAuth...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/google-drive/callback`,
        { code, state }
      );
      console.log('✅ [IntegrationService] Google Drive connected');
      return response;
    } catch (error) {
      console.error('❌ Failed to complete Google Drive OAuth:', error);
      throw error;
    }
  }

  /**
   * Disconnect Google Drive
   */
  async disconnectGoogleDrive(): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Disconnecting Google Drive...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/google-drive/disconnect`,
        {}
      );
      console.log('✅ [IntegrationService] Google Drive disconnected');
      return response;
    } catch (error) {
      console.error('❌ Failed to disconnect Google Drive:', error);
      throw error;
    }
  }

  // ==================== DROPBOX ====================

  /**
   * Get Dropbox OAuth authorization URL
   */
  async getDropboxAuthUrl(): Promise<string> {
    try {
      console.log('🔐 [IntegrationService] Getting Dropbox auth URL...');
      const response = await apiClient.get<OAuthResponse>(`${this.basePath}/dropbox/authorize`);
      console.log('✅ [IntegrationService] Got Dropbox auth URL');
      return response.auth_url;
    } catch (error) {
      console.error('❌ Failed to get Dropbox auth URL:', error);
      throw error;
    }
  }

  /**
   * Complete Dropbox OAuth callback
   */
  async completeDropboxCallback(code: string, state: string): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Completing Dropbox OAuth...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/dropbox/callback`,
        { code, state }
      );
      console.log('✅ [IntegrationService] Dropbox connected');
      return response;
    } catch (error) {
      console.error('❌ Failed to complete Dropbox OAuth:', error);
      throw error;
    }
  }

  /**
   * Disconnect Dropbox
   */
  async disconnectDropbox(): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Disconnecting Dropbox...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/dropbox/disconnect`,
        {}
      );
      console.log('✅ [IntegrationService] Dropbox disconnected');
      return response;
    } catch (error) {
      console.error('❌ Failed to disconnect Dropbox:', error);
      throw error;
    }
  }

  // ==================== ZOTERO ====================

  /**
   * Connect Zotero with API key
   */
  async connectZotero(apiKey: string, userId?: string): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Connecting Zotero...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/zotero/connect`,
        { api_key: apiKey, user_id: userId }
      );
      console.log('✅ [IntegrationService] Zotero connected');
      return response;
    } catch (error) {
      console.error('❌ Failed to connect Zotero:', error);
      throw error;
    }
  }

  /**
   * Disconnect Zotero
   */
  async disconnectZotero(): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Disconnecting Zotero...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/zotero/disconnect`,
        {}
      );
      console.log('✅ [IntegrationService] Zotero disconnected');
      return response;
    } catch (error) {
      console.error('❌ Failed to disconnect Zotero:', error);
      throw error;
    }
  }

  // ==================== MENDELEY ====================

  /**
   * Get Mendeley OAuth authorization URL
   */
  async getMendeleyAuthUrl(): Promise<string> {
    try {
      console.log('🔐 [IntegrationService] Getting Mendeley auth URL...');
      const response = await apiClient.get<OAuthResponse>(`${this.basePath}/mendeley/authorize`);
      console.log('✅ [IntegrationService] Got Mendeley auth URL');
      return response.auth_url;
    } catch (error) {
      console.error('❌ Failed to get Mendeley auth URL:', error);
      throw error;
    }
  }

  /**
   * Complete Mendeley OAuth callback
   */
  async completeMendeleyCallback(code: string, state: string): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Completing Mendeley OAuth...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/mendeley/callback`,
        { code, state }
      );
      console.log('✅ [IntegrationService] Mendeley connected');
      return response;
    } catch (error) {
      console.error('❌ Failed to complete Mendeley OAuth:', error);
      throw error;
    }
  }

  /**
   * Disconnect Mendeley
   */
  async disconnectMendeley(): Promise<IntegrationResponse> {
    try {
      console.log('🔐 [IntegrationService] Disconnecting Mendeley...');
      const response = await apiClient.post<IntegrationResponse>(
        `${this.basePath}/mendeley/disconnect`,
        {}
      );
      console.log('✅ [IntegrationService] Mendeley disconnected');
      return response;
    } catch (error) {
      console.error('❌ Failed to disconnect Mendeley:', error);
      throw error;
    }
  }
}

export const integrationService = new IntegrationService();
