import React, { useState } from 'react';
import { FileText, Save, Download, Edit3, Calendar, Users, Target, BookOpen } from 'lucide-react';

interface PaperSection {
  id: string;
  title: string;
  content: string;
  status: 'not-started' | 'in-progress' | 'completed' | 'needs-review';
  lastModified: Date;
  wordCount: number;
}

interface CurrentPaper {
  id: string;
  title: string;
  abstract: string;
  status: 'draft' | 'in-review' | 'revision' | 'completed';
  createdAt: Date;
  lastModified: Date;
  totalWordCount: number;
  targetWordCount: number;
  coAuthors: string[];
  researchArea: string;
  sections: PaperSection[];
}

const CurrentPaperComponent = () => {
  const [currentPaper, setCurrentPaper] = useState<CurrentPaper>({
    id: '1',
    title: 'Untitled Research Paper',
    abstract: '',
    status: 'draft',
    createdAt: new Date(),
    lastModified: new Date(),
    totalWordCount: 0,
    targetWordCount: 8000,
    coAuthors: [],
    researchArea: '',
    sections: [
      { id: '1', title: 'Introduction', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 },
      { id: '2', title: 'Literature Review', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 },
      { id: '3', title: 'Methodology', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 },
      { id: '4', title: 'Results', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 },
      { id: '5', title: 'Discussion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 },
      { id: '6', title: 'Conclusion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0 }
    ]
  });

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(currentPaper.title);
  const [selectedSection, setSelectedSection] = useState<string | null>(null);

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

  const updatePaperTitle = () => {
    setCurrentPaper(prev => ({
      ...prev,
      title: editTitle,
      lastModified: new Date()
    }));
    setIsEditing(false);
  };

  const updateSectionStatus = (sectionId: string, newStatus: PaperSection['status']) => {
    setCurrentPaper(prev => ({
      ...prev,
      sections: prev.sections.map(section =>
        section.id === sectionId
          ? { ...section, status: newStatus, lastModified: new Date() }
          : section
      ),
      lastModified: new Date()
    }));
  };

  const exportToPDF = () => {
    // Placeholder for PDF export functionality
    console.log('Exporting to PDF...');
    // In real implementation, you would integrate with a PDF library like jsPDF
    alert('PDF export functionality would be implemented here');
  };

  const saveToCloud = () => {
    console.log('Saving to cloud...');
    alert('Paper saved successfully!');
  };

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
                <h2 className="text-xl font-bold text-gray-900">{currentPaper.title}</h2>
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Edit3 size={16} />
                </button>
              </div>
            )}
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className="flex items-center gap-1">
                <Calendar size={14} />
                Last modified: {currentPaper.lastModified.toLocaleDateString()}
              </span>
              <span className="flex items-center gap-1">
                <FileText size={14} />
                {currentPaper.totalWordCount} / {currentPaper.targetWordCount} words
              </span>
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(currentPaper.status)}`}>
                {currentPaper.status.replace('-', ' ').toUpperCase()}
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
            <span>{Math.round((currentPaper.sections.filter(s => s.status === 'completed').length / currentPaper.sections.length) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{
                width: `${(currentPaper.sections.filter(s => s.status === 'completed').length / currentPaper.sections.length) * 100}%`
              }}
            />
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 text-center">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold text-gray-900">{currentPaper.sections.length}</div>
            <div className="text-xs text-gray-600">Total Sections</div>
          </div>
          <div className="p-3 bg-green-50 rounded-lg">
            <div className="text-lg font-semibold text-green-600">
              {currentPaper.sections.filter(s => s.status === 'completed').length}
            </div>
            <div className="text-xs text-gray-600">Completed</div>
          </div>
          <div className="p-3 bg-yellow-50 rounded-lg">
            <div className="text-lg font-semibold text-yellow-600">
              {currentPaper.sections.filter(s => s.status === 'in-progress').length}
            </div>
            <div className="text-xs text-gray-600">In Progress</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-lg font-semibold text-gray-600">
              {currentPaper.sections.filter(s => s.status === 'not-started').length}
            </div>
            <div className="text-xs text-gray-600">Not Started</div>
          </div>
        </div>
      </div>

      {/* Sections List */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Paper Sections</h3>
        <div className="space-y-3">
          {currentPaper.sections.map((section) => (
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
                    {section.wordCount} words • Last modified: {section.lastModified.toLocaleDateString()}
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
          ))}
        </div>
      </div>

      {/* Abstract Section */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Abstract</h3>
        <textarea
          value={currentPaper.abstract}
          onChange={(e) => setCurrentPaper(prev => ({ ...prev, abstract: e.target.value }))}
          placeholder="Write your paper abstract here..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <div className="flex justify-between items-center mt-2 text-sm text-gray-600">
          <span>Abstract: {currentPaper.abstract.split(' ').length - 1} words</span>
          <span>Recommended: 150-250 words</span>
        </div>
      </div>

      {/* Research Area and Co-authors */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Target size={18} />
            Research Area
          </h3>
          <input
            type="text"
            value={currentPaper.researchArea}
            onChange={(e) => setCurrentPaper(prev => ({ ...prev, researchArea: e.target.value }))}
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
            placeholder="Add co-author names (comma separated)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                const value = (e.target as HTMLInputElement).value;
                if (value.trim()) {
                  setCurrentPaper(prev => ({
                    ...prev,
                    coAuthors: [...prev.coAuthors, value.trim()]
                  }));
                  (e.target as HTMLInputElement).value = '';
                }
              }
            }}
          />
          <div className="mt-3 flex flex-wrap gap-2">
            {currentPaper.coAuthors.map((author, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center gap-1"
              >
                {author}
                <button
                  onClick={() => setCurrentPaper(prev => ({
                    ...prev,
                    coAuthors: prev.coAuthors.filter((_, i) => i !== index)
                  }))}
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