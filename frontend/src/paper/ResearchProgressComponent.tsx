// components/paper/ResearchProgressComponent.tsx
import React from 'react';
import { useGlobalContext } from '../contexts/GlobalContext';
import { Calendar, Target, TrendingUp, Clock, CheckCircle, BookOpen, Users } from 'lucide-react';

interface ResearchProgressComponentProps {
  paperId: string;
}

const ResearchProgressComponent: React.FC<ResearchProgressComponentProps> = ({ paperId }) => {
  const { papers, activePaper } = useGlobalContext();
  
  const paper = activePaper || papers.find(p => p.id === paperId);

  if (!paper) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <Target size={32} className="text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Paper not found</h3>
        <p className="text-gray-500">The requested paper could not be found.</p>
      </div>
    );
  }

  const completedSections = paper.sections.filter(s => s.status === 'completed').length;
  const inProgressSections = paper.sections.filter(s => s.status === 'in-progress').length;
  const totalSections = paper.sections.length;
  const wordProgress = paper.targetWordCount > 0 ? Math.round((paper.currentWordCount / paper.targetWordCount) * 100) : 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'in-progress': return 'bg-yellow-100 text-yellow-700';
      case 'needs-review': return 'bg-orange-100 text-orange-700';
      case 'not-started': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const formatDate = (date: Date | string): string => {
    const dateObj = date instanceof Date ? date : new Date(date);
    return dateObj.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Progress Overview */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-6">Research Progress</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-3 bg-blue-100 rounded-full flex items-center justify-center">
              <Target size={24} className="text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{paper.progress}%</div>
            <div className="text-sm text-gray-500">Overall Progress</div>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-3 bg-green-100 rounded-full flex items-center justify-center">
              <CheckCircle size={24} className="text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{completedSections}</div>
            <div className="text-sm text-gray-500">Sections Done</div>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-3 bg-yellow-100 rounded-full flex items-center justify-center">
              <Clock size={24} className="text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{inProgressSections}</div>
            <div className="text-sm text-gray-500">In Progress</div>
          </div>
          
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
              <TrendingUp size={24} className="text-purple-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{Math.min(wordProgress, 100)}%</div>
            <div className="text-sm text-gray-500">Word Target</div>
          </div>
        </div>
      </div>

      {/* Word Count Progress */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Word Count Progress</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Current: {paper.currentWordCount.toLocaleString()} words</span>
            <span className="text-sm text-gray-600">Target: {paper.targetWordCount.toLocaleString()} words</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
              style={{ width: `${Math.min(wordProgress, 100)}%` }}
            />
          </div>
          <div className="text-center">
            <span className="text-lg font-semibold text-gray-900">
              {paper.targetWordCount - paper.currentWordCount > 0 
                ? `${(paper.targetWordCount - paper.currentWordCount).toLocaleString()} words remaining`
                : 'Word target achieved!'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Section Progress */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Section Progress</h3>
        <div className="space-y-4">
          {paper.sections
            .sort((a, b) => a.order - b.order)
            .map((section) => {
              const targetWordsPerSection = Math.round(paper.targetWordCount / paper.sections.length);
              const progress = targetWordsPerSection > 0 ? Math.min((section.wordCount / targetWordsPerSection) * 100, 100) : 0;
              
              return (
                <div key={section.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{section.title}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(section.status)}`}>
                      {section.status.replace('-', ' ')}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                    <span>{section.wordCount} words</span>
                    <span>{Math.round(progress)}% of target ({targetWordsPerSection} words)</span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        section.status === 'completed' ? 'bg-green-500' :
                        section.status === 'in-progress' ? 'bg-blue-500' :
                        section.status === 'needs-review' ? 'bg-orange-500' :
                        'bg-gray-400'
                      }`}
                      style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                  </div>
                  
                  {section.content && (
                    <div className="mt-2 text-xs text-gray-500">
                      Last modified: {formatDate(section.lastModified)}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Research Timeline</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-3 bg-green-50 rounded-lg">
            <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Paper Created</div>
              <div className="text-sm text-gray-500">
                {formatDate(paper.createdAt)}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-4 p-3 bg-blue-50 rounded-lg">
            <div className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0"></div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Last Modified</div>
              <div className="text-sm text-gray-500">
                {formatDate(paper.lastModified)}
              </div>
            </div>
          </div>
          
          {paper.status === 'published' && paper.publicationDate && (
            <div className="flex items-center space-x-4 p-3 bg-purple-50 rounded-lg">
              <div className="w-3 h-3 bg-purple-500 rounded-full flex-shrink-0"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">Published</div>
                <div className="text-sm text-gray-500">
                  {formatDate(paper.publicationDate)}
                </div>
              </div>
              {paper.journal && (
                <div className="text-sm text-gray-600">
                  in {paper.journal}
                </div>
              )}
            </div>
          )}

          {paper.doi && (
            <div className="flex items-center space-x-4 p-3 bg-indigo-50 rounded-lg">
              <div className="w-3 h-3 bg-indigo-500 rounded-full flex-shrink-0"></div>
              <div className="flex-1">
                <div className="font-medium text-gray-900">DOI Assigned</div>
                <div className="text-sm text-gray-500 font-mono">
                  {paper.doi}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Collaboration */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Collaboration</h3>
        <div className="space-y-3">
          {paper.coAuthors.length > 0 ? (
            paper.coAuthors.map((author, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium flex-shrink-0">
                  {author.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{author}</div>
                  <div className="text-sm text-gray-500">Co-author</div>
                </div>
                <div className="w-2 h-2 bg-green-500 rounded-full" title="Active collaborator"></div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Users size={48} className="mx-auto text-gray-300 mb-4" />
              <p className="font-medium">No collaborators yet</p>
              <p className="text-sm">Invite others to collaborate on this research</p>
              <button className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                Invite Collaborators
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Research Statistics */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Research Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Research Area</div>
                <div className="text-lg font-semibold text-gray-900">
                  {paper.researchArea || 'Not specified'}
                </div>
              </div>
              <BookOpen size={20} className="text-blue-600" />
            </div>
          </div>
          
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Citations</div>
                <div className="text-lg font-semibold text-gray-900">
                  {paper.citationCount || 0}
                </div>
              </div>
              <TrendingUp size={20} className="text-green-600" />
            </div>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">Tags</div>
                <div className="text-lg font-semibold text-gray-900">
                  {paper.tags.length}
                </div>
              </div>
              <Target size={20} className="text-purple-600" />
            </div>
          </div>
        </div>
        
        {paper.tags.length > 0 && (
          <div className="mt-4">
            <div className="text-sm text-gray-600 mb-2">Research Tags:</div>
            <div className="flex flex-wrap gap-2">
              {paper.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchProgressComponent;