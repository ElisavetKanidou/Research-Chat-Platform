// components/common/StatusBadge.tsx
import React from 'react';
import { getStatusColor, getStatusIcon, formatStatus } from '../../utils/statusHelpers';

interface StatusBadgeProps {
  status: string;
  showIcon?: boolean;
  showText?: boolean;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outline' | 'solid' | 'dot';
  className?: string;
  onClick?: () => void;
  customColors?: {
    background: string;
    text: string;
    border?: string;
  };
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ 
  status, 
  showIcon = true, 
  showText = true,
  size = 'sm',
  variant = 'default',
  className = '',
  onClick,
  customColors
}) => {
  const sizeClasses = {
    xs: 'text-xs px-1.5 py-0.5',
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  const iconSizes = {
    xs: 10,
    sm: 12,
    md: 14,
    lg: 16,
  };

  const getVariantClasses = () => {
    const baseColors = customColors ? 
      `bg-${customColors.background} text-${customColors.text} border-${customColors.border || customColors.background}` :
      getStatusColor(status);

    switch (variant) {
      case 'outline':
        return `border ${baseColors.replace('bg-', 'border-').replace('text-', 'text-')} bg-transparent`;
      case 'solid':
        return `${baseColors.replace('-100', '-600').replace('text-', 'text-white')}`;
      case 'dot':
        return `bg-gray-100 text-gray-800`;
      default:
        return baseColors;
    }
  };

  const renderDotVariant = () => (
    <span 
      className={`inline-flex items-center gap-2 ${sizeClasses[size]} rounded-full font-medium ${className} ${onClick ? 'cursor-pointer hover:opacity-80' : ''}`}
      onClick={onClick}
    >
      <span 
        className={`w-2 h-2 rounded-full ${customColors ? `bg-${customColors.background}` : getStatusColor(status).split(' ')[0]}`}
      />
      {showText && <span>{formatStatus(status)}</span>}
    </span>
  );

  if (variant === 'dot') {
    return renderDotVariant();
  }

  return (
    <span 
      className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClasses[size]} ${getVariantClasses()} ${className} ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      } : undefined}
    >
      {showIcon && (
        <span className="flex-shrink-0" style={{ fontSize: iconSizes[size] }}>
          {getStatusIcon(status)}
        </span>
      )}
      {showText && (
        <span className="truncate">
          {formatStatus(status)}
        </span>
      )}
    </span>
  );
};

// Predefined status badge variants for common use cases
export const PaperStatusBadge: React.FC<Omit<StatusBadgeProps, 'status'> & { status: 'draft' | 'in-progress' | 'in-review' | 'revision' | 'completed' | 'published' | 'archived' }> = (props) => (
  <StatusBadge {...props} />
);

export const TaskStatusBadge: React.FC<Omit<StatusBadgeProps, 'status'> & { status: 'not-started' | 'in-progress' | 'completed' | 'needs-review' }> = (props) => (
  <StatusBadge {...props} />
);

export const PriorityBadge: React.FC<Omit<StatusBadgeProps, 'status'> & { status: 'high' | 'medium' | 'low' }> = (props) => (
  <StatusBadge {...props} variant="solid" />
);

// Animated status badge for loading states
export const AnimatedStatusBadge: React.FC<StatusBadgeProps & { isLoading?: boolean }> = ({ 
  isLoading = false, 
  ...props 
}) => (
  <StatusBadge 
    {...props} 
    className={`${props.className} ${isLoading ? 'animate-pulse' : ''}`} 
  />
);