// services/analyticsService.ts - UPDATED VERSION
import { apiClient } from '../utils/apiHelpers';

// ============================================
// NEW INTERFACES FOR REAL BACKEND DATA
// ============================================

export interface AnalyticsOverview {
  total_papers: number;
  status_breakdown: Record<string, number>;
  total_words: number;
  average_progress: number;
  active_papers: number;
  published_papers: number;
  papers_this_month: number;
}

export interface MonthlyProductivity {
  month: string;
  year: number;
  papers: number;
  words: number;
}

export interface ProductivityAnalytics {
  monthly_data: MonthlyProductivity[];
  writing_velocity: {
    words_per_week: number;
    change_from_last_month: number;
  };
  completion_time: {
    average_months: number;
    fastest_months: number;
  };
}

export interface CollaborationAnalytics {
  total_collaborators: number;
  collaborative_papers: number;
  solo_papers: number;
  top_collaborators: Array<{ name: string; papers: number }>;
}

export interface ResearchImpact {
  total_citations: number;
  published_papers: number;
  research_areas: Array<{ area: string; papers: number }>;
  h_index: number;
  average_citations: number;
}

// ============================================
// ANALYTICS SERVICE CLASS
// ============================================

class AnalyticsService {
  private readonly basePath = '/analytics';

  // ============================================
  // NEW REAL BACKEND METHODS
  // ============================================

  async getOverview(): Promise<AnalyticsOverview> {
    try {
      const response = await apiClient.get<AnalyticsOverview>(`${this.basePath}/overview`);
      return response;
    } catch (error) {
      console.error('Failed to fetch analytics overview:', error);
      // Return mock data as fallback
      return {
        total_papers: 0,
        status_breakdown: {},
        total_words: 0,
        average_progress: 0,
        active_papers: 0,
        published_papers: 0,
        papers_this_month: 0
      };
    }
  }

  async getProductivity(months: number = 6): Promise<ProductivityAnalytics> {
    try {
      const response = await apiClient.get<ProductivityAnalytics>(
        `${this.basePath}/productivity?months=${months}`
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch productivity analytics:', error);
      return {
        monthly_data: [],
        writing_velocity: {
          words_per_week: 0,
          change_from_last_month: 0
        },
        completion_time: {
          average_months: 0,
          fastest_months: 0
        }
      };
    }
  }

  async getCollaboration(): Promise<CollaborationAnalytics> {
    try {
      const response = await apiClient.get<CollaborationAnalytics>(
        `${this.basePath}/collaboration`
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch collaboration analytics:', error);
      return {
        total_collaborators: 0,
        collaborative_papers: 0,
        solo_papers: 0,
        top_collaborators: []
      };
    }
  }

  async getResearchImpact(): Promise<ResearchImpact> {
    try {
      const response = await apiClient.get<ResearchImpact>(
        `${this.basePath}/research-impact`
      );
      return response;
    } catch (error) {
      console.error('Failed to fetch research impact:', error);
      return {
        total_citations: 0,
        published_papers: 0,
        research_areas: [],
        h_index: 0,
        average_citations: 0
      };
    }
  }

  // ============================================
  // EXISTING METHODS (kept for compatibility)
  // ============================================

  // Export analytics data
  async exportAnalytics(format: 'csv' | 'json' | 'pdf'): Promise<Blob> {
    try {
      const response = await fetch(`${(apiClient as any).baseUrl}${this.basePath}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ format }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      return await response.blob();
    } catch (error) {
      console.error('Error exporting analytics:', error);
      throw error;
    }
  }
}

export const analyticsService = new AnalyticsService();