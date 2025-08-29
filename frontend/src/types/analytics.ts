// types/analytics.ts
export interface UserAnalytics {
  userId: string;
  totalPapers: number;
  publishedPapers: number;
  draftPapers: number;
  inProgressPapers: number;
  totalWords: number;
  avgProgress: number;
  totalCollaborators: number;
  researchAreas: number;
  avgCompletionTime: number;
  productivityScore: number;
  lastUpdated: Date;
}

export interface PaperAnalytics {
  paperId: string;
  wordCount: number;
  readingTime: number;
  estimatedCompletionTime: number;
  collaboratorCount: number;
  sectionProgress: SectionAnalytics[];
  timeDistribution: TimeDistribution[];
  citationCount: number;
  revisionCount: number;
  createdAt: Date;
  lastModified: Date;
}

export interface SectionAnalytics {
  sectionId: string;
  title: string;
  wordCount: number;
  status: string;
  timeSpent: number;
  lastModified: Date;
  revisions: number;
}

export interface TimeDistribution {
  date: string;
  wordsWritten: number;
  timeSpent: number;
  sessionsCount: number;
}

export interface ProductivityMetrics {
  daily: DailyMetric[];
  weekly: WeeklyMetric[];
  monthly: MonthlyMetric[];
}

export interface DailyMetric {
  date: string;
  wordsWritten: number;
  timeSpent: number;
  papersWorkedOn: number;
  sessionsCount: number;
  focusScore: number;
}

export interface WeeklyMetric {
  week: string;
  totalWords: number;
  totalTime: number;
  averageWordsPerDay: number;
  mostProductiveDay: string;
  papersProgress: number;
}

export interface MonthlyMetric {
  month: string;
  papersCompleted: number;
  totalWords: number;
  averageWordsPerWeek: number;
  collaborations: number;
  milestonesReached: number;
}

export interface CollaborationAnalytics {
  collaboratorId: string;
  name: string;
  email: string;
  sharedPapers: number;
  totalContributions: number;
  avgResponseTime: number;
  collaborationStarted: Date;
  lastActivity: Date;
  contributionTypes: ContributionType[];
}

export interface ContributionType {
  type: 'writing' | 'editing' | 'review' | 'methodology' | 'analysis';
  count: number;
  percentage: number;
}

export interface ResearchTrend {
  area: string;
  paperCount: number;
  wordCount: number;
  averageProgress: number;
  timeSpent: number;
  collaborators: string[];
  publications: number;
  citations: number;
}

export interface WritingPattern {
  preferredTime: {
    hour: number;
    dayOfWeek: number;
    productivity: number;
  };
  sessionLength: {
    average: number;
    optimal: number;
    distribution: number[];
  };
  writingVelocity: {
    wordsPerHour: number;
    wordsPerSession: number;
    consistency: number;
  };
}

export interface AnalyticsFilter {
  dateRange: {
    start: Date;
    end: Date;
  };
  paperIds?: string[];
  collaborators?: string[];
  researchAreas?: string[];
  status?: string[];
}

export interface AnalyticsExport {
  format: 'csv' | 'json' | 'pdf';
  data: any;
  generatedAt: Date;
  filters: AnalyticsFilter;
}

export interface Insight {
  id: string;
  type: 'productivity' | 'collaboration' | 'writing' | 'research';
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  actionable: boolean;
  suggestions: string[];
  dataPoints: any[];
  generatedAt: Date;
}

export interface ComparisonMetric {
  label: string;
  userValue: number;
  benchmarkValue: number;
  percentile: number;
  trend: 'improving' | 'declining' | 'stable';
}

export interface ResearchGoal {
  id: string;
  title: string;
  target: number;
  current: number;
  unit: string;
  deadline: Date;
  type: 'words' | 'papers' | 'time' | 'collaborations';
  priority: 'high' | 'medium' | 'low';
  achieved: boolean;
}

export type AnalyticsTimeframe = 'day' | 'week' | 'month' | 'quarter' | 'year' | 'all';
export type MetricType = 'papers' | 'words' | 'time' | 'collaborations' | 'productivity';
export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter';