// components/layout/Sidebar.tsx - WITH NOTIFICATION BELL
import React from 'react';
import { Home, FileText, MessageSquare, BarChart3, Settings, Plus, LogOut, User } from 'lucide-react';
import { useGlobalContext } from '../../contexts/GlobalContext';
import NotificationBell from './NotificationBell';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onNewPaper: () => void;
  onLogout?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSectionChange,
  onNewPaper,
  onLogout
}) => {
  const { papers, activePaper, user } = useGlobalContext();

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'papers', label: 'Papers Management', icon: FileText, badge: papers.length },
    { id: 'chat', label: 'AI Research Assistant', icon: MessageSquare },
    { id: 'analytics', label: 'Analytics & Insights', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-80 bg-white shadow-lg flex flex-col h-full">
      {/* Header with Notification Bell */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-2">
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-900">ResearchHub</h1>
          </div>
          {/* ✅ NOTIFICATION BELL HERE */}
          <NotificationBell />
        </div>
        <p className="text-sm text-gray-600">Comprehensive Research Management</p>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-6 overflow-y-auto">
        <div className="space-y-2">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onSectionChange(item.id)}
              className={`w-full flex items-center gap-3 p-3 text-left rounded-lg transition-colors ${
                activeSection === item.id ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-50'
              }`}
            >
              <item.icon size={20} />
              <div className="flex items-center justify-between flex-1">
                <span>{item.label}</span>
                {item.badge && item.badge > 0 && (
                  <span className="text-xs bg-gray-200 px-2 py-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </div>
            </button>
          ))}

          {/* Active Paper Indicator */}
          {activePaper && (
            <div className="ml-4 mt-2">
              <button
                onClick={() => onSectionChange('workspace')}
                className={`w-full flex items-center gap-3 p-2 text-left rounded-lg transition-colors text-sm ${
                  activeSection === 'workspace' ? 'bg-blue-50 text-blue-600' : 'hover:bg-gray-50 text-gray-600'
                }`}
              >
                <div className="w-2 h-2 bg-blue-500 rounded-full" />
                <span className="truncate">{activePaper.title}</span>
              </button>
            </div>
          )}
        </div>
      </nav>

      {/* Footer Actions */}
      <div className="p-6 border-t space-y-3">
        <button
          onClick={onNewPaper}
          className="w-full flex items-center justify-center gap-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={20} />
          <span>New Paper</span>
        </button>

        {activePaper && (
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500 mb-1">Active Paper</div>
            <div className="text-sm font-medium text-gray-900 truncate">{activePaper.title}</div>
            <div className="text-xs text-gray-500 mt-1">{activePaper.progress}% complete</div>
            <div className="w-full bg-gray-200 rounded-full h-1 mt-1">
              <div
                className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                style={{ width: `${activePaper.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* User Info & Logout */}
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User size={16} className="text-blue-600" />
            </div>
            <div>
              <div className="text-sm font-medium text-gray-900">
                {user?.name || 'Researcher'}
              </div>
              <div className="text-xs text-gray-500">{papers.length} papers</div>
            </div>
          </div>
          {onLogout && (
            <button
              onClick={onLogout}
              className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
              title="Logout"
            >
              <LogOut size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};