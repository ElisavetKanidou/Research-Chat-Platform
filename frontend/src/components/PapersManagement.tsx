// components/PapersManagement.tsx
import React, { useState } from 'react';
import { useGlobalContext } from '../contexts/GlobalContext';
import type { Paper } from '../types/paper';

// ADDED: Imports for all used icons
import { 
  FileText, 
  MoreVertical, 
  Edit, 
  Copy, 
  Archive, 
  Trash2, 
  Clock, 
  Users, 
  Plus, 
  Search 
} from 'lucide-react';

interface PapersManagementProps {
  onPaperSelect: (paper: Paper) => void;
  onNewPaper: () => void;
}

type ViewMode = 'grid' | 'list';
type FilterStatus = 'all' | 'draft' | 'in-progress' | 'in-review' | 'revision' | 'completed' | 'published' | 'archived';
type SortBy = 'lastModified' | 'created' | 'title' | 'progress';

const PapersManagement: React.FC<PapersManagementProps> = ({ onPaperSelect, onNewPaper }) => {
  // FIX: Added createPaper to use for duplication
  const { papers, updatePaper, deletePaper, createPaper } = useGlobalContext();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [sortBy, setSortBy] = useState<SortBy>('lastModified');
  const [showDropdown, setShowDropdown] = useState<string | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-700';
      case 'in-progress': return 'bg-blue-100 text-blue-700';
      case 'in-review': return 'bg-yellow-100 text-yellow-700';
      case 'revision': return 'bg-orange-100 text-orange-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'published': return 'bg-purple-100 text-purple-700';
      case 'archived': return 'bg-gray-100 text-gray-500';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft': return '📝';
      case 'in-progress': return '⏳';
      case 'in-review': return '👁️';
      case 'revision': return '✏️';
      case 'completed': return '✅';
      case 'published': return '📚';
      case 'archived': return '📦';
      default: return '📄';
    }
  };

  // Filter and sort papers
  const filteredPapers = papers
    .filter(paper => {
      const matchesSearch = paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           paper.researchArea.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           paper.coAuthors.some(author => author.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesFilter = filterStatus === 'all' || paper.status === filterStatus;
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      // Ensure dates are valid before comparing
      const dateA = a.lastModified instanceof Date ? a.lastModified : new Date(a.lastModified);
      const dateB = b.lastModified instanceof Date ? b.lastModified : new Date(b.lastModified);
      const createdA = a.createdAt instanceof Date ? a.createdAt : new Date(a.createdAt);
      const createdB = b.createdAt instanceof Date ? b.createdAt : new Date(b.createdAt);

      switch (sortBy) {
        case 'lastModified':
          return dateB.getTime() - dateA.getTime();
        case 'created':
          return createdB.getTime() - createdA.getTime();
        case 'title':
          return a.title.localeCompare(b.title);
        case 'progress':
          return b.progress - a.progress;
        default:
          return 0;
      }
    });

  // FIX: Implemented duplication functionality using createPaper from context
  const handleDuplicatePaper = async (paper: Paper) => {
    try {
      await createPaper({
        ...paper,
        title: `${paper.title} (Copy)`,
        status: 'draft',
        progress: 0,
        currentWordCount: 0,
      });
    } catch (error) {
      console.error("Failed to duplicate paper:", error);
    } finally {
      setShowDropdown(null);
    }
  };

  const handleArchivePaper = (paperId: string) => {
    updatePaper(paperId, { status: 'archived' });
    setShowDropdown(null);
  };

  const handleDeletePaper = (paperId: string) => {
    if (window.confirm('Are you sure you want to delete this paper? This action cannot be undone.')) {
      deletePaper(paperId);
    }
    setShowDropdown(null);
  };

  const PaperCard = ({ paper }: { paper: Paper }) => (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 
              className="text-lg font-semibold text-gray-900 mb-2 cursor-pointer hover:text-blue-600 line-clamp-2"
              onClick={() => onPaperSelect(paper)}
            >
              {paper.title}
            </h3>
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                {getStatusIcon(paper.status)} {paper.status.replace('-', ' ')}
              </span>
              <span className="text-xs text-gray-500">
                {paper.researchArea}
              </span>
            </div>
          </div>
          <div className="relative">
            <button
              onClick={(e) => { e.stopPropagation(); setShowDropdown(showDropdown === paper.id ? null : paper.id); }}
              className="p-1 hover:bg-gray-100 rounded-full"
            >
              <MoreVertical size={16} className="text-gray-400" />
            </button>
            {showDropdown === paper.id && (
              <div className="absolute right-0 top-8 bg-white border rounded-lg shadow-lg py-2 w-48 z-10" onClick={e => e.stopPropagation()}>
                <button
                  onClick={() => onPaperSelect(paper)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Edit size={14} />
                  Edit Paper
                </button>
                <button
                  onClick={() => handleDuplicatePaper(paper)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Copy size={14} />
                  Duplicate
                </button>
                <button
                  onClick={() => handleArchivePaper(paper.id)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Archive size={14} />
                  Archive
                </button>
                <hr className="my-2" />
                <button
                  onClick={() => handleDeletePaper(paper.id)}
                  className="w-full px-4 py-2 text-left hover:bg-red-50 text-red-600 flex items-center gap-2"
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{paper.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${paper.progress}%` }}
            />
          </div>
        </div>

        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <FileText size={14} />
            <span>{paper.currentWordCount.toLocaleString()} / {paper.targetWordCount.toLocaleString()} words</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={14} />
            <span>Modified {(paper.lastModified instanceof Date ? paper.lastModified : new Date(paper.lastModified)).toLocaleDateString()}</span>
          </div>
          {paper.coAuthors.length > 0 && (
            <div className="flex items-center gap-2">
              <Users size={14} />
              <span>{paper.coAuthors.length} collaborator{paper.coAuthors.length > 1 ? 's' : ''}</span>
            </div>
          )}
        </div>

        <div className="mt-4 pt-4 border-t">
          <button
            onClick={() => onPaperSelect(paper)}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Continue Working
          </button>
        </div>
      </div>
    </div>
  );

  const PaperListItem = ({ paper }: { paper: Paper }) => (
    <div className="bg-white border rounded-lg p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="p-3 bg-blue-100 rounded-lg">
            <FileText size={20} className="text-blue-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 
              className="text-lg font-medium text-gray-900 cursor-pointer hover:text-blue-600 truncate"
              onClick={() => onPaperSelect(paper)}
            >
              {paper.title}
            </h3>
            <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                {paper.status.replace('-', ' ')}
              </span>
              <span>{paper.researchArea}</span>
              <span>{paper.currentWordCount.toLocaleString()} words</span>
              <span>Modified {(paper.lastModified instanceof Date ? paper.lastModified : new Date(paper.lastModified)).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm font-medium text-gray-900">{paper.progress}%</div>
            <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${paper.progress}%` }}
              />
            </div>
          </div>
          <div className="relative">
            <button
              onClick={(e) => { e.stopPropagation(); setShowDropdown(showDropdown === paper.id ? null : paper.id); }}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <MoreVertical size={16} className="text-gray-400" />
            </button>
            {showDropdown === paper.id && (
              <div className="absolute right-0 top-10 bg-white border rounded-lg shadow-lg py-2 w-48 z-10" onClick={e => e.stopPropagation()}>
                <button
                  onClick={() => onPaperSelect(paper)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Edit size={14} />
                  Edit Paper
                </button>
                <button
                  onClick={() => handleDuplicatePaper(paper)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Copy size={14} />
                  Duplicate
                </button>
                <button
                  onClick={() => handleArchivePaper(paper.id)}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Archive size={14} />
                  Archive
                </button>
                <hr className="my-2" />
                <button
                  onClick={() => handleDeletePaper(paper.id)}
                  className="w-full px-4 py-2 text-left hover:bg-red-50 text-red-600 flex items-center gap-2"
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-6" onClick={() => setShowDropdown(null)}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Papers Management</h1>
            <p className="text-gray-600">Manage all your research papers in one place</p>
          </div>
          <button
            onClick={onNewPaper}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            New Paper
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white p-4 rounded-lg shadow-sm border mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search size={18} className="absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Search papers by title, research area, or collaborators..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex gap-3">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="in-progress">In Progress</option>
                <option value="in-review">In Review</option>
                <option value="revision">Needs Revision</option>
                <option value="completed">Completed</option>
                <option value="published">Published</option>
                <option value="archived">Archived</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="lastModified">Last Modified</option>
                <option value="created">Date Created</option>
                <option value="title">Title</option>
                <option value="progress">Progress</option>
              </select>
              <div className="flex border border-gray-300 rounded-lg">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`px-3 py-2 rounded-l-lg ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  Grid
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`px-3 py-2 rounded-r-lg ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                >
                  List
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Papers Display */}
        {filteredPapers.length === 0 ? (
          <div className="text-center py-12">
            <FileText size={64} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No papers found</h3>
            <p className="text-gray-600 mb-6">
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter criteria.' 
                : 'Get started by creating your first research paper.'}
            </p>
            <button
              onClick={onNewPaper}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus size={20} />
              Create Your First Paper
            </button>
          </div>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
              : 'space-y-4'
          }>
            {filteredPapers.map((paper) => (
              viewMode === 'grid' 
                ? <PaperCard key={paper.id} paper={paper} />
                : <PaperListItem key={paper.id} paper={paper} />
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {filteredPapers.length > 0 && (
          <div className="mt-8 bg-white p-4 rounded-lg shadow-sm border">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Showing {filteredPapers.length} of {papers.length} papers
              </span>
              <div className="flex items-center gap-6">
                <span>
                  Total words: {filteredPapers.reduce((sum, p) => sum + p.currentWordCount, 0).toLocaleString()}
                </span>
                <span>
                  Avg progress: {filteredPapers.length > 0 ? Math.round(filteredPapers.reduce((sum, p) => sum + p.progress, 0) / filteredPapers.length) : 0}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PapersManagement;