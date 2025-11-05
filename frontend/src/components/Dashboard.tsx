// components/Dashboard.tsx
import React from 'react';
import { FileText, Clock, CheckCircle, Users, Calendar, TrendingUp, AlertCircle, Plus, ArrowRight } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import type { Paper } from '../types/paper';

interface Deadline {
  id: string;
  title: string;
  dueDate: Date;
  paperId: string;
}

interface DashboardProps {
  onPaperSelect: (paper: Paper) => void;
  onNewPaper: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onPaperSelect, onNewPaper }) => {
  const { papers, loading, error, user } = useGlobalContext();

  // Show loading state
  if (loading) {
    return (
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-64 mb-4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="h-16 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error loading dashboard</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Helper functions for safe field access
  const getCurrentWordCount = (p: any) => p.current_word_count || p.currentWordCount || 0;
  const getLastModified = (p: any) => {
    const date = p.updated_at || p.lastModified || p.createdAt;
    return date instanceof Date ? date : new Date(date);
  };
  const getCreatedAt = (p: any) => {
    const date = p.created_at || p.createdAt;
    return date instanceof Date ? date : new Date(date);
  };

  const safePapers = papers.map(p => ({
    ...p,
    lastModified: getLastModified(p),
    createdAt: getCreatedAt(p),
    currentWordCount: getCurrentWordCount(p)
  }));

  // Calculate statistics
  const activePapers = safePapers.filter(p => ['draft', 'in-progress', 'in-review', 'revision'].includes(p.status));
  const publishedPapers = safePapers.filter(p => p.status === 'published');
  const completedPapers = safePapers.filter(p => p.status === 'completed');
  const totalWordCount = safePapers.reduce((sum, p) => sum + p.currentWordCount, 0);
  const avgProgress = safePapers.length > 0 ? Math.round(safePapers.reduce((sum, p) => sum + p.progress, 0) / safePapers.length) : 0;

  // Get recent activity (papers modified in last 7 days)
  const recentActivity = safePapers
    .filter(p => {
      const daysDiff = Math.ceil((new Date().getTime() - p.lastModified.getTime()) / (1000 * 60 * 60 * 24));
      return daysDiff <= 7;
    })
    .sort((a, b) => b.lastModified.getTime() - a.lastModified.getTime())
    .slice(0, 5);

  // Get upcoming deadlines (mock data based on papers)
  const upcomingDeadlines: Deadline[] = safePapers
    .filter(p => ['in-progress', 'in-review', 'revision'].includes(p.status))
    .map((paper, index) => ({
      id: `deadline-${paper.id}`,
      title: `Complete ${paper.title}`,
      dueDate: new Date(Date.now() + (index + 1) * 7 * 24 * 60 * 60 * 1000), // Weekly intervals
      paperId: paper.id,
    }))
    .slice(0, 3);

  // Get papers needing attention
  const papersNeedingAttention = safePapers.filter(p =>
    p.status === 'in-review' ||
    p.status === 'revision' ||
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
      case 'archived': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatTimeAgo = (date: Date) => {
    const hours = Math.ceil((new Date().getTime() - date.getTime()) / (1000 * 60 * 60));
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    const days = Math.ceil(hours / 24);
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.ceil(days / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const getDaysUntil = (date: Date) => {
    const days = Math.ceil((date.getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="h-full overflow-hidden flex flex-col">
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back{user ? `, ${user.name}` : ''}!
              </h1>
              <p className="text-gray-600">Here's an overview of your research progress and activities</p>
            </div>
            <button
              onClick={onNewPaper}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
            >
              <Plus size={16} />
              New Paper
            </button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Papers</p>
                  <p className="text-2xl font-semibold text-gray-900">{activePapers.length}</p>
                  <p className="text-xs text-blue-600 mt-1">In progress</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <FileText className="text-blue-600" size={24} />
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Published</p>
                  <p className="text-2xl font-semibold text-gray-900">{publishedPapers.length}</p>
                  <p className="text-xs text-green-600 mt-1">{completedPapers.length} completed</p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <CheckCircle className="text-green-600" size={24} />
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Words</p>
                  <p className="text-2xl font-semibold text-gray-900">{totalWordCount.toLocaleString()}</p>
                  <p className="text-xs text-purple-600 mt-1">Across all papers</p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <TrendingUp className="text-purple-600" size={24} />
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Avg Progress</p>
                  <p className="text-2xl font-semibold text-gray-900">{avgProgress}%</p>
                  <p className="text-xs text-orange-600 mt-1">Overall completion</p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <Clock className="text-orange-600" size={24} />
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Activity */}
            <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                <Clock size={18} className="text-gray-400" />
              </div>
              <div className="space-y-3">
                {recentActivity.length > 0 ? (
                  recentActivity.map((paper) => (
                    <div
                      key={paper.id}
                      className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer border border-transparent hover:border-gray-200 transition-all"
                      onClick={() => onPaperSelect(paper)}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-blue-50 rounded-lg">
                          <FileText size={16} className="text-blue-600" />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-gray-900 truncate max-w-64">{paper.title}</p>
                          <p className="text-sm text-gray-500">
                            {formatTimeAgo(paper.lastModified)} • {paper.currentWordCount.toLocaleString()} words
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(paper.status)}`}>
                          {paper.status.replace('-', ' ')}
                        </span>
                        <div className="w-8 h-2 bg-gray-200 rounded-full">
                          <div
                            className="h-2 bg-blue-500 rounded-full transition-all"
                            style={{ width: `${paper.progress}%` }}
                          />
                        </div>
                        <ArrowRight size={14} className="text-gray-400" />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FileText size={32} className="mx-auto mb-2 opacity-50" />
                    <p>No recent activity</p>
                    <p className="text-sm">Your recent paper edits will appear here</p>
                  </div>
                )}
              </div>
            </div>

            {/* Upcoming Deadlines */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Upcoming Deadlines</h3>
                <Calendar size={18} className="text-gray-500" />
              </div>
              <div className="space-y-3">
                {upcomingDeadlines.length > 0 ? (
                  upcomingDeadlines.map((deadline) => {
                    const daysUntil = getDaysUntil(deadline.dueDate);
                    return (
                      <div key={deadline.id} className="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                        <p className="font-medium text-gray-900 text-sm truncate">{deadline.title}</p>
                        <div className="flex items-center justify-between mt-2">
                          <p className="text-xs text-gray-500">
                            {deadline.dueDate.toLocaleDateString()}
                          </p>
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            daysUntil <= 3
                              ? 'bg-red-100 text-red-700'
                              : daysUntil <= 7
                              ? 'bg-yellow-100 text-yellow-700'
                              : 'bg-green-100 text-green-700'
                          }`}>
                            {daysUntil <= 0 ? 'Overdue' : `${daysUntil} days`}
                          </span>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <Calendar size={24} className="mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No upcoming deadlines</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Papers Needing Attention */}
          {papersNeedingAttention.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow-sm border border-orange-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Needs Attention</h3>
                <AlertCircle size={18} className="text-orange-500" />
              </div>
              <div className="space-y-3">
                {papersNeedingAttention.map((paper) => (
                  <div
                    key={paper.id}
                    className="flex items-center justify-between p-3 hover:bg-orange-50 rounded-lg cursor-pointer border-l-4 border-orange-200 transition-colors"
                    onClick={() => onPaperSelect(paper)}
                  >
                    <div className="min-w-0">
                      <p className="font-medium text-gray-900 truncate max-w-48">{paper.title}</p>
                      <p className="text-sm text-orange-600">
                        {paper.status === 'in-review' ? 'Awaiting review feedback' :
                          paper.status === 'revision' ? 'Needs revision based on feedback' :
                            'No progress in over a week'}
                      </p>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(paper.status)}`}>
                        {paper.status.replace('-', ' ')}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">{paper.progress}% complete</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={onNewPaper}
                className="flex items-center p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border"
              >
                <Plus size={20} className="text-blue-600 mr-3" />
                <span className="text-gray-700">Start New Research</span>
              </button>
              <button className="flex items-center p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border">
                <Users size={20} className="text-green-600 mr-3" />
                <span className="text-gray-700">Invite Collaborators</span>
              </button>
              <button className="flex items-center p-3 bg-white rounded-lg hover:bg-gray-50 transition-colors border">
                <TrendingUp size={20} className="text-purple-600 mr-3" />
                <span className="text-gray-700">View Analytics</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;