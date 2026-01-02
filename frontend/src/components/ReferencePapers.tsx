// components/ReferencePapers.tsx
import React, { useState, useEffect } from 'react';
import {
  FileText,
  Upload,
  Trash2,
  RefreshCw,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Calendar,
  BookOpen,
  FlaskConical,
  User,
  BookMarked,
  MoreVertical,
  Download,
  Eye
} from 'lucide-react';
import {
  referencePapersService,
  type ReferencePaper,
  type PaperType,
  type ReferencePaperListResponse
} from '../services/referencePapersService';

interface ReferencePapersProps {
  onUploadClick: () => void;
  refreshTrigger?: number; // Add prop to trigger refresh from parent
}

type FilterType = 'all' | PaperType;

const ReferencePapers: React.FC<ReferencePapersProps> = ({ onUploadClick, refreshTrigger }) => {
  const [papers, setPapers] = useState<ReferencePaper[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [stats, setStats] = useState({
    total: 0,
    lab_papers_count: 0,
    personal_papers_count: 0,
    literature_papers_count: 0,
  });
  const [showDropdown, setShowDropdown] = useState<string | null>(null);
  const [reanalyzing, setReanalyzing] = useState<string | null>(null);

  useEffect(() => {
    loadReferencePapers();
  }, [filterType]);

  // Refresh when refreshTrigger changes (e.g., after successful upload)
  useEffect(() => {
    if (refreshTrigger) {
      loadReferencePapers();
    }
  }, [refreshTrigger]);

  const loadReferencePapers = async () => {
    try {
      setLoading(true);
      const response: ReferencePaperListResponse = await referencePapersService.getReferencePapers(
        filterType === 'all' ? undefined : filterType
      );

      setPapers(response.papers);
      setStats({
        total: response.total,
        lab_papers_count: response.lab_papers_count,
        personal_papers_count: response.personal_papers_count,
        literature_papers_count: response.literature_papers_count,
      });
    } catch (error) {
      console.error('Failed to load reference papers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (paperId: string) => {
    if (!confirm('Are you sure you want to delete this reference paper?')) {
      return;
    }

    try {
      await referencePapersService.deleteReferencePaper(paperId);
      await loadReferencePapers();
    } catch (error) {
      console.error('Failed to delete paper:', error);
      alert('Failed to delete paper. Please try again.');
    }
  };

  const handleReanalyze = async (paperId: string) => {
    try {
      setReanalyzing(paperId);
      await referencePapersService.reanalyzeReferencePaper(paperId);
      await loadReferencePapers();
    } catch (error) {
      console.error('Failed to reanalyze paper:', error);
      alert('Failed to reanalyze paper. Please try again.');
    } finally {
      setReanalyzing(null);
    }
  };

  const getPaperTypeIcon = (type: PaperType) => {
    switch (type) {
      case 'lab':
        return <FlaskConical className="w-5 h-5" />;
      case 'personal':
        return <User className="w-5 h-5" />;
      case 'literature':
        return <BookMarked className="w-5 h-5" />;
      default:
        return <FileText className="w-5 h-5" />;
    }
  };

  const getPaperTypeColor = (type: PaperType) => {
    switch (type) {
      case 'lab':
        return 'bg-blue-100 text-blue-700';
      case 'personal':
        return 'bg-green-100 text-green-700';
      case 'literature':
        return 'bg-purple-100 text-purple-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getPaperTypeLabel = (type: PaperType) => {
    switch (type) {
      case 'lab':
        return 'Lab Paper';
      case 'personal':
        return 'Personal Paper';
      case 'literature':
        return 'Literature';
      default:
        return type;
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const filteredPapers = papers.filter(paper => {
    const matchesSearch =
      paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      paper.authors?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      paper.research_area?.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-600" />
          <p className="text-gray-600">Loading reference papers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Reference Papers</h2>
            <p className="text-sm text-gray-600 mt-1">
              Manage papers used for AI writing style personalization
            </p>
          </div>
          <button
            onClick={onUploadClick}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            Upload Paper
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <BookOpen className="w-4 h-4" />
              <span className="text-sm font-medium">Total Papers</span>
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 cursor-pointer hover:bg-blue-100 transition-colors"
               onClick={() => setFilterType('lab')}>
            <div className="flex items-center gap-2 text-blue-600 mb-1">
              <FlaskConical className="w-4 h-4" />
              <span className="text-sm font-medium">Lab Papers</span>
            </div>
            <p className="text-2xl font-bold text-blue-900">{stats.lab_papers_count}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4 cursor-pointer hover:bg-green-100 transition-colors"
               onClick={() => setFilterType('personal')}>
            <div className="flex items-center gap-2 text-green-600 mb-1">
              <User className="w-4 h-4" />
              <span className="text-sm font-medium">Personal Papers</span>
            </div>
            <p className="text-2xl font-bold text-green-900">{stats.personal_papers_count}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 cursor-pointer hover:bg-purple-100 transition-colors"
               onClick={() => setFilterType('literature')}>
            <div className="flex items-center gap-2 text-purple-600 mb-1">
              <BookMarked className="w-4 h-4" />
              <span className="text-sm font-medium">Literature</span>
            </div>
            <p className="text-2xl font-bold text-purple-900">{stats.literature_papers_count}</p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by title, authors, or research area..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                filterType === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              }`}
            >
              All
            </button>
            <button
              onClick={loadReferencePapers}
              className="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Papers List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredPapers.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reference papers found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm ? 'Try a different search term' : 'Upload your first reference paper to get started'}
            </p>
            {!searchTerm && (
              <button
                onClick={onUploadClick}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Upload className="w-4 h-4" />
                Upload Paper
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredPapers.map((paper) => (
              <div
                key={paper.id}
                className="bg-white rounded-lg border border-gray-200 hover:shadow-lg transition-shadow overflow-hidden"
              >
                {/* Card Header */}
                <div className="p-4 border-b border-gray-100">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getPaperTypeColor(paper.paper_type)}`}>
                          {getPaperTypeIcon(paper.paper_type)}
                          {getPaperTypeLabel(paper.paper_type)}
                        </span>
                        {paper.is_analyzed ? (
                          <span title="Analyzed"><CheckCircle className="w-4 h-4 text-green-600" /></span>
                        ) : (
                          <span title="Not analyzed"><XCircle className="w-4 h-4 text-gray-400" /></span>
                        )}
                      </div>
                      <h3 className="font-semibold text-gray-900 line-clamp-2" title={paper.title}>
                        {paper.title}
                      </h3>
                    </div>
                    <div className="relative">
                      <button
                        onClick={() => setShowDropdown(showDropdown === paper.id ? null : paper.id)}
                        className="p-1 hover:bg-gray-100 rounded"
                      >
                        <MoreVertical className="w-5 h-5 text-gray-500" />
                      </button>
                      {showDropdown === paper.id && (
                        <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                          <button
                            onClick={() => {
                              handleReanalyze(paper.id);
                              setShowDropdown(null);
                            }}
                            disabled={reanalyzing === paper.id}
                            className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
                          >
                            <RefreshCw className={`w-4 h-4 ${reanalyzing === paper.id ? 'animate-spin' : ''}`} />
                            {reanalyzing === paper.id ? 'Reanalyzing...' : 'Reanalyze'}
                          </button>
                          <button
                            onClick={() => {
                              handleDelete(paper.id);
                              setShowDropdown(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-4 space-y-3">
                  {paper.authors && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Authors:</span> {paper.authors}
                    </div>
                  )}
                  {paper.year && (
                    <div className="text-sm text-gray-600 flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      <span>{paper.year}</span>
                      {paper.journal && <span className="text-gray-400">• {paper.journal}</span>}
                    </div>
                  )}
                  {paper.research_area && (
                    <div className="text-sm">
                      <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                        {paper.research_area}
                      </span>
                    </div>
                  )}

                  {/* Writing Style Features */}
                  {paper.is_analyzed && paper.writing_style_features && (
                    <div className="pt-3 border-t border-gray-100">
                      <p className="text-xs font-medium text-gray-700 mb-2">Writing Style Analysis:</p>
                      <div className="space-y-1">
                        <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                          {paper.writing_style_features.avg_sentence_length && (
                            <div className="flex items-center gap-1">
                              <span className="text-gray-500">Avg Sentence:</span>
                              <span className="font-medium">{paper.writing_style_features.avg_sentence_length.toFixed(1)} words</span>
                            </div>
                          )}
                          {paper.writing_style_features.passive_voice_ratio !== undefined && (
                            <div className="flex items-center gap-1">
                              <span className="text-gray-500">Passive Voice:</span>
                              <span className="font-medium">{(paper.writing_style_features.passive_voice_ratio * 100).toFixed(0)}%</span>
                            </div>
                          )}
                          {paper.writing_style_features.vocabulary_complexity !== undefined && (
                            <div className="flex items-center gap-1">
                              <span className="text-gray-500">Vocab Complexity:</span>
                              <span className="font-medium">{(paper.writing_style_features.vocabulary_complexity * 100).toFixed(0)}%</span>
                            </div>
                          )}
                          {paper.writing_style_features.citation_density !== undefined && (
                            <div className="flex items-center gap-1">
                              <span className="text-gray-500">Citations/1k:</span>
                              <span className="font-medium">{paper.writing_style_features.citation_density.toFixed(1)}</span>
                            </div>
                          )}
                        </div>
                        {paper.writing_style_features.common_phrases && paper.writing_style_features.common_phrases.length > 0 && (
                          <div className="text-xs text-gray-600 mt-2">
                            <span className="text-gray-500">Common phrases:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {paper.writing_style_features.common_phrases.slice(0, 3).map((phrase, idx) => (
                                <span key={idx} className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                                  {phrase}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {paper.writing_style_features.technical_terms && paper.writing_style_features.technical_terms.length > 0 && (
                          <div className="text-xs text-gray-600 mt-2">
                            <span className="text-gray-500">Technical terms:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {paper.writing_style_features.technical_terms.slice(0, 3).map((term, idx) => (
                                <span key={idx} className="px-1.5 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">
                                  {term}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Card Footer */}
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                  <span>{formatFileSize(paper.file_size)}</span>
                  <span>Uploaded {formatDate(paper.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReferencePapers;
