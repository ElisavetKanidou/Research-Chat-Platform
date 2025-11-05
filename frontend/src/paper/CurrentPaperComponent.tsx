import React, { useState } from 'react';
import { FileText, Save, Download, Edit3, Calendar, Users, Target } from 'lucide-react';
import { useGlobalContext } from '../contexts/GlobalContext';
import type { PaperSection } from '../types/paper';
import { paperService } from '../services/paperService';

const CurrentPaperComponent: React.FC = () => {
  const { activePaper, updatePaper, addNotification, refreshActivePaper, refreshPapers } = useGlobalContext();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(activePaper?.title || '');
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  

  if (!activePaper) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <FileText size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">No paper selected</p>
        </div>
      </div>
    );
  }

  // Helper functions for safe field access
  const getLastModified = () => {
    const date = (activePaper as any).updated_at || activePaper.lastModified || activePaper.createdAt;
    return date instanceof Date ? date : new Date(date);
  };

  const getCurrentWordCount = () => {
    return (activePaper as any).current_word_count || activePaper.currentWordCount || 0;
  };

  const getTargetWordCount = () => {
    return (activePaper as any).target_word_count || activePaper.targetWordCount || 8000;
  };

  const getResearchArea = () => {
    return (activePaper as any).research_area || activePaper.researchArea || '';
  };

  const getCoAuthors = (): string[] => {
    return (activePaper as any).co_authors || activePaper.coAuthors || [];
  };

  const getSections = (): PaperSection[] => {
    return activePaper.sections || [];
  };

  const lastModified = getLastModified();
  const currentWordCount = getCurrentWordCount();
  const targetWordCount = getTargetWordCount();
  const researchArea = getResearchArea();
  const coAuthors = getCoAuthors();
  const sections = getSections();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'not-started': return 'bg-gray-100 text-gray-600';
      case 'in-progress': return 'bg-yellow-100 text-yellow-700';
      case 'completed': return 'bg-green-100 text-green-700';
      case 'needs-review': return 'bg-orange-100 text-orange-700';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✓';
      case 'in-progress': return '⏳';
      case 'needs-review': return '⚠️';
      default: return '○';
    }
  };

  const updatePaperTitle = async () => {
    try {
      await updatePaper(activePaper.id, { title: editTitle });
      setIsEditing(false);
      addNotification({
        type: 'success',
        title: 'Title Updated',
        message: 'Paper title has been updated successfully',
        autoRemove: true,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'Failed to update paper title',
      });
    }
  };
  const updateSectionStatus = async (sectionId: string, newStatus: PaperSection['status']) => {
    try {
      await paperService.updateSection(activePaper.id, sectionId, { 
        status: newStatus 
      });

      // ✅ Auto-refresh
      await refreshActivePaper();
      await refreshPapers();

      addNotification({
        type: 'success',
        title: 'Section Updated',
        message: 'Section status updated successfully',
        autoRemove: true,
      });
    } catch (error) {
      console.error('Failed to update section:', error);
      addNotification({
        type: 'error',
        title: 'Update Failed',
        message: 'Failed to update section status',
      });
    }
  };

  const updateAbstract = async (newAbstract: string) => {
    try {
      await updatePaper(activePaper.id, { abstract: newAbstract });
      await refreshActivePaper(); // ← ΠΡΟΣΘΗΚΗ
    } catch (error) {
      console.error('Failed to update abstract:', error);
    }
  };

  const updateResearchArea = async (newArea: string) => {
    try {
      await updatePaper(activePaper.id, { researchArea: newArea });
      await refreshActivePaper(); // ← ΠΡΟΣΘΗΚΗ
    } catch (error) {
      console.error('Failed to update research area:', error);
    }
  };

  const addCoAuthor = async (authorName: string) => {
    if (authorName.trim() && !coAuthors.includes(authorName.trim())) {
      try {
        await updatePaper(activePaper.id, {
          coAuthors: [...coAuthors, authorName.trim()]
        });
      } catch (error) {
        console.error('Failed to add co-author:', error);
      }
    }
  };

  const removeCoAuthor = async (index: number) => {
    try {
      const newCoAuthors = coAuthors.filter((_, i) => i !== index);
      await updatePaper(activePaper.id, { coAuthors: newCoAuthors });
    } catch (error) {
      console.error('Failed to remove co-author:', error);
    }
  };

  const exportToPDF = () => {
    // Placeholder for PDF export functionality
    console.log('Exporting to PDF...');
    addNotification({
      type: 'info',
      title: 'Export Started',
      message: 'PDF export is being processed...',
    });
    // In real implementation, you would integrate with a PDF library like jsPDF
  };

  const saveToCloud = async () => {
    try {
      await updatePaper(activePaper.id, { lastModified: new Date() });
      addNotification({
        type: 'success',
        title: 'Saved',
        message: 'Paper saved to cloud successfully',
        autoRemove: true,
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save paper to cloud',
      });
    }
  };

  const abstractWordCount = activePaper.abstract ? activePaper.abstract.trim().split(/\s+/).length : 0;

  return (
    <div className="space-y-6">
      {/* Paper Header */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {isEditing ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="text-xl font-bold border-b-2 border-blue-500 focus:outline-none flex-1"
                  onKeyPress={(e) => e.key === 'Enter' && updatePaperTitle()}
                  onBlur={updatePaperTitle}
                />
                <button
                  onClick={updatePaperTitle}
                  className="text-green-600 hover:text-green-700"
                >
                  <Save size={18} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-gray-900">{activePaper.title}</h2>
                <button
                  onClick={() => {
                    setIsEditing(true);
                    setEditTitle(activePaper.title);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Edit3 size={16} />
                </button>
              </div>
            )}
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Calendar size={14} />
                Last modified: {lastModified.toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <FileText size={14} />
                {currentWordCount} / {targetWordCount} words
              </span>
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(activePaper.status)}`}>
                {activePaper.status.replace('-', ' ').toUpperCase()}
              </span>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={saveToCloud}
              className="flex items-center gap-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
            >
              <Save size={16} />
              Save
            </button>
            <button
              onClick={exportToPDF}
              className="flex items-center gap-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
            >
              <Download size={16} />
              Export PDF
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
            <span>Overall Progress</span>
            <span>{activePaper.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${activePaper.progress}%` }}
            />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 text-center">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold text-gray-900">{sections.length}</div>
            <div className="text-xs text-gray-600">Total Sections</div>
          </div>
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="text-lg font-semibold text-green-600">
              {sections.filter(s => s.status === 'completed').length}
            </div>
            <div className="text-xs text-gray-600">Completed</div>
          </div>
          <div className="p-3 bg-yellow-50 rounded-lg">
            <div className="text-lg font-semibold text-yellow-600">
              {sections.filter(s => s.status === 'in-progress').length}
            </div>
            <div className="text-xs text-gray-600">In Progress</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold text-gray-600">
              {sections.filter(s => s.status === 'not-started').length}
            </div>
            <div className="text-xs text-gray-600">Not Started</div>
          </div>
        </div>
      </div>

      {/* Sections List */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Paper Sections</h3>
        {sections.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No sections available. Add sections to get started.
          </div>
        ) : (
          <div className="space-y-3">
            {sections
              .sort((a, b) => a.order - b.order)
              .map((section) => {
                const sectionTargetWords = sections.length > 0 ? targetWordCount / sections.length : 0;
                const progress = section.wordCount > 0 ? Math.min((section.wordCount / sectionTargetWords) * 100, 100) : 0;
                
                return (
                  <div
                    key={section.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedSection(selectedSection === section.id ? null : section.id)}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{getStatusIcon(section.status)}</span>
                      <div>
                        <h4 className="font-medium text-gray-900">{section.title}</h4>
                        <p className="text-sm text-gray-600">
                          {section.wordCount} words • Last modified: {section.lastModified instanceof Date ? section.lastModified.toLocaleDateString() : new Date(section.lastModified).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(section.status)}`}>
                        {section.status.replace('-', ' ')}
                      </span>
                      <select
                        value={section.status}
                        onChange={(e) => updateSectionStatus(section.id, e.target.value as PaperSection['status'])}
                        onClick={(e) => e.stopPropagation()}
                        className="text-sm border rounded px-2 py-1"
                      >
                        <option value="not-started">Not Started</option>
                        <option value="in-progress">In Progress</option>
                        <option value="needs-review">Needs Review</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                );
              })}
          </div>
        )}
      </div>

      {/* Abstract Section */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Abstract</h3>
        <textarea
          value={activePaper.abstract || ''}
          onChange={(e) => updateAbstract(e.target.value)}
          placeholder="Write your paper abstract here..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="flex justify-between items-center mt-2 text-sm text-gray-600">
          <span>Abstract: {abstractWordCount} words</span>
          <span className={abstractWordCount >= 150 && abstractWordCount <= 250 ? 'text-green-600' : 'text-gray-500'}>
            Recommended: 150-250 words
          </span>
        </div>
      </div>

      {/* Research Area and Co-authors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Target size={18} />
            Research Area
          </h3>
          <input
            type="text"
            value={researchArea}
            onChange={(e) => updateResearchArea(e.target.value)}
            placeholder="e.g., Machine Learning, Artificial Intelligence"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Users size={18} />
            Co-authors
          </h3>
          <input
            type="text"
            placeholder="Add co-author names (press Enter)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const value = (e.target as HTMLInputElement).value;
                if (value.trim()) {
                  addCoAuthor(value.trim());
                  (e.target as HTMLInputElement).value = '';
                }
              }
            }}
          />
          <div className="mt-3 flex flex-wrap gap-2">
            {coAuthors.map((author, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1"
              >
                {author}
                <button
                  onClick={() => removeCoAuthor(index)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentPaperComponent;