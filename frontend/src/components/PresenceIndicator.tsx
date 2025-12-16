// components/PresenceIndicator.tsx
import React from 'react';

export type PresenceStatus = 'online' | 'away' | 'offline';

interface PresenceIndicatorProps {
  status: PresenceStatus;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({
  status,
  showText = false,
  size = 'md',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const statusColors = {
    online: 'bg-green-500',
    away: 'bg-yellow-500',
    offline: 'bg-gray-400'
  };

  const statusText = {
    online: 'Online',
    away: 'Away',
    offline: 'Offline'
  };

  return (
    <div className={`flex items-center gap-1.5 ${className}`}>
      <span
        className={`${sizeClasses[size]} ${statusColors[status]} rounded-full border-2 border-white`}
        title={statusText[status]}
      />
      {showText && (
        <span className="text-xs text-gray-600">{statusText[status]}</span>
      )}
    </div>
  );
};

export default PresenceIndicator;
