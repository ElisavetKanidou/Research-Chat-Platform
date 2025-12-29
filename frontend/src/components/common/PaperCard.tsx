// components/common/PaperCard.tsx
import React from 'react';
import { FileText, Clock, Users, MoreVertical, Calendar } from 'lucide-react';
import type { Paper } from '../../types/paper';
import { getStatusColor, formatTimeAgo } from '../../utils/statusHelpers';
import { formatDate, formatDateTime } from '../../utils/dateHelpers';

interface PaperCardProps {
  paper: Paper;
  onClick: (paper: Paper) => void;
  onMenuClick?: (paper: Paper, event: React.MouseEvent) => void;
  showMenu?: boolean;
  variant?: 'default' | 'compact' | 'detailed';
  className?: string;
}

export const PaperCard: React.FC<PaperCardProps> = ({
  paper,
  onClick,
  onMenuClick,
  showMenu = true,
  variant = 'default',
  className = ''
}) => {
  const handleCardClick = () => {
    onClick(paper);
  };

  const handleMenuClick = (event: React.MouseEvent) => {
    event.stopPropagation();
    if (onMenuClick) {
      onMenuClick(paper, event);
    }
  };

  const renderCompactCard = () => (
    <div
      className={`bg-white rounded-lg shadow-sm border hover:shadow-md transition-all cursor-pointer p-4 ${className}`}
      onClick={handleCardClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-semibold text-gray-900 truncate">
            {paper.title}
          </h3>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
              {paper.status.replace('-', ' ')}
            </span>
            <span className="text-xs text-gray-500">{paper.progress}%</span>
            {(() => {
              const paperObj = paper as any;
              const collabCount = paperObj.collaborator_count ?? paper.collaboratorCount ?? 0;
              if (collabCount > 0) {
                return (
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Users size={12} />
                    {collabCount}
                  </span>
                );
              }
              return null;
            })()}
          </div>
        </div>
        {showMenu && (
          <button
            onClick={handleMenuClick}
            className="p-1 hover:bg-gray-100 rounded-full ml-2"
          >
            <MoreVertical size={14} className="text-gray-400" />
          </button>
        )}
      </div>
    </div>
  );

  const renderDetailedCard = () => (
    <div 
      className={`bg-white rounded-lg shadow-sm border hover:shadow-md transition-all cursor-pointer ${className}`}
      onClick={handleCardClick}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              {paper.title}
            </h3>
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                {paper.status.replace('-', ' ')}
              </span>
              {paper.researchArea && (
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {paper.researchArea}
                </span>
              )}
            </div>
            {paper.abstract && (
              <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                {paper.abstract}
              </p>
            )}
          </div>
          {showMenu && (
            <button
              onClick={handleMenuClick}
              className="p-1 hover:bg-gray-100 rounded-full"
            >
              <MoreVertical size={16} className="text-gray-400" />
            </button>
          )}
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

        <div className="space-y-2 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-2">
            <FileText size={14} />
            <span>{paper.currentWordCount.toLocaleString()} / {paper.targetWordCount.toLocaleString()} words</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock size={14} />
            <span>Modified {formatTimeAgo(paper.lastModified)}</span>
          </div>
          {paper.deadline && (
            <div className="flex items-center gap-2 text-orange-600">
              <Calendar size={14} />
              <span>Due {formatDateTime(paper.deadline)}</span>
            </div>
          )}
          {(() => {
            const paperObj = paper as any;
            const collabCount = paperObj.collaborator_count ?? paperObj.collaboratorCount ?? 0;

            if (collabCount > 0) {
              return (
                <div className="flex items-center gap-2">
                  <Users size={14} />
                  <span>{collabCount} collaborator{collabCount > 1 ? 's' : ''}</span>
                </div>
              );
            }
            return null;
          })()}
        </div>

        <div className="pt-4 border-t">
          <button
            onClick={handleCardClick}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Continue Working
          </button>
        </div>
      </div>
    </div>
  );

  const renderDefaultCard = () => (
    <div 
      className={`bg-white rounded-lg shadow-sm border hover:shadow-md transition-all cursor-pointer ${className}`}
      onClick={handleCardClick}
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              {paper.title}
            </h3>
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(paper.status)}`}>
                {paper.status.replace('-', ' ')}
              </span>
              {paper.researchArea && (
                <span className="text-xs text-gray-500">{paper.researchArea}</span>
              )}
            </div>
          </div>
          {showMenu && (
            <button
              onClick={handleMenuClick}
              className="p-1 hover:bg-gray-100 rounded-full"
            >
              <MoreVertical size={16} className="text-gray-400" />
            </button>
          )}
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
            <span>Modified {formatTimeAgo(paper.lastModified)}</span>
          </div>
          {paper.deadline && (
            <div className="flex items-center gap-2 text-orange-600">
              <Calendar size={14} />
              <span>Due {formatDateTime(paper.deadline)}</span>
            </div>
          )}
          {(() => {
            const paperObj = paper as any;
            const collabCount = paperObj.collaborator_count ?? paperObj.collaboratorCount ?? 0;

            if (collabCount > 0) {
              return (
                <div className="flex items-center gap-2">
                  <Users size={14} />
                  <span>{collabCount} collaborator{collabCount > 1 ? 's' : ''}</span>
                </div>
              );
            }
            return null;
          })()}
        </div>

        <div className="mt-4 pt-4 border-t">
          <button
            onClick={handleCardClick}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Continue Working
          </button>
        </div>
      </div>
    </div>
  );

  switch (variant) {
    case 'compact':
      return renderCompactCard();
    case 'detailed':
      return renderDetailedCard();
    default:
      return renderDefaultCard();
  }
};