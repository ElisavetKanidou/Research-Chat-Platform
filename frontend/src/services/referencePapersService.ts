// services/referencePapersService.ts

export type PaperType = 'lab' | 'personal' | 'literature';

export interface WritingStyleFeatures {
  avg_sentence_length?: number;
  vocabulary_complexity?: number;
  passive_voice_ratio?: number;
  common_phrases?: string[];
  technical_terms?: string[];
  citation_density?: number;
  section_structure?: string[];
}

export interface ReferencePaper {
  id: string;
  user_id: string;
  title: string;
  authors?: string;
  year?: number;
  journal?: string;
  doi?: string;
  paper_type: PaperType;
  research_area?: string;
  keywords?: string[];
  abstract?: string;
  file_url: string;
  file_size?: number;
  original_filename: string;
  is_analyzed: boolean;
  analysis_date?: string;
  writing_style_features?: WritingStyleFeatures;
  metadata?: Record<string, any>;
  times_used: number;
  created_at: string;
  updated_at: string;
}

export interface ReferencePaperListResponse {
  papers: ReferencePaper[];
  total: number;
  lab_papers_count: number;
  personal_papers_count: number;
  literature_papers_count: number;
}

export interface ReferencePaperUploadResponse {
  id: string;
  title: string;
  paper_type: string;
  file_url: string;
  original_filename: string;
  is_analyzed: boolean;
  message: string;
}

export interface UploadReferencePaperRequest {
  file: File;
  title: string;
  paper_type: PaperType;
  authors?: string;
  year?: number;
  journal?: string;
  doi?: string;
  research_area?: string;
  abstract?: string;
}

export interface UpdateReferencePaperRequest {
  title?: string;
  authors?: string;
  year?: number;
  journal?: string;
  doi?: string;
  research_area?: string;
  keywords?: string[];
  abstract?: string;
}

class ReferencePapersService {
  private readonly apiUrl = 'http://127.0.0.1:8000/api/v1/reference-papers';

  /**
   * Upload a new reference paper
   */
  async uploadReferencePaper(request: UploadReferencePaperRequest): Promise<ReferencePaperUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('file', request.file);
      formData.append('title', request.title);
      formData.append('paper_type', request.paper_type);

      if (request.authors) formData.append('authors', request.authors);
      if (request.year) formData.append('year', request.year.toString());
      if (request.journal) formData.append('journal', request.journal);
      if (request.doi) formData.append('doi', request.doi);
      if (request.research_area) formData.append('research_area', request.research_area);
      if (request.abstract) formData.append('abstract', request.abstract);

      const response = await fetch(`${this.apiUrl}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error uploading reference paper:', error);
      throw error;
    }
  }

  /**
   * Get all reference papers for the current user
   */
  async getReferencePapers(paperType?: PaperType): Promise<ReferencePaperListResponse> {
    try {
      const url = paperType
        ? `${this.apiUrl}/?paper_type=${paperType}`
        : `${this.apiUrl}/`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch reference papers: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching reference papers:', error);

      // Return empty list as fallback
      return {
        papers: [],
        total: 0,
        lab_papers_count: 0,
        personal_papers_count: 0,
        literature_papers_count: 0,
      };
    }
  }

  /**
   * Get a specific reference paper by ID
   */
  async getReferencePaper(paperId: string): Promise<ReferencePaper> {
    try {
      const response = await fetch(`${this.apiUrl}/${paperId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch reference paper: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching reference paper:', error);
      throw error;
    }
  }

  /**
   * Update reference paper metadata
   */
  async updateReferencePaper(
    paperId: string,
    updates: UpdateReferencePaperRequest
  ): Promise<ReferencePaper> {
    try {
      const response = await fetch(`${this.apiUrl}/${paperId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update reference paper: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating reference paper:', error);
      throw error;
    }
  }

  /**
   * Delete a reference paper
   */
  async deleteReferencePaper(paperId: string): Promise<void> {
    try {
      const response = await fetch(`${this.apiUrl}/${paperId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete reference paper: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Error deleting reference paper:', error);
      throw error;
    }
  }

  /**
   * Re-analyze a reference paper's writing style
   */
  async reanalyzeReferencePaper(paperId: string): Promise<ReferencePaper> {
    try {
      const response = await fetch(`${this.apiUrl}/${paperId}/reanalyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to reanalyze reference paper: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error reanalyzing reference paper:', error);
      throw error;
    }
  }

  /**
   * Get stats about reference papers
   */
  async getReferencePapersStats(): Promise<{
    total: number;
    byType: Record<PaperType, number>;
    analyzed: number;
    notAnalyzed: number;
  }> {
    try {
      const data = await this.getReferencePapers();

      const analyzed = data.papers.filter(p => p.is_analyzed).length;

      return {
        total: data.total,
        byType: {
          lab: data.lab_papers_count,
          personal: data.personal_papers_count,
          literature: data.literature_papers_count,
        },
        analyzed,
        notAnalyzed: data.total - analyzed,
      };
    } catch (error) {
      console.error('Error getting reference papers stats:', error);
      return {
        total: 0,
        byType: { lab: 0, personal: 0, literature: 0 },
        analyzed: 0,
        notAnalyzed: 0,
      };
    }
  }

  private getAuthToken(): string {
    return localStorage.getItem('auth_token') || 'fake-token';
  }
}

export const referencePapersService = new ReferencePapersService();
