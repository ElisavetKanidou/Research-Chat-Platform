// services/paperService.ts

import { Paper, PaperSection, ResearchPhase, Task } from '../types/paper';

const API_BASE_URL = 'http://127.0.0.1:8000/api';
const STORAGE_KEY = 'researchhub_papers';

class PaperService {
  private useLocalStorage = false; // Toggle for development

  // Get all papers for current user
  async getAllPapers(): Promise<Paper[]> {
    if (this.useLocalStorage) {
      return this.getFromLocalStorage();
    }

    try {
      const response = await fetch(`${API_BASE_URL}/papers`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch papers: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching papers:', error);
      // Fallback to localStorage
      return this.getFromLocalStorage();
    }
  }

  // Get specific paper by ID
  async getPaperById(paperId: string): Promise<Paper | null> {
    if (this.useLocalStorage) {
      const papers = this.getFromLocalStorage();
      return papers.find(p => p.id === paperId) || null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) return null;
        throw new Error(`Failed to fetch paper: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching paper:', error);
      // Fallback to localStorage
      const papers = this.getFromLocalStorage();
      return papers.find(p => p.id === paperId) || null;
    }
  }

  // Create new paper
  async createPaper(paper: Paper): Promise<Paper> {
    if (this.useLocalStorage) {
      return this.saveToLocalStorage(paper);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/papers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify(paper),
      });

      if (!response.ok) {
        throw new Error(`Failed to create paper: ${response.statusText}`);
      }

      const createdPaper = await response.json();
      // Also save to localStorage as backup
      this.saveToLocalStorage(createdPaper);
      return createdPaper;
    } catch (error) {
      console.error('Error creating paper:', error);
      // Fallback to localStorage
      return this.saveToLocalStorage(paper);
    }
  }

  // Update existing paper
  async updatePaper(paperId: string, updates: Partial<Paper>): Promise<Paper> {
    if (this.useLocalStorage) {
      return this.updateLocalStorage(paperId, updates);
    }

    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update paper: ${response.statusText}`);
      }

      const updatedPaper = await response.json();
      // Also update localStorage
      this.updateLocalStorage(paperId, updates);
      return updatedPaper;
    } catch (error) {
      console.error('Error updating paper:', error);
      // Fallback to localStorage
      return this.updateLocalStorage(paperId, updates);
    }
  }

  // Delete paper
  async deletePaper(paperId: string): Promise<void> {
    if (this.useLocalStorage) {
      this.deleteFromLocalStorage(paperId);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete paper: ${response.statusText}`);
      }

      // Also remove from localStorage
      this.deleteFromLocalStorage(paperId);
    } catch (error) {
      console.error('Error deleting paper:', error);
      // Fallback to localStorage
      this.deleteFromLocalStorage(paperId);
    }
  }

  // Update paper section
  async updatePaperSection(paperId: string, sectionId: string, updates: Partial<PaperSection>): Promise<PaperSection> {
    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}/sections/${sectionId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update section: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating section:', error);
      throw error;
    }
  }

  // Get research phases for paper
  async getResearchPhases(paperId: string): Promise<ResearchPhase[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}/phases`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch research phases: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching research phases:', error);
      return this.getDefaultResearchPhases(paperId);
    }
  }

  // Export paper to various formats
  async exportPaper(paperId: string, format: 'pdf' | 'docx' | 'latex'): Promise<Blob> {
    try {
      const response = await fetch(`${API_BASE_URL}/papers/${paperId}/export/${format}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to export paper: ${response.statusText}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Error exporting paper:', error);
      throw error;
    }
  }

  // Search papers
  async searchPapers(query: string, filters?: {
    status?: string;
    researchArea?: string;
    dateFrom?: Date;
    dateTo?: Date;
  }): Promise<Paper[]> {
    try {
      const params = new URLSearchParams({
        q: query,
        ...filters && Object.entries(filters).reduce((acc, [key, value]) => {
          if (value) acc[key] = value.toString();
          return acc;
        }, {} as Record<string, string>),
      });

      const response = await fetch(`${API_BASE_URL}/papers/search?${params}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to search papers: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error searching papers:', error);
      // Fallback to local search
      return this.searchLocalPapers(query, filters);
    }
  }

  // Private methods for localStorage operations
  private getFromLocalStorage(): Paper[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return [];
      return JSON.parse(stored).map((paper: any) => ({
        ...paper,
        createdAt: new Date(paper.createdAt),
        lastModified: new Date(paper.lastModified),
        sections: paper.sections?.map((section: any) => ({
          ...section,
          lastModified: new Date(section.lastModified),
        })) || [],
      }));
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return [];
    }
  }

  private saveToLocalStorage(paper: Paper): Paper {
    try {
      const papers = this.getFromLocalStorage();
      const updatedPapers = [...papers, paper];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedPapers));
      return paper;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      throw error;
    }
  }

  private updateLocalStorage(paperId: string, updates: Partial<Paper>): Paper {
    try {
      const papers = this.getFromLocalStorage();
      const paperIndex = papers.findIndex(p => p.id === paperId);
      
      if (paperIndex === -1) {
        throw new Error('Paper not found');
      }

      const updatedPaper = { ...papers[paperIndex], ...updates, lastModified: new Date() };
      papers[paperIndex] = updatedPaper;
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(papers));
      return updatedPaper;
    } catch (error) {
      console.error('Error updating localStorage:', error);
      throw error;
    }
  }

  private deleteFromLocalStorage(paperId: string): void {
    try {
      const papers = this.getFromLocalStorage();
      const filteredPapers = papers.filter(p => p.id !== paperId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filteredPapers));
    } catch (error) {
      console.error('Error deleting from localStorage:', error);
    }
  }

  private searchLocalPapers(query: string, filters?: any): Paper[] {
    const papers = this.getFromLocalStorage();
    return papers.filter(paper => {
      const matchesQuery = query === '' || 
        paper.title.toLowerCase().includes(query.toLowerCase()) ||
        paper.abstract.toLowerCase().includes(query.toLowerCase()) ||
        paper.researchArea.toLowerCase().includes(query.toLowerCase());

      const matchesStatus = !filters?.status || paper.status === filters.status;
      const matchesArea = !filters?.researchArea || paper.researchArea === filters.researchArea;

      return matchesQuery && matchesStatus && matchesArea;
    });
  }

  private getAuthToken(): string {
    // In a real app, this would come from your auth system
    return localStorage.getItem('auth_token') || 'fake-token';
  }

  private getDefaultResearchPhases(paperId: string): ResearchPhase[] {
    return [
      {
        id: '2',
        name: 'Hypothesis Formation',
        status: 'completed',
        progress: 100,
        startDate: new Date('2024-02-20'),
        dueDate: new Date('2024-03-15'),
        estimatedHours: 40,
        actualHours: 45,
        tasks: [],
        paperId,
      },
      {
        id: '3',
        name: 'Methodology Design',
        status: 'in-progress',
        progress: 75,
        startDate: new Date('2024-03-10'),
        dueDate: new Date('2024-04-30'),
        estimatedHours: 120,
        actualHours: 90,
        tasks: [],
        paperId,
      },
      {
        id: '4',
        name: 'Data Collection',
        status: 'pending',
        progress: 0,
        startDate: new Date('2024-05-01'),
        dueDate: new Date('2024-07-31'),
        estimatedHours: 200,
        actualHours: 0,
        tasks: [],
        paperId,
      },
      {
        id: '5',
        name: 'Analysis & Results',
        status: 'pending',
        progress: 0,
        startDate: new Date('2024-08-01'),
        dueDate: new Date('2024-10-31'),
        estimatedHours: 150,
        actualHours: 0,
        tasks: [],
        paperId,
      },
      {
        id: '6',
        name: 'Paper Writing',
        status: 'pending',
        progress: 0,
        startDate: new Date('2024-11-01'),
        dueDate: new Date('2024-12-31'),
        estimatedHours: 100,
        actualHours: 0,
        tasks: [],
        paperId,
      }
    ];
  }
}

export const paperService = new PaperService();
        id: '1',
        name: 'Literature Review',
        status: 'completed',
        progress: 100,
        startDate: new Date('2024-01-15'),
        dueDate: new Date('2024-02-28'),
        estimatedHours: 80,
        actualHours: 85,
        tasks: [],
        paperId,
      },