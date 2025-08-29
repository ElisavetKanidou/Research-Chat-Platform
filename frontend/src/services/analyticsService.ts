// services/analyticsService.ts
import { apiClient } from '../utils/apiHelpers';
import { 
  UserAnalytics, 
  PaperAnalytics, 
  ProductivityMetrics, 
  CollaborationAnalytics,
  ResearchTrend,
  WritingPattern,
  AnalyticsFilter,
  Insight,
  ComparisonMetric,
  AnalyticsTimeframe 
} from '../types/analytics';
import { AnalyticsResponse, AnalyticsRequest } from '../types/api';

class AnalyticsService {
  private readonly basePath = '/analytics';

  // Get user's overall analytics
  async getUserAnalytics(timeframe: AnalyticsTimeframe = 'month'): Promise<UserAnalytics> {
    try {
      const response = await apiClient.get<AnalyticsResponse>(`${this.basePath}/user`, {
        timeframe,
      });
      
      return this.transformToUserAnalytics(response);
    } catch (error) {
      console.error('Error fetching user analytics:', error);
      return this.getMockUserAnalytics();
    }
  }

  // Get analytics for specific paper
  async getPaperAnalytics(paperId: string): Promise<PaperAnalytics> {
    try {
      return await apiClient.get<PaperAnalytics>(`${this.basePath}/papers/${paperId}`);
    } catch (error) {
      console.error('Error fetching paper analytics:', error);
      return this.getMockPaperAnalytics(paperId);
    }
  }

  // Get productivity metrics over time
  async getProductivityMetrics(filter: AnalyticsFilter): Promise<ProductivityMetrics> {
    try {
      return await apiClient.post<ProductivityMetrics>(`${this.basePath}/productivity`, filter);
    } catch (error) {
      console.error('Error fetching productivity metrics:', error);
      return this.getMockProductivityMetrics();
    }
  }

  // Get collaboration analytics
  async getCollaborationAnalytics(): Promise<CollaborationAnalytics[]> {
    try {
      return await apiClient.get<CollaborationAnalytics[]>(`${this.basePath}/collaboration`);
    } catch (error) {
      console.error('Error fetching collaboration analytics:', error);
      return this.getMockCollaborationAnalytics();
    }
  }

  // Get research trends
  async getResearchTrends(): Promise<ResearchTrend[]> {
    try {
      return await apiClient.get<ResearchTrend[]>(`${this.basePath}/trends`);
    } catch (error) {
      console.error('Error fetching research trends:', error);
      return this.getMockResearchTrends();
    }
  }

  // Get writing patterns
  async getWritingPatterns(): Promise<WritingPattern> {
    try {
      return await apiClient.get<WritingPattern>(`${this.basePath}/writing-patterns`);
    } catch (error) {
      console.error('Error fetching writing patterns:', error);
      return this.getMockWritingPatterns();
    }
  }

  // Get AI insights
  async getInsights(): Promise<Insight[]> {
    try {
      return await apiClient.get<Insight[]>(`${this.basePath}/insights`);
    } catch (error) {
      console.error('Error fetching insights:', error);
      return this.getMockInsights();
    }
  }

  // Get comparison with benchmarks
  async getComparisons(): Promise<ComparisonMetric[]> {
    try {
      return await apiClient.get<ComparisonMetric[]>(`${this.basePath}/comparisons`);
    } catch (error) {
      console.error('Error fetching comparisons:', error);
      return this.getMockComparisons();
    }
  }

  // Export analytics data
  async exportAnalytics(format: 'csv' | 'json' | 'pdf', filter: AnalyticsFilter): Promise<Blob> {
    try {
      const response = await fetch(`${apiClient['baseUrl']}${this.basePath}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ format, filter }),
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

  // Private helper methods for mock data
  private transformToUserAnalytics(response: AnalyticsResponse): UserAnalytics {
    return {
      userId: response.userId,
      totalPapers: response.metrics.find(m => m.name === 'totalPapers')?.value || 0,
      publishedPapers: response.metrics.find(m => m.name === 'publishedPapers')?.value || 0,
      draftPapers: response.metrics.find(m => m.name === 'draftPapers')?.value || 0,
      inProgressPapers: response.metrics.find(m => m.name === 'inProgressPapers')?.value || 0,
      totalWords: response.metrics.find(m => m.name === 'totalWords')?.value || 0,
      avgProgress: response.metrics.find(m => m.name === 'avgProgress')?.value || 0,
      totalCollaborators: response.metrics.find(m => m.name === 'collaborators')?.value || 0,
      researchAreas: response.metrics.find(m => m.name === 'researchAreas')?.value || 0,
      avgCompletionTime: response.metrics.find(m => m.name === 'avgCompletionTime')?.value || 0,
      productivityScore: response.metrics.find(m => m.name === 'productivityScore')?.value || 0,
      lastUpdated: new Date(response.generatedAt),
    };
  }

  private getMockUserAnalytics(): UserAnalytics {
    return {
      userId: 'mock-user',
      totalPapers: 12,
      publishedPapers: 3,
      draftPapers: 2,
      inProgressPapers: 7,
      totalWords: 45620,
      avgProgress: 67,
      totalCollaborators: 8,
      researchAreas: 4,
      avgCompletionTime: 4.2,
      productivityScore: 78,
      lastUpdated: new Date(),
    };
  }

  private getMockPaperAnalytics(paperId: string): PaperAnalytics {
    return {
      paperId,
      wordCount: 5200,
      readingTime: 26,
      estimatedCompletionTime: 2.5,
      collaboratorCount: 2,
      sectionProgress: [
        {
          sectionId: '1',
          title: 'Introduction',
          wordCount: 800,
          status: 'completed',
          timeSpent: 4.5,
          lastModified: new Date(),
          revisions: 3,
        },
        {
          sectionId: '2',
          title: 'Literature Review',
          wordCount: 1500,
          status: 'completed',
          timeSpent: 8.2,
          lastModified: new Date(),
          revisions: 2,
        },
        {
          sectionId: '3',
          title: 'Methodology',
          wordCount: 1200,
          status: 'in-progress',
          timeSpent: 6.0,
          lastModified: new Date(),
          revisions: 1,
        },
      ],
      timeDistribution: [
        { date: '2024-01-15', wordsWritten: 500, timeSpent: 2.5, sessionsCount: 1 },
        { date: '2024-01-16', wordsWritten: 800, timeSpent: 3.2, sessionsCount: 2 },
        { date: '2024-01-17', wordsWritten: 650, timeSpent: 2.8, sessionsCount: 1 },
      ],
      citationCount: 0,
      revisionCount: 6,
      createdAt: new Date('2024-01-15'),
      lastModified: new Date(),
    };
  }

  private getMockProductivityMetrics(): ProductivityMetrics {
    return {
      daily: Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        wordsWritten: Math.floor(Math.random() * 1000) + 200,
        timeSpent: Math.floor(Math.random() * 6) + 1,
        papersWorkedOn: Math.floor(Math.random() * 3) + 1,
        sessionsCount: Math.floor(Math.random() * 4) + 1,
        focusScore: Math.floor(Math.random() * 40) + 60,
      })),
      weekly: [],
      monthly: [],
    };
  }

  private getMockCollaborationAnalytics(): CollaborationAnalytics[] {
    return [
      {
        collaboratorId: '1',
        name: 'Dr. Sarah Wilson',
        email: 'sarah.wilson@university.edu',
        sharedPapers: 3,
        totalContributions: 25,
        avgResponseTime: 2.5,
        collaborationStarted: new Date('2023-09-01'),
        lastActivity: new Date('2024-01-15'),
        contributionTypes: [
          { type: 'writing', count: 10, percentage: 40 },
          { type: 'review', count: 8, percentage: 32 },
          { type: 'editing', count: 7, percentage: 28 },
        ],
      },
    ];
  }

  private getMockResearchTrends(): ResearchTrend[] {
    return [
      {
        area: 'Machine Learning',
        paperCount: 5,
        wordCount: 28500,
        averageProgress: 72,
        timeSpent: 120,
        collaborators: ['Dr. Smith', 'Jane Doe'],
        publications: 2,
        citations: 45,
      },
      {
        area: 'Natural Language Processing',
        paperCount: 3,
        wordCount: 18200,
        averageProgress: 65,
        timeSpent: 85,
        collaborators: ['Prof. Johnson'],
        publications: 1,
        citations: 23,
      },
    ];
  }

  private getMockWritingPatterns(): WritingPattern {
    return {
      preferredTime: {
        hour: 9,
        dayOfWeek: 2,
        productivity: 85,
      },
      sessionLength: {
        average: 2.5,
        optimal: 3.0,
        distribution: [1, 2, 4, 6, 3, 2, 1],
      },
      writingVelocity: {
        wordsPerHour: 320,
        wordsPerSession: 800,
        consistency: 75,
      },
    };
  }

  private getMockInsights(): Insight[] {
    return [
      {
        id: '1',
        type: 'productivity',
        title: 'Peak Writing Hours',
        description: 'You are most productive between 9-11 AM, writing 40% more words during this time.',
        severity: 'info',
        actionable: true,
        suggestions: [
          'Schedule important writing tasks during your peak hours',
          'Block calendar time for deep work in the morning',
        ],
        dataPoints: [],
        generatedAt: new Date(),
      },
      {
        id: '2',
        type: 'writing',
        title: 'Collaboration Opportunity',
        description: 'Dr. Sarah Wilson has expertise that aligns with your current research direction.',
        severity: 'info',
        actionable: true,
        suggestions: [
          'Reach out to discuss potential collaboration',
          'Share your current draft for feedback',
        ],
        dataPoints: [],
        generatedAt: new Date(),
      },
    ];
  }

  private getMockComparisons(): ComparisonMetric[] {
    return [
      {
        label: 'Words per Week',
        userValue: 2847,
        benchmarkValue: 2200,
        percentile: 78,
        trend: 'improving',
      },
      {
        label: 'Papers per Year',
        userValue: 4,
        benchmarkValue: 3.2,
        percentile: 65,
        trend: 'stable',
      },
    ];
  }
}

export const analyticsService = new AnalyticsService();