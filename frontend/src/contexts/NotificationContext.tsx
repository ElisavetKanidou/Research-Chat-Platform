// contexts/NotificationContext.tsx - REAL-TIME WITH WEBSOCKET
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { Notification } from '../types/notification';
import { useWebSocket } from '../hooks/useWebSocket';

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  isConnected: boolean; // NEW: WebSocket connection status
  fetchNotifications: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // ✅ NEW: Use WebSocket for real-time updates
  const { isConnected, lastMessage, subscribe } = useWebSocket();

  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const fetchNotifications = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        console.log('⚠️ No auth token, skipping notifications fetch');
        return;
      }

      setLoading(true);
      const response = await fetch('http://127.0.0.1:8000/api/v1/notifications/', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Fetched notifications:', data);
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      } else {
        console.error('❌ Failed to fetch notifications:', response.status);
      }
    } catch (error) {
      console.error('💥 Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // ✅ Handle real-time WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    console.log('📨 Received WebSocket message:', lastMessage);

    // Handle different message types
    switch (lastMessage.type) {
      case 'notification':
        // Add new notification to the list
        const newNotification: Notification = {
          id: `ws-${Date.now()}`,
          type: lastMessage.notification_type,
          title: lastMessage.title,
          message: lastMessage.message,
          is_read: false,
          created_at: lastMessage.timestamp,
          data: lastMessage.data
        };
        setNotifications(prev => [newNotification, ...prev]);
        setUnreadCount(prev => prev + 1);
        console.log('🔔 New notification added:', newNotification);
        break;

      case 'paper_update':
        console.log('📄 Paper update received:', lastMessage);
        // Optionally add paper update as notification
        break;

      case 'collaboration':
        console.log('👥 Collaboration update received:', lastMessage);
        // Optionally add collaboration update as notification
        break;

      case 'connected':
        console.log('✅ WebSocket connected:', lastMessage.message);
        // Subscribe to notification channel
        subscribe('notifications');
        break;

      case 'pong':
        // Heartbeat response
        break;

      default:
        console.log('❓ Unknown message type:', lastMessage.type);
    }
  }, [lastMessage, subscribe]);

  const markAsRead = async (id: string) => {
    try {
      // Optimistic update
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));

      const response = await fetch(`http://127.0.0.1:8000/api/v1/notifications/${id}/read`, {
        method: 'POST',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        // Revert on failure
        await fetchNotifications();
      }
    } catch (error) {
      console.error('Failed to mark as read:', error);
      await fetchNotifications();
    }
  };

  const markAllAsRead = async () => {
    try {
      // Optimistic update
      const previousNotifications = notifications;
      const previousUnreadCount = unreadCount;

      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);

      const response = await fetch('http://127.0.0.1:8000/api/v1/notifications/mark-all-read', {
        method: 'POST',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        // Revert on failure
        setNotifications(previousNotifications);
        setUnreadCount(previousUnreadCount);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      await fetchNotifications();
    }
  };

  const deleteNotification = async (id: string) => {
    try {
      // Optimistic update
      const notificationToDelete = notifications.find(n => n.id === id);
      setNotifications(prev => prev.filter(n => n.id !== id));

      if (notificationToDelete && !notificationToDelete.is_read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }

      const response = await fetch(`http://127.0.0.1:8000/api/v1/notifications/${id}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        // Revert on failure
        await fetchNotifications();
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
      await fetchNotifications();
    }
  };

  const clearAll = async () => {
    try {
      // Optimistic update
      const previousNotifications = notifications;
      const previousUnreadCount = unreadCount;

      setNotifications([]);
      setUnreadCount(0);

      const response = await fetch('http://127.0.0.1:8000/api/v1/notifications/clear-all', {
        method: 'DELETE',
        headers: getAuthHeaders()
      });

      if (!response.ok) {
        // Revert on failure
        setNotifications(previousNotifications);
        setUnreadCount(previousUnreadCount);
      }
    } catch (error) {
      console.error('Failed to clear notifications:', error);
      await fetchNotifications();
    }
  };

  // ✅ Fetch initial notifications ONCE on mount (no more polling!)
  useEffect(() => {
    console.log('🔔 NotificationProvider mounted, fetching initial notifications...');
    fetchNotifications();
  }, []); // Only run once on mount

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        loading,
        isConnected, // NEW: Expose WebSocket connection status
        fetchNotifications,
        markAsRead,
        markAllAsRead,
        deleteNotification,
        clearAll
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};