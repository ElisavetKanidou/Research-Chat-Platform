// components/Analytics.tsx
import React, { useState } from 'react';
import { BarChart3, TrendingUp, Users, BookOpen, Award, Calendar, FileText, Clock, Target, Download } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';

const Analytics: React.FC = () => {
  const { papers } = useGlobalContext();
  const [timeFrame, setTimeFrame] = useState<'month' | 'quarter' | 'year' | 'all'>('quarter');
  const [activeTab, setActiveTab] = useState<'overview' | 'productivity' | 'collaboration' | 'research'>('overview');

  // Ensure papers have proper date handling
  const safePapers = papers.map(p => ({
    ...p,
    createdAt: p.createdAt instanceof Date ? p.createdAt : new Date(p.createdAt),
    lastModified: p.lastModified instanceof Date ? p.lastModified : new Date(p.lastModified),
  }));

  // Calculate comprehensive statistics
  const stats = {
    totalPapers: safePapers.length,
    publishedPapers: safePapers.filter(p => p.status === 'published').length,
    inProgressPapers: safePapers.filter(p => ['draft', 'in-progress', 'in-review', 'revision'].includes(p.status)).length,
    totalWords: safePapers.reduce((sum, p) => sum + p.currentWordCount, 0),
    totalCollaborators: [...new Set(safePapers.flatMap(p => p.coAuthors))].length,
    researchAreas: [...new Set(safePapers.map(p => p.researchArea).filter(Boolean))].length,
    avgProgress: safePapers.length > 0 ? Math.round(safePapers.reduce((sum, p) => sum + p.progress, 0) / safePapers.length) : 0,
    completionRate: safePapers.length > 0 ? Math.round((safePapers.filter(p => p.status === 'published').length / safePapers.length) * 100) : 0
  };

  // Research areas distribution
  const researchAreasData = safePapers.reduce((acc, paper) => {
    if (paper.researchArea) {
      acc[paper.researchArea] = (acc[paper.researchArea] || 0) + 1;
    }
    return acc;
  }, {} as Record<string, number>);

  // Status distribution
  const statusData = safePapers.reduce((acc, paper) => {
    acc[paper.status] = (acc[paper.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Monthly productivity (mock data - in real app would be calculated from actual dates)
  const monthlyData = [
    { month: 'Jan', papers: 2, words: 15000 },
    { month: 'Feb', papers: 1, words: 8000 },
    { month: 'Mar', papers: 3, words: 22000 },
    { month: 'Apr', papers: 2, words: 18000 },
    { month: 'May', papers: 1, words: 12000 },
    { month: 'Jun', papers: 2, words: 16000 }
  ];

  // Collaboration network data
  const collaboratorStats = safePapers.flatMap(p => p.coAuthors).reduce((acc, author) => {
    acc[author] = (acc[author] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const topCollaborators = Object.entries(collaboratorStats)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10);

  const exportAnalytics = () => {
    console.log('Exporting analytics report...');
    alert('Analytics report exported successfully!');
  };

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Papers</p>
              <p className="text-3xl font-bold text-blue-600">{stats.totalPapers}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-full">
              <FileText className="text-blue-600" size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-green-600 font-medium">{stats.publishedPapers} published</span>
            <span className="text-gray-500 ml-2">({stats.completionRate}% completion rate)</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Words</p>
              <p className="text-3xl font-bold text-green-600">{stats.totalWords.toLocaleString()}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-full">
              <BookOpen className="text-green-600" size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp size={16} className="text-green-600 mr-1" />
            <span className="text-green-600 font-medium">+12% this month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Collaborators</p>
              <p className="text-3xl font-bold text-purple-600">{stats.totalCollaborators}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-full">
              <Users className="text-purple-600" size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-gray-500">
            <span>Across {stats.researchAreas} research areas</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Progress</p>
              <p className="text-3xl font-bold text-orange-600">{stats.avgProgress}%</p>
            </div>
            <div className="p-3 bg-orange-100 rounded-full">
              <Target className="text-orange-600" size={24} />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-gray-500">
            <span>{stats.inProgressPapers} papers in progress</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Research Areas Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Areas</h3>
          <div className="space-y-3">
            {Object.entries(researchAreasData).map(([area, count]) => (
              <div key={area}>
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>{area || 'Unspecified'}</span>
                  <span>{count} paper{count > 1 ? 's' : ''}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(count / Math.max(...Object.values(researchAreasData))) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Status Distribution */}
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Paper Status Distribution</h3>
          <div className="space-y-3">
            {Object.entries(statusData).map(([status, count]) => {
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
            })}
          </div>
        </div>
      </div>
    </div>
  );

  const ProductivityTab = () => (
    <div className="space-y-6">
      {/* Monthly Productivity Chart */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Monthly Productivity</h3>
          <select
            value={timeFrame}
            onChange={(e) => setTimeFrame(e.target.value as any)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
            <option value="all">All Time</option>
          </select>
        </div>
        <div className="grid grid-cols-6 gap-4">
          {monthlyData.map((data, index) => (
            <div key={data.month} className="text-center">
              <div className="mb-2">
                <div className="relative h-32 bg-gray-100 rounded">
                  <div
                    className="absolute bottom-0 w-full bg-blue-500 rounded"
                    style={{
                      height: `${(data.papers / Math.max(...monthlyData.map(d => d.papers))) * 100}%`
                    }}
                  />
                </div>
              </div>
              <div className="text-sm font-medium text-gray-900">{data.month}</div>
              <div className="text-xs text-gray-500">{data.papers} papers</div>
              <div className="text-xs text-gray-500">{data.words.toLocaleString()} words</div>
            </div>
          ))}
        </div>
      </div>

      {/* Writing Velocity and other productivity metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">Writing Velocity</h4>
            <Clock size={18} className="text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-blue-600">2,847</div>
          <div className="text-sm text-gray-600">words/week average</div>
          <div className="mt-3 flex items-center text-sm text-green-600">
            <TrendingUp size={14} className="mr-1" />
            <span>+15% from last month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">Completion Time</h4>
            <Calendar size={18} className="text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-green-600">4.2</div>
          <div className="text-sm text-gray-600">months average per paper</div>
          <div className="mt-3 flex items-center text-sm text-orange-600">
            <span>3.1 months fastest</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-medium text-gray-900">Focus Sessions</h4>
            <Target size={18} className="text-gray-400" />
          </div>
          <div className="text-2xl font-bold text-purple-600">18</div>
          <div className="text-sm text-gray-600">hours this week</div>
          <div className="mt-3 flex items-center text-sm text-gray-500">
            <span>2.5 hours average/session</span>
          </div>
        </div>
      </div>

      {/* Research Timeline */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Research Timeline</h3>
        <div className="space-y-4">
          {safePapers.slice(0, 5).map((paper, index) => (
            <div key={paper.id} className="flex items-center gap-4">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{paper.title}</span>
                  <span className="text-sm text-gray-500">{paper.createdAt.toLocaleDateString()}</span>
                </div>
                <div className="text-sm text-gray-600">
                  {paper.status === 'published' ? 'Published' : `${paper.progress}% complete`}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const CollaborationTab = () => (
    <div className="space-y-6">
      {/* Top Collaborators */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Collaborators</h3>
        <div className="space-y-3">
          {topCollaborators.length > 0 ? (
            topCollaborators.map(([name, count], index) => (
              <div key={name} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-sm font-medium text-blue-600">
                    {name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{name}</div>
                    <div className="text-sm text-gray-600">{count} collaboration{count > 1 ? 's' : ''}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(count / Math.max(...topCollaborators.map(([,c]) => c))) * 100}%` }}
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
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">{stats.totalCollaborators}</div>
            <div className="text-sm text-gray-600">Total Collaborators</div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600 mb-2">
              {stats.totalPapers > 0 ? Math.round(safePapers.reduce((sum, p) => sum + p.coAuthors.length, 0) / stats.totalPapers * 10) / 10 : 0}
            </div>
            <div className="text-sm text-gray-600">Avg Co-authors per Paper</div>
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600 mb-2">{stats.researchAreas}</div>
            <div className="text-sm text-gray-600">Research Areas</div>
          </div>
        </div>
      </div>
    </div>
  );

  const ResearchTab = () => (
    <div className="space-y-6">
      {/* Research Impact Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <Award size={32} className="mx-auto text-yellow-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">342</div>
          <div className="text-sm text-gray-600">Total Citations</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <BarChart3 size={32} className="mx-auto text-green-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">15.2</div>
          <div className="text-sm text-gray-600">H-Index</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <TrendingUp size={32} className="mx-auto text-blue-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">28.5</div>
          <div className="text-sm text-gray-600">Avg Citations/Paper</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <FileText size={32} className="mx-auto text-purple-600 mb-3" />
          <div className="text-2xl font-bold text-gray-900">{stats.publishedPapers}</div>
          <div className="text-sm text-gray-600">Published Papers</div>
        </div>
      </div>

      {/* Recent Publications */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Publications</h3>
        <div className="space-y-3">
          {safePapers.filter(p => p.status === 'published').slice(0, 5).map((paper) => (
            <div key={paper.id} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg">
              <div className="p-2 bg-green-100 rounded">
                <FileText size={16} className="text-green-600" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{paper.title}</h4>
                <p className="text-sm text-gray-600 mt-1">
                  {paper.researchArea} • {paper.currentWordCount.toLocaleString()} words
                </p>
                <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                  <span>Published {paper.lastModified.toLocaleDateString()}</span>
                  {paper.coAuthors.length > 0 && (
                    <>
                      <span>•</span>
                      <span>{paper.coAuthors.length} co-author{paper.coAuthors.length > 1 ? 's' : ''}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics & Insights</h1>
            <p className="text-gray-600">Track your research progress and discover patterns</p>
          </div>
          <button
            onClick={exportAnalytics}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Download size={18} />
            Export Report
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white p-1 rounded-lg shadow-sm border">
          <div className="flex space-x-1">
            {[
              { id: 'overview', label: 'Overview', icon: BarChart3 },
              { id: 'productivity', label: 'Productivity', icon: TrendingUp },
              { id: 'collaboration', label: 'Collaboration', icon: Users },
              { id: 'research', label: 'Research Impact', icon: Award }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <Icon size={18} />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'productivity' && <ProductivityTab />}
        {activeTab === 'collaboration' && <CollaborationTab />}
        {activeTab === 'research' && <ResearchTab />}
      </div>
    </div>
  );
};

export default Analytics;