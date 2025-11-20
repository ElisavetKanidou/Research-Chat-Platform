import React, { useState } from 'react';
import { Search, HelpCircle, Maximize2, User, Settings, LogOut, Menu } from 'lucide-react';
import NotificationBell from './NotificationBell';
import { useGlobalContext } from '../../contexts/GlobalContext';

interface HeaderProps {
  title?: string;
  subtitle?: string;
  showSearch?: boolean;
  onSearch?: (query: string) => void;
  actions?: React.ReactNode;
  onMenuClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  showSearch = true,
  onSearch,
  actions,
  onMenuClick
}) => {
  const { user } = useGlobalContext();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
  };

  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 sticky top-0 z-40 shadow-sm">
      
      {/* Left Section */}
      <div className="flex items-center gap-4 flex-1 min-w-0">
        {onMenuClick && (
          <button onClick={onMenuClick} className="lg:hidden p-2 text-gray-600">
            <Menu size={24} />
          </button>
        )}
        
        {title ? (
          <div className="min-w-0">
            <h1 className="text-xl font-bold text-gray-900 truncate">{title}</h1>
            {subtitle && (
              <p className="text-sm text-gray-500 truncate hidden md:block">{subtitle}</p>
            )}
          </div>
        ) : (
          <h1 className="text-xl font-bold text-gray-900">Research Platform</h1>
        )}
      </div>

      {/* Center Section - Search */}
      {showSearch && (
        <div className="hidden md:flex flex-1 max-w-xl mx-4">
          <div className="relative w-full">
            <Search 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" 
              size={18} 
            />
            <input
              type="text"
              placeholder="Search..."
              onChange={(e) => onSearch?.(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-sm"
            />
          </div>
        </div>
      )}

      {/* Right Section */}
      <div className="flex items-center gap-2 sm:gap-3">
        {actions}

        <button 
          type="button"
          className="hidden sm:flex p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Help"
        >
          <HelpCircle size={20} />
        </button>

        <button 
          type="button"
          onClick={handleFullscreen}
          className="hidden sm:flex p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Fullscreen"
        >
          <Maximize2 size={20} />
        </button>

        {/* Notification Bell */}
        <div className="relative z-50">
          <NotificationBell />
        </div>

        <div className="w-px h-6 bg-gray-200 mx-1 hidden sm:block"></div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-1.5 hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-200"
          >
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium text-sm shadow-sm">
              {user?.personalInfo?.name?.charAt(0).toUpperCase() || user?.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-sm font-medium text-gray-700 truncate max-w-[100px]">
                {user?.personalInfo?.name || user?.name || 'User'}
              </div>
            </div>
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <>
              <div 
                className="fixed inset-0 z-40"
                onClick={() => setShowUserMenu(false)}
              />
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50">
                <div className="px-4 py-3 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">{user?.personalInfo?.name || user?.name}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.personalInfo?.email || user?.email}</p>
                </div>
                
                <div className="p-1">
                  <button className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 rounded-lg flex items-center gap-2">
                    <User size={16} /> Profile
                  </button>
                  <button className="w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 rounded-lg flex items-center gap-2">
                    <Settings size={16} /> Settings
                  </button>
                </div>
                
                <div className="border-t border-gray-100 p-1">
                  <button
                    onClick={handleLogout}
                    className="w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-2"
                  >
                    <LogOut size={16} /> Logout
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;