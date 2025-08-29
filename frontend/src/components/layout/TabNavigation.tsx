// components/layout/TabNavigation.tsx
import React from 'react';

interface Tab {
  id: string;
  label: string;
  icon?: React.ComponentType<{ size?: number }>;
  disabled?: boolean;
  badge?: string | number;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
  variant?: 'default' | 'pills' | 'underlined';
  size?: 'sm' | 'md' | 'lg';
}

export const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onChange,
  variant = 'default',
  size = 'md'
}) => {
  const baseClasses = 'flex items-center gap-2 font-medium transition-colors';
  
  const variantClasses = {
    default: {
      container: 'bg-white p-1 rounded-lg shadow-sm border',
      tab: 'px-4 py-2 rounded-lg',
      active: 'bg-blue-100 text-blue-700',
      inactive: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
    },
    pills: {
      container: 'flex space-x-1',
      tab: 'px-4 py-2 rounded-full border',
      active: 'bg-blue-600 text-white border-blue-600',
      inactive: 'text-gray-600 border-gray-300 hover:bg-gray-50'
    },
    underlined: {
      container: 'border-b',
      tab: 'px-6 py-3 border-b-2',
      active: 'border-blue-500 text-blue-600',
      inactive: 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
    }
  };

  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  const classes = variantClasses[variant];

  return (
    <div className={classes.container}>
      <div className="flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => !tab.disabled && onChange(tab.id)}
            disabled={tab.disabled}
            className={`
              ${baseClasses}
              ${classes.tab}
              ${sizeClasses[size]}
              ${activeTab === tab.id ? classes.active : classes.inactive}
              ${tab.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            {tab.icon && <tab.icon size={18} />}
            <span>{tab.label}</span>
            {tab.badge && (
              <span className="px-2 py-1 text-xs bg-gray-200 rounded-full">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
};