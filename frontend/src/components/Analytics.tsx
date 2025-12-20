// components/Analytics.tsx - COMPLETE FIXED VERSION
import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, BookOpen, Award, Calendar, FileText, Clock, Target, Download } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import { analyticsService } from '../services/analyticsService';
import type { AnalyticsOverview, ProductivityAnalytics, CollaborationAnalytics, ResearchImpact } from '../services/analyticsService';

const Analytics: React.FC = () => {
  const { papers } = useGlobalContext();
  const [timeFrame, setTimeFrame] = useState<'month' | 'quarter' | 'year' | 'all'>('quarter');
  const [activeTab, setActiveTab] = useState<'overview' | 'productivity' | 'collaboration' | 'research'>('overview');
  
  // Real data from backend
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [productivity, setProductivity] = useState<ProductivityAnalytics | null>(null);
  const [collaboration, setCollaboration] = useState<CollaborationAnalytics | null>(null);
  const [researchImpact, setResearchImpact] = useState<ResearchImpact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load analytics data
  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [overviewData, productivityData, collaborationData, impactData] = await Promise.all([
        analyticsService.getOverview(),
        analyticsService.getProductivity(6),
        analyticsService.getCollaboration(),
        analyticsService.getResearchImpact()
      ]);
      
      setOverview(overviewData);
      setProductivity(productivityData);
      setCollaboration(collaborationData);
      setResearchImpact(impactData);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data. Using local data.');
    } finally {
      setLoading(false);
    }
  };

  // Fallback to local papers data if backend fails
  const safePapers = papers.map(p => ({
    ...p,
    createdAt: p.createdAt instanceof Date ? p.createdAt : new Date(p.createdAt),
    lastModified: (p as any).updated_at ? new Date((p as any).updated_at) :
                   p.lastModified instanceof Date ? p.lastModified : new Date(p.lastModified),
    deadline: p.deadline ? (p.deadline instanceof Date ? p.deadline : new Date(p.deadline)) : undefined
  }));

  // Local stats as fallback
  const localStats = {
    totalPapers: safePapers.length,
    publishedPapers: safePapers.filter(p => p.status === 'published').length,
    inProgressPapers: safePapers.filter(p => ['draft', 'in-progress', 'in-review', 'revision'].includes(p.status)).length,
    totalWords: safePapers.reduce((sum, p) => ((p as any).current_word_count || p.currentWordCount || 0) + sum, 0),
    totalCollaborators: safePapers.reduce((sum, p) => sum + ((p as any).collaborator_count || p.collaboratorCount || 0), 0),
    researchAreas: [...new Set(safePapers.map(p => (p as any).research_area || p.researchArea).filter(Boolean))].length,
    avgProgress: safePapers.length > 0 ? Math.round(safePapers.reduce((sum, p) => sum + p.progress, 0) / safePapers.length) : 0,
    completionRate: safePapers.length > 0 ? Math.round((safePapers.filter(p => p.status === 'published').length / safePapers.length) * 100) : 0
  };

  // Use backend data if available, otherwise use local
  const stats = overview ? {
    totalPapers: overview.total_papers,
    publishedPapers: overview.published_papers,
    inProgressPapers: overview.active_papers,
    totalWords: overview.total_words,
    avgProgress: overview.average_progress,
    totalCollaborators: collaboration?.total_collaborators || localStats.totalCollaborators,
    researchAreas: researchImpact?.research_areas.length || localStats.researchAreas,
    completionRate: overview.total_papers > 0 ? Math.round((overview.published_papers / overview.total_papers) * 100) : 0
  } : localStats;

  const exportAnalytics = () => {
    const data = {
      overview: overview || localStats,
      productivity,
      collaboration,
      researchImpact,
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const OverviewTab = () => {
    // Research areas from backend or local
    const researchAreasData = researchImpact?.research_areas.reduce((acc, item) => {
      acc[item.area] = item.papers;
      return acc;
    }, {} as Record<string, number>) || safePapers.reduce((acc, paper) => {
      const area = (paper as any).research_area || paper.researchArea;
      if (area) {
        acc[area] = (acc[area] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    // Status distribution from backend
    const statusData = overview?.status_breakdown || safePapers.reduce((acc, paper) => {
      acc[paper.status] = (acc[paper.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return (
      <div className="space-y-6">
        {error && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">{error}</p>
          </div>
        )}

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Papers</p>
                <p className="text-2xl lg:text-3xl font-bold text-blue-600">{stats.totalPapers}</p>
              </div>
              <div className="p-2 lg:p-3 bg-blue-100 rounded-full">
                <FileText className="text-blue-600" size={20} />
              </div>
            </div>
            <div className="mt-3 lg:mt-4 flex items-center text-sm">
              <span className="text-green-600 font-medium">{stats.publishedPapers} published</span>
              <span className="text-gray-500 ml-2">({stats.completionRate}% completion rate)</span>
            </div>
          </div>

          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Words</p>
                <p className="text-2xl lg:text-3xl font-bold text-green-600">{stats.totalWords.toLocaleString()}</p>
              </div>
              <div className="p-2 lg:p-3 bg-green-100 rounded-full">
                <BookOpen className="text-green-600" size={20} />
              </div>
            </div>
            <div className="mt-3 lg:mt-4 flex items-center text-sm">
              {overview?.papers_this_month ? (
                <span className="text-green-600 font-medium">+{overview.papers_this_month} this month</span>
              ) : (
                <span className="text-gray-500">Real-time tracking</span>
              )}
            </div>
          </div>

          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Collaborators</p>
                <p className="text-2xl lg:text-3xl font-bold text-purple-600">{stats.totalCollaborators}</p>
              </div>
              <div className="p-2 lg:p-3 bg-purple-100 rounded-full">
                <Users className="text-purple-600" size={20} />
              </div>
            </div>
            <div className="mt-3 lg:mt-4 flex items-center text-sm text-gray-500">
              <span>Across {stats.researchAreas} research areas</span>
            </div>
          </div>

          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Progress</p>
                <p className="text-2xl lg:text-3xl font-bold text-orange-600">{stats.avgProgress}%</p>
              </div>
              <div className="p-2 lg:p-3 bg-orange-100 rounded-full">
                <Target className="text-orange-600" size={20} />
              </div>
            </div>
            <div className="mt-3 lg:mt-4 flex items-center text-sm text-gray-500">
              <span>{stats.inProgressPapers} papers in progress</span>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Research Areas Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Areas</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {Object.entries(researchAreasData).length > 0 ? (
                Object.entries(researchAreasData).map(([area, count]) => (
                  <div key={area}>
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span className="truncate pr-2">{area || 'Unspecified'}</span>
                      <span className="flex-shrink-0">{count} paper{count > 1 ? 's' : ''}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(count / Math.max(...Object.values(researchAreasData))) * 100}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No research areas data available</p>
                </div>
              )}
            </div>
          </div>

          {/* Status Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Paper Status Distribution</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {Object.entries(statusData).length > 0 ? (
                Object.entries(statusData).map(([status, count]) => {
                  const percentage = Math.round((count / stats.totalPapers) * 100);
                  const statusColors = {
                    'draft': 'bg-gray-500',
                    'in-progress': 'bg-blue-500',
                    'in-review': 'bg-yellow-500',
                    'revision': 'bg-orange-500',
                    'completed': 'bg-green-500',
                    'published': 'bg-purple-500',
                    'archived': 'bg-gray-400'
                  };
                  return (
                    <div key={status} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-4 h-4 rounded-full ${statusColors[status as keyof typeof statusColors] || 'bg-gray-400'}`} />
                        <span className="text-sm capitalize">{status.replace('-', ' ')}</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {count} ({percentage}%)
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <FileText size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No papers available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ProductivityTab = () => {
    // SAFE ACCESS to all productivity data
    const monthlyData = productivity?.monthly_data || [];
    const writingVelocity = productivity?.writing_velocity || { 
      words_per_week: 0, 
      change_from_last_month: 0 
    };
    const completionTime = productivity?.completion_time || { 
      average_months: 0, 
      fastest_months: 0 
    };

    return (
      <div className="space-y-6">
        {/* Monthly Productivity Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-4">
            <h3 className="text-lg font-semibold text-gray-900">Monthly Productivity</h3>
            <button
              onClick={loadAnalytics}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
            >
              Refresh Data
            </button>
          </div>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 sm:gap-4 overflow-x-auto">
            {monthlyData.length > 0 ? (
              monthlyData.map((data) => (
                <div key={`${data.month}-${data.year}`} className="text-center min-w-0">
                  <div className="mb-2">
                    <div className="relative h-20 sm:h-24 md:h-32 lg:h-40 bg-gray-100 rounded">
                      <div
                        className="absolute bottom-0 w-full bg-blue-500 rounded transition-all duration-500 ease-out"
                        style={{
                          height: `${(data.papers / Math.max(...monthlyData.map(d => d.papers))) * 100}%`
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-sm font-medium text-gray-900">{data.month}</div>
                  <div className="text-xs text-gray-500">{data.papers} papers</div>
                  <div className="text-xs text-gray-500">{(data.words / 1000).toFixed(0)}k words</div>
                </div>
              ))
            ) : (
              <div className="col-span-6 text-center py-8 text-gray-500">
                <BarChart3 size={32} className="mx-auto mb-2 opacity-50" />
                <p>No productivity data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Writing Velocity - FIXED with safe access */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900">Writing Velocity</h4>
              <Clock size={18} className="text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-blue-600">
              {writingVelocity.words_per_week.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">words/week average</div>
            {writingVelocity.change_from_last_month !== 0 && (
              <div className="mt-3 flex items-center text-sm text-green-600">
                <TrendingUp size={14} className="mr-1" />
                <span>+{writingVelocity.change_from_last_month}% from last month</span>
              </div>
            )}
          </div>

          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900">Completion Time</h4>
              <Calendar size={18} className="text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-green-600">
              {completionTime.average_months}
            </div>
            <div className="text-sm text-gray-600">months average per paper</div>
            {completionTime.fastest_months > 0 && (
              <div className="mt-3 flex items-center text-sm text-orange-600">
                <span>{completionTime.fastest_months} months fastest</span>
              </div>
            )}
          </div>

          <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border sm:col-span-2 lg:col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium text-gray-900">Active Papers</h4>
              <Target size={18} className="text-gray-400" />
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.inProgressPapers}</div>
            <div className="text-sm text-gray-600">currently in progress</div>
          </div>
        </div>

        {/* Research Timeline */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Timeline</h3>
          <div className="space-y-4 max-h-80 overflow-y-auto">
            {safePapers.slice(0, 5).length > 0 ? (
              safePapers.slice(0, 5).map((paper) => (
                <div key={paper.id} className="flex items-center gap-4">
                  <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full" />
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <span className="font-medium text-gray-900 truncate">{paper.title}</span>
                      <span className="text-sm text-gray-500 flex-shrink-0">
                        {paper.deadline
                          ? `Due ${paper.deadline.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}`
                          : paper.createdAt.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })
                        }
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {paper.status === 'published' ? 'Published' : `${paper.progress}% complete`}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Clock size={32} className="mx-auto mb-2 opacity-50" />
                <p>No research activity yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const CollaborationTab = () => {
    const topCollaborators = collaboration?.top_collaborators || [];

    return (
      <div className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Collaborators</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {topCollaborators.length > 0 ? (
              topCollaborators.map((collab, index) => (
                <div key={collab.name} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600 flex-shrink-0">
                      {collab.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-gray-900 truncate">{collab.name}</div>
                      <div className="text-sm text-gray-600">{collab.papers} collaboration{collab.papers > 1 ? 's' : ''}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${(collab.papers / Math.max(...topCollaborators.map(c => c.papers))) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-500">#{index + 1}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Users size={32} className="mx-auto mb-2 opacity-50" />
                <p>No collaborators yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Collaboration Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {collaboration?.total_collaborators || 0}
              </div>
              <div className="text-sm text-gray-600">Total Collaborators</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {collaboration?.collaborative_papers || 0}
              </div>
              <div className="text-sm text-gray-600">Collaborative Papers</div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border sm:col-span-2 lg:col-span-1">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {collaboration?.solo_papers || 0}
              </div>
              <div className="text-sm text-gray-600">Solo Papers</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const ResearchTab = () => (
    <div className="space-y-6">
      {/* Research Impact Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border text-center">
          <Award size={28} className="mx-auto text-yellow-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">
            {researchImpact?.total_citations || 0}
          </div>
          <div className="text-sm text-gray-600">Total Citations</div>
        </div>
        <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border text-center">
          <BarChart3 size={28} className="mx-auto text-green-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">
            {researchImpact?.h_index || 0}
          </div>
          <div className="text-sm text-gray-600">H-Index</div>
        </div>
        <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border text-center">
          <TrendingUp size={28} className="mx-auto text-blue-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">
            {researchImpact?.average_citations || 0}
          </div>
          <div className="text-sm text-gray-600">Avg Citations/Paper</div>
        </div>
        <div className="bg-white p-4 lg:p-6 rounded-lg shadow-sm border text-center">
          <FileText size={28} className="mx-auto text-purple-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">
            {researchImpact?.published_papers || stats.publishedPapers}
          </div>
          <div className="text-sm text-gray-600">Published Papers</div>
        </div>
      </div>

      {/* Recent Publications */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Publications</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {safePapers.filter(p => p.status === 'published').slice(0, 5).length > 0 ? (
            safePapers.filter(p => p.status === 'published').slice(0, 5).map((paper) => (
              <div key={paper.id} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg">
                <div className="p-2 bg-green-100 rounded flex-shrink-0">
                  <FileText size={16} className="text-green-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-900 truncate">{paper.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {(paper as any).research_area || paper.researchArea} • {((paper as any).current_word_count || paper.currentWordCount).toLocaleString()} words
                  </p>
                  <div className="flex flex-wrap items-center gap-2 mt-2 text-xs text-gray-500">
                    <span>Published {paper.lastModified.toLocaleDateString()}</span>
                    {((paper as any).collaborator_count || paper.collaboratorCount || 0) > 0 && (
                      <>
                        <span>•</span>
                        <span>{(paper as any).collaborator_count || paper.collaboratorCount} collaborator{((paper as any).collaborator_count || paper.collaboratorCount) > 1 ? 's' : ''}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText size={32} className="mx-auto mb-2 opacity-50" />
              <p>No published papers yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full overflow-hidden flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 lg:p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
              <p className="text-gray-600">Track your research progress and discover patterns</p>
            </div>
            <button
              onClick={exportAnalytics}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors w-full sm:w-auto justify-center"
            >
              <Download size={18} />
              Export Report
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white p-1 rounded-lg shadow-sm border overflow-x-auto">
            <div className="flex space-x-1 min-w-max">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'productivity', label: 'Productivity', icon: TrendingUp },
                { id: 'collaboration', label: 'Collaboration', icon: Users },
                { id: 'research', label: 'Research Impact', icon: Award }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id as any)}
                  className={`flex items-center gap-2 px-3 lg:px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                    activeTab === id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={18} />
                  <span className="hidden sm:inline">{label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="min-h-0">
            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'productivity' && <ProductivityTab />}
            {activeTab === 'collaboration' && <CollaborationTab />}
            {activeTab === 'research' && <ResearchTab />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;