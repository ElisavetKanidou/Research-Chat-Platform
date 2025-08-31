// services/paperService.ts
import type { Paper } from '../types/paper';
import { apiClient } from '../utils/apiHelpers';

class PaperService {
  private readonly basePath = '/papers';
  private readonly PAPERS_STORAGE_KEY = 'research_papers';

  async getAllPapers(): Promise<Paper[]> {
    try {
      const response = await apiClient.get<Paper[]>(this.basePath);
      return response;
    } catch (error) {
      console.log('API failed, using local storage fallback for papers');
      return this.getLocalPapers();
    }
  }

  async createPaper(paper: Paper): Promise<Paper> {
    try {
      const response = await apiClient.post<Paper>(this.basePath, paper);
      return response;
    } catch (error) {
      console.log('API failed, using local storage fallback for paper creation');
      return this.saveLocalPaper(paper);
    }
  }

  async updatePaper(paperId: string, updates: Partial<Paper>): Promise<Paper> {
    try {
      const response = await apiClient.patch<Paper>(`${this.basePath}/${paperId}`, updates);
      return response;
    } catch (error) {
      console.log('API failed, using local storage fallback for paper update');
      return this.updateLocalPaper(paperId, updates);
    }
  }

  async deletePaper(paperId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.basePath}/${paperId}`);
    } catch (error) {
      console.log('API failed, using local storage fallback for paper deletion');
      this.deleteLocalPaper(paperId);
    }
  }

  async getPaper(paperId: string): Promise<Paper> {
    try {
      const response = await apiClient.get<Paper>(`${this.basePath}/${paperId}`);
      return response;
    } catch (error) {
      console.log('API failed, using local storage fallback for paper retrieval');
      const paper = this.getLocalPaper(paperId);
      if (!paper) throw new Error('Paper not found');
      return paper;
    }
  }

  // Local storage fallback methods
  private getLocalPapers(): Paper[] {
    try {
      const stored = localStorage.getItem(this.PAPERS_STORAGE_KEY);
      if (!stored) return this.getDefaultPapers();
      
      const papers = JSON.parse(stored);
      return papers.map((paper: any) => ({
        ...paper,
        createdAt: new Date(paper.createdAt),
        lastModified: new Date(paper.lastModified),
        publicationDate: paper.publicationDate ? new Date(paper.publicationDate) : undefined,
        sections: paper.sections.map((section: any) => ({
          ...section,
          lastModified: new Date(section.lastModified),
        })),
      }));
    } catch (error) {
      console.error('Error loading papers from localStorage:', error);
      return this.getDefaultPapers();
    }
  }

  private saveLocalPaper(paper: Paper): Paper {
    const papers = this.getLocalPapers();
    papers.push(paper);
    this.saveLocalPapers(papers);
    return paper;
  }

  private updateLocalPaper(paperId: string, updates: Partial<Paper>): Paper {
    const papers = this.getLocalPapers();
    const index = papers.findIndex(p => p.id === paperId);
    
    if (index === -1) throw new Error('Paper not found');
    
    const updatedPaper = { ...papers[index], ...updates, lastModified: new Date() };
    papers[index] = updatedPaper;
    this.saveLocalPapers(papers);
    return updatedPaper;
  }

  private deleteLocalPaper(paperId: string): void {
    const papers = this.getLocalPapers();
    const filtered = papers.filter(p => p.id !== paperId);
    this.saveLocalPapers(filtered);
  }

  private getLocalPaper(paperId: string): Paper | null {
    const papers = this.getLocalPapers();
    return papers.find(p => p.id === paperId) || null;
  }

  private saveLocalPapers(papers: Paper[]): void {
    try {
      localStorage.setItem(this.PAPERS_STORAGE_KEY, JSON.stringify(papers));
    } catch (error) {
      console.error('Error saving papers to localStorage:', error);
    }
  }

  private getDefaultPapers(): Paper[] {
    return [
      {
        id: '1',
        title: 'Machine Learning in Healthcare: A Comprehensive Survey',
        abstract: 'This paper explores the applications of machine learning in healthcare, examining current trends, challenges, and future opportunities in medical AI.',
        status: 'in-progress',
        createdAt: new Date('2024-01-15T10:00:00Z'),
        lastModified: new Date('2024-01-20T14:30:00Z'),
        progress: 75,
        targetWordCount: 8000,
        currentWordCount: 4500,
        coAuthors: ['Dr. Smith', 'Dr. Johnson'],
        researchArea: 'Healthcare AI',
        sections: [
          { id: '1', title: 'Introduction', content: 'Healthcare AI introduction...', status: 'completed', lastModified: new Date(), wordCount: 800, order: 1 },
          { id: '2', title: 'Literature Review', content: 'Review of existing literature...', status: 'completed', lastModified: new Date(), wordCount: 1200, order: 2 },
          { id: '3', title: 'Methodology', content: 'Research methodology...', status: 'in-progress', lastModified: new Date(), wordCount: 900, order: 3 },
          { id: '4', title: 'Results', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 4 },
          { id: '5', title: 'Discussion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 5 },
          { id: '6', title: 'Conclusion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 6 }
        ],
        tags: ['machine learning', 'healthcare', 'AI'],
        isPublic: false,
      },
      {
        id: '2',
        title: 'Natural Language Processing for Clinical Data',
        abstract: 'An investigation into NLP techniques for processing and analyzing clinical text data to improve patient outcomes.',
        status: 'draft',
        createdAt: new Date('2024-01-10T09:00:00Z'),
        lastModified: new Date('2024-01-18T11:15:00Z'),
        progress: 30,
        targetWordCount: 6000,
        currentWordCount: 1200,
        coAuthors: ['Dr. Brown'],
        researchArea: 'Natural Language Processing',
        sections: [
          { id: '1', title: 'Introduction', content: 'NLP in clinical settings...', status: 'completed', lastModified: new Date(), wordCount: 600, order: 1 },
          { id: '2', title: 'Literature Review', content: 'Prior work in clinical NLP...', status: 'in-progress', lastModified: new Date(), wordCount: 600, order: 2 },
          { id: '3', title: 'Methodology', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 3 },
          { id: '4', title: 'Results', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 4 },
          { id: '5', title: 'Discussion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 5 },
          { id: '6', title: 'Conclusion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 6 }
        ],
        tags: ['NLP', 'clinical data', 'text processing'],
        isPublic: false,
      },
      {
        id: '3',
        title: 'Deep Learning for Medical Image Analysis',
        abstract: 'Comprehensive analysis of deep learning approaches for medical imaging, including CNN architectures and transfer learning.',
        status: 'published',
        createdAt: new Date('2023-12-01T08:00:00Z'),
        lastModified: new Date('2024-01-05T16:45:00Z'),
        progress: 100,
        targetWordCount: 9000,
        currentWordCount: 8200,
        coAuthors: ['Dr. Wilson', 'Dr. Lee'],
        researchArea: 'Medical Imaging',
        sections: [
          { id: '1', title: 'Introduction', content: 'Deep learning in medical imaging...', status: 'completed', lastModified: new Date(), wordCount: 1000, order: 1 },
          { id: '2', title: 'Literature Review', content: 'Comprehensive literature review...', status: 'completed', lastModified: new Date(), wordCount: 1500, order: 2 },
          { id: '3', title: 'Methodology', content: 'CNN architectures and methods...', status: 'completed', lastModified: new Date(), wordCount: 1800, order: 3 },
          { id: '4', title: 'Results', content: 'Experimental results and analysis...', status: 'completed', lastModified: new Date(), wordCount: 2200, order: 4 },
          { id: '5', title: 'Discussion', content: 'Discussion of findings...', status: 'completed', lastModified: new Date(), wordCount: 1200, order: 5 },
          { id: '6', title: 'Conclusion', content: 'Conclusions and future work...', status: 'completed', lastModified: new Date(), wordCount: 500, order: 6 }
        ],
        tags: ['deep learning', 'medical imaging', 'CNN'],
        isPublic: true,
        doi: '10.1000/example.doi',
        journal: 'Medical AI Journal',
        publicationDate: new Date('2024-01-05'),
        citationCount: 15,
      },
    ];
  }
}

export const paperService = new PaperService();