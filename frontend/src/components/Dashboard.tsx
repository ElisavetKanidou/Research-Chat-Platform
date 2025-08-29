import React from 'react';
import { FileText, Clock, CheckCircle, Users, Calendar, TrendingUp, AlertCircle, Plus, ArrowRight } from 'lucide-react';
import { useGlobalContext } from '../App';

interface DashboardProps {
  onPaperSelect: (paper: any) => void;
  onNewPaper: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onPaperSelect, onNewPaper }) => {
  const { papers } = useGlobalContext();

  // Calculate statistics
  const activePapers = papers.filter(p => ['draft', 'in-progress', 'in-review', 'revision'].includes(p.status));
  const publishedPapers = papers.filter(p => p.status === 'published');
  const totalWordCount = papers.reduce((sum, p) => sum + p.currentWordCount, 0);
  const avgProgress = papers.length > 0 ? Math.round(papers.reduce((sum, p) => sum + p.progress, 0) / papers.length) : 0;

  // Get recent activity (papers modified in last 7 days)
  const recentActivity = papers
    .filter(p => {
      const daysDiff = Math.ceil((new Date().getTime() - p.lastModified.getTime()) / (1000 * 60 * 60 * 24));
      return daysDiff <= 7;
    })
    .sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime())
    .slice(0, 5);

  // Get upcoming deadlines (mock data - in real app would come from tasks/milestones)
  const upcomingDeadlines = [
    { id: '1', title: 'Submit Chapter 3 - ML Healthcare Paper', dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), paperId: '1' },
    { id: '2', title: 'Peer Review Response - NLP Paper', dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), paperId: '2' },
    { id: '3', title: 'Conference Presentation Prep', dueDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), paperId: '1' }
  ];

  // Get papers needing attention
  const papersNeedingAttention = papers.filter(p => 
    p.status === 'in-review' || p.status === 'revision' || 
    (p.status === 'in-progress' && p.progress < 50 && 
     Math.ceil((new Date().getTime() - p.lastModified.getTime()) / (1000 * 60 * 60 * 24)) > 7)
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700';
      case 'in-progress': return 'bg-blue-100 text-blue-700';
      case 'in-review': return 'bg-yellow-100 text-yellow-700';
      case 'revision': return 'bg-orange-100 text-orange-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'published': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const hours = Math.ceil((new Date().getTime() - date.getTime()) / (1000 * 60 * 60));
    if (hours < 24) return `${hours}h ago`;
    const days = Math.ceil(hours / 24);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString();
  };

  const getDaysUntil = (date: Date) => {
    const days = Math.ceil((date.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back!</h1>
          <p className="text-gray-600">Here's what's happening with your research projects.</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Papers</p>
                <p className="text-3xl font-bold text-blue-600">{activePapers.length}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <FileText className="text-blue-600" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-green-600">
              <TrendingUp size={16} className="mr-1" />
              <span>{publishedPapers.length} published</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Words</p>
                <p className="text-3xl font-bold text-green-600">{totalWordCount.toLocaleString()}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <FileText className="text-green-600" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-gray-500">
              <span>Across all papers</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Progress</p>
                <p className="text-3xl font-bold text-purple-600">{avgProgress}%</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="text-purple-600" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-gray-500">
              <span>All active projects</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Collaborators</p>
                <p className="text-3xl font-bold text-orange-600">
                  {[...new Set(papers.flatMap(p => p.coAuthors))].length}
                </p>
              </div>
              <div className="p-3 bg-orange-100 rounded-full">
                <Users className="text-orange-600" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-gray-500">
              <span>Unique co-authors</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activity */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
              <Clock size={18} className="text-gray-400" />
            </div>
            <div className="space-y-3">
              {recentActivity.length > 0 ? (
                recentActivity.map((paper) => (
                  <div
                    key={paper.id}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                    onClick={() => onPaperSelect(paper)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded">
                        <FileText size={16} className="text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 truncate max-w-64">{paper.title}</p>
                        <p className="text-sm text-gray-500">Modified {formatTimeAgo(paper.lastModified)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                        {paper.status}
                      </span>
                      <ArrowRight size={16} className="text-gray-400" />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-gray-500">
                  <FileText size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No recent activity</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={onNewPaper}
                className="w-full flex items-center gap-3 p-4 text-left hover:bg-blue-50 rounded-lg border-2 border-dashed border-blue-200 transition-colors"
              >
                <div className="p-2 bg-blue-100 rounded">
                  <Plus size={18} className="text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-blue-900">Start New Paper</p>
                  <p className="text-sm text-blue-600">Create a new research paper</p>
                </div>
              </button>

              {activePapers.length > 0 && (
                <button
                  onClick={() => onPaperSelect(activePapers[0])}
                  className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 rounded-lg border transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded">
                      <FileText size={18} className="text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Continue Recent Work</p>
                      <p className="text-sm text-gray-600 truncate max-w-48">{activePapers[0].title}</p>
                    </div>
                  </div>
                  <ArrowRight size={16} className="text-gray-400" />
                </button>
              )}

              <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded">
                    <TrendingUp size={18} className="text-purple-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Research Insights</p>
                    <p className="text-sm text-gray-600">View your analytics dashboard</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Upcoming Deadlines */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Upcoming Deadlines</h3>
              <Calendar size={18} className="text-gray-400" />
            </div>
            <div className="space-y-3">
              {upcomingDeadlines.slice(0, 4).map((deadline) => {
                const days = getDaysUntil(deadline.dueDate);
                const paper = papers.find(p => p.id === deadline.paperId);
                return (
                  <div key={deadline.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{deadline.title}</p>
                      <p className="text-sm text-gray-500">{paper?.title}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${
                        days <= 3 ? 'text-red-600' : days <= 7 ? 'text-yellow-600' : 'text-gray-600'
                      }`}>
                        {days <= 0 ? 'Overdue' : `${days} days`}
                      </p>
                      <p className="text-xs text-gray-500">{deadline.dueDate.toLocaleDateString()}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Papers Needing Attention */}
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Needs Attention</h3>
              <AlertCircle size={18} className="text-orange-500" />
            </div>
            <div className="space-y-3">
              {papersNeedingAttention.length > 0 ? (
                papersNeedingAttention.map((paper) => (
                  <div
                    key={paper.id}
                    className="flex items-center justify-between p-3 hover:bg-orange-50 rounded-lg cursor-pointer border-l-3 border-orange-200"
                    onClick={() => onPaperSelect(paper)}
                  >
                    <div>
                      <p className="font-medium text-gray-900 truncate max-w-48">{paper.title}</p>
                      <p className="text-sm text-orange-600">
                        {paper.status === 'in-review' ? 'Awaiting review' : 
                         paper.status === 'revision' ? 'Needs revision' : 
                         'Stale - no recent progress'}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                        {paper.status}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{paper.progress}% done</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-gray-500">
                  <CheckCircle size={32} className="mx-auto mb-2 text-green-500 opacity-50" />
                  <p>All papers are up to date!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;