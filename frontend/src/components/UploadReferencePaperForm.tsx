// components/UploadReferencePaperForm.tsx
import React, { useState, useRef } from 'react';
import {
  Upload,
  X,
  FileText,
  AlertCircle,
  CheckCircle,
  Loader,
  FlaskConical,
  User,
  BookMarked
} from 'lucide-react';
import {
  referencePapersService,
  type PaperType,
  type UploadReferencePaperRequest
} from '../services/referencePapersService';

interface UploadReferencePaperFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

const UploadReferencePaperForm: React.FC<UploadReferencePaperFormProps> = ({ onClose, onSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form fields
  const [title, setTitle] = useState('');
  const [paperType, setPaperType] = useState<PaperType>('literature');
  const [authors, setAuthors] = useState('');
  const [year, setYear] = useState<number | undefined>(undefined);
  const [journal, setJournal] = useState('');
  const [doi, setDoi] = useState('');
  const [researchArea, setResearchArea] = useState('');
  const [abstract, setAbstract] = useState('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed');
      return;
    }

    // Validate file size (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setError('File size must be less than 50MB');
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Auto-fill title from filename if empty
    if (!title) {
      const filename = file.name.replace('.pdf', '');
      setTitle(filename);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith('.pdf')) {
      setSelectedFile(file);
      setError(null);

      if (!title) {
        const filename = file.name.replace('.pdf', '');
        setTitle(filename);
      }
    } else {
      setError('Only PDF files are allowed');
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedFile) {
      setError('Please select a PDF file');
      return;
    }

    if (!title.trim()) {
      setError('Please enter a title');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const request: UploadReferencePaperRequest = {
        file: selectedFile,
        title: title.trim(),
        paper_type: paperType,
        authors: authors.trim() || undefined,
        year: year,
        journal: journal.trim() || undefined,
        doi: doi.trim() || undefined,
        research_area: researchArea.trim() || undefined,
        abstract: abstract.trim() || undefined,
      };

      // Simulate progress (since we don't have real progress events)
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 10, 90));
      }, 200);

      const response = await referencePapersService.uploadReferencePaper(request);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadSuccess(true);

      // Wait a bit to show success message
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to upload paper. Please try again.');
      setUploadProgress(0);
    } finally {
      setUploading(false);
    }
  };

  const getPaperTypeInfo = (type: PaperType) => {
    switch (type) {
      case 'lab':
        return {
          icon: <FlaskConical className="w-5 h-5" />,
          label: 'Lab Paper',
          description: 'Papers from your research lab',
          color: 'border-blue-500 bg-blue-50'
        };
      case 'personal':
        return {
          icon: <User className="w-5 h-5" />,
          label: 'Personal Paper',
          description: 'Your own published papers',
          color: 'border-green-500 bg-green-50'
        };
      case 'literature':
        return {
          icon: <BookMarked className="w-5 h-5" />,
          label: 'Literature',
          description: 'Reference papers from literature',
          color: 'border-purple-500 bg-purple-50'
        };
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Upload Reference Paper</h2>
            <p className="text-sm text-gray-600 mt-1">
              Upload a PDF paper to analyze writing style for AI personalization
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={uploading}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6">
          <div className="space-y-6">
            {/* File Upload Area */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF File <span className="text-red-500">*</span>
              </label>
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  selectedFile
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  disabled={uploading}
                />
                {selectedFile ? (
                  <div className="flex items-center justify-center gap-3">
                    <FileText className="w-8 h-8 text-green-600" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900">{selectedFile.name}</p>
                      <p className="text-sm text-gray-600">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    <p className="text-gray-700 font-medium mb-1">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-sm text-gray-500">PDF files only (max 50MB)</p>
                  </div>
                )}
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paper Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter paper title"
                disabled={uploading}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>

            {/* Paper Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paper Type <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-3">
                {(['lab', 'personal', 'literature'] as PaperType[]).map((type) => {
                  const info = getPaperTypeInfo(type);
                  return (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setPaperType(type)}
                      disabled={uploading}
                      className={`p-4 border-2 rounded-lg transition-all disabled:opacity-50 ${
                        paperType === type
                          ? `${info.color} border-2`
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex flex-col items-center text-center">
                        <div className={paperType === type ? 'text-current' : 'text-gray-500'}>
                          {info.icon}
                        </div>
                        <p className="font-medium text-sm mt-2">{info.label}</p>
                        <p className="text-xs text-gray-500 mt-1">{info.description}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Two Column Layout for remaining fields */}
            <div className="grid grid-cols-2 gap-4">
              {/* Authors */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Authors</label>
                <input
                  type="text"
                  value={authors}
                  onChange={(e) => setAuthors(e.target.value)}
                  placeholder="e.g., John Doe, Jane Smith"
                  disabled={uploading}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>

              {/* Year */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
                <input
                  type="number"
                  value={year || ''}
                  onChange={(e) => setYear(e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="2024"
                  min="1900"
                  max="2100"
                  disabled={uploading}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>

              {/* Journal */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Journal</label>
                <input
                  type="text"
                  value={journal}
                  onChange={(e) => setJournal(e.target.value)}
                  placeholder="e.g., Nature, Science"
                  disabled={uploading}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>

              {/* DOI */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">DOI</label>
                <input
                  type="text"
                  value={doi}
                  onChange={(e) => setDoi(e.target.value)}
                  placeholder="e.g., 10.1000/xyz123"
                  disabled={uploading}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                />
              </div>
            </div>

            {/* Research Area */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Research Area</label>
              <input
                type="text"
                value={researchArea}
                onChange={(e) => setResearchArea(e.target.value)}
                placeholder="e.g., Machine Learning, Neuroscience"
                disabled={uploading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              />
            </div>

            {/* Abstract */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Abstract</label>
              <textarea
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Enter paper abstract (optional)"
                rows={4}
                disabled={uploading}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 resize-none"
              />
            </div>

            {/* Upload Progress */}
            {uploading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-2">
                  <Loader className="w-5 h-5 text-blue-600 animate-spin" />
                  <span className="text-sm font-medium text-blue-900">
                    Uploading and analyzing paper...
                  </span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-blue-700 mt-1">{uploadProgress}% complete</p>
              </div>
            )}

            {/* Success Message */}
            {uploadSuccess && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium text-green-900">
                  Paper uploaded and analyzed successfully!
                </span>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="text-sm text-red-900">{error}</span>
              </div>
            )}
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <button
            type="button"
            onClick={onClose}
            disabled={uploading}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={uploading || !selectedFile || !title.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {uploading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Upload Paper
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadReferencePaperForm;
