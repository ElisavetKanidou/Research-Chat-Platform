import React, { useState, useRef, useEffect } from 'react';
import { Bell, Check, Trash2, X } from 'lucide-react';
import { useNotifications } from '../../contexts/NotificationContext';

const NotificationBell: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    clearAll
  } = useNotifications();

  // Κλείσιμο όταν πατάμε κλικ έξω
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current && 
        !dropdownRef.current.contains(event.target as Node) &&
        btnRef.current &&
        !btnRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Χρησιμοποιούμε onMouseDown για άμεση απόκριση (παρακάμπτει προβλήματα focus/click)
  const handleToggle = (e: React.MouseEvent) => {
    e.preventDefault(); // Αποτρέπει το κουμπί να πάρει focus που ίσως κλείνει το μενού
    e.stopPropagation();
    console.log("🔔 Bell toggled. New state:", !isOpen); 
    setIsOpen(prev => !prev);
  };

  const handleNotificationClick = async (notification: any) => {
    if (!notification.is_read) {
      await markAsRead(notification.id);
    }
    setIsOpen(false); // Κλείσιμο μετά το κλικ
  };

  const formatTime = (dateString: string) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    } catch (e) { return ''; }
  };

  return (
    <div className="relative inline-block">
      {/* Bell Button */}
      <button
        ref={btnRef}
        type="button"
        onMouseDown={handleToggle} 
        className={`relative p-2 rounded-lg transition-colors duration-200 flex items-center justify-center ${
          isOpen ? 'bg-blue-100 text-blue-700' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
        }`}
        title="Notifications"
      >
        {/* pointer-events-none: Το εικονίδιο δεν "κλέβει" το κλικ */}
        <Bell size={20} className="pointer-events-none" />
        
        {/* Badge */}
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 flex h-4 w-4 -mt-1 -mr-1 pointer-events-none">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-[10px] font-bold text-white items-center justify-center border-2 border-white">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div 
          ref={dropdownRef}
          className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-xl shadow-2xl border border-gray-200 z-50 origin-top-right overflow-hidden"
          style={{ 
             top: '100%',
             marginRight: '-0.5rem' // Μικρή διόρθωση θέσης
          }}
          onMouseDown={(e) => e.stopPropagation()} // Το κλικ μέσα στο dropdown δεν το κλείνει
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
              {unreadCount > 0 && (
                <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded-full">
                  {unreadCount} New
                </span>
              )}
            </div>
            <div className="flex gap-2">
                {unreadCount > 0 && (
                    <button 
                        onMouseDown={(e) => { e.stopPropagation(); markAllAsRead(); }}
                        className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                        title="Mark all read"
                    >
                        Mark all read
                    </button>
                )}
                {notifications.length > 0 && (
                    <button 
                        onMouseDown={(e) => { e.stopPropagation(); if(window.confirm('Clear all?')) clearAll(); }}
                        className="text-xs text-red-500 hover:text-red-700 p-1 rounded hover:bg-red-50"
                        title="Clear list"
                    >
                        <Trash2 size={14} />
                    </button>
                )}
            </div>
          </div>

          {/* List */}
          <div className="max-h-[400px] overflow-y-auto custom-scrollbar bg-white">
            {notifications.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Bell size={32} className="mx-auto mb-2 opacity-20" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-50">
                {notifications.map((n) => (
                  <div 
                    key={n.id} 
                    onMouseDown={() => handleNotificationClick(n)}
                    className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors relative ${!n.is_read ? 'bg-blue-50/40' : ''}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                        <p className="text-sm font-medium text-gray-900 pr-6">{n.title}</p>
                        <span className="text-[10px] text-gray-400 whitespace-nowrap ml-2 shrink-0">
                            {formatTime(n.created_at)}
                        </span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">{n.message}</p>
                    {!n.is_read && (
                        <span className="absolute top-4 right-4 w-2 h-2 bg-blue-500 rounded-full"></span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;