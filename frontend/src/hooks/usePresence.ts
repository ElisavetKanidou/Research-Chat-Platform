// hooks/usePresence.ts
import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import type { PresenceStatus } from '../components/PresenceIndicator';
import { getApiBaseUrl, getWebSocketUrl } from '../config/api';

interface PresenceData {
  status: PresenceStatus;
  lastSeen: string | null;
}

interface UsePresenceReturn {
  presenceMap: Map<string, PresenceData>;
  getStatus: (userId: string) => PresenceStatus;
  getLastSeen: (userId: string) => string | null;
  refreshPresence: (userIds: string[]) => Promise<void>;
}

/**
 * Hook for tracking user presence (online/away/offline status)
 *
 * Features:
 * - Sends heartbeat every 30 seconds to update own presence
 * - Listens to WebSocket for real-time presence updates
 * - Caches presence data to minimize API calls
 * - Efficient bulk status checks
 */
export const usePresence = (userIds: string[] = []): UsePresenceReturn => {
  const [presenceMap, setPresenceMap] = useState<Map<string, PresenceData>>(new Map());
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const shouldReconnectRef = useRef<boolean>(true);

  // Send heartbeat to update own presence
  const sendHeartbeat = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      // Only send heartbeat if we have a valid token
      if (!token || token === 'null' || token === 'undefined') {
        return;
      }

      await axios.post(
        `${getApiBaseUrl()}/presence/heartbeat`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
    } catch (error) {
      console.error('Failed to send presence heartbeat:', error);
    }
  }, []);

  // Fetch presence status for multiple users
  const refreshPresence = useCallback(async (targetUserIds: string[]) => {
    if (targetUserIds.length === 0) return;

    try {
      const token = localStorage.getItem('auth_token');
      // Only fetch if we have a valid token
      if (!token || token === 'null' || token === 'undefined') {
        return;
      }

      const response = await axios.post(
        `${getApiBaseUrl()}/presence/bulk-status`,
        targetUserIds,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      const newPresenceMap = new Map(presenceMap);
      Object.entries(response.data).forEach(([userId, data]: [string, any]) => {
        newPresenceMap.set(userId, {
          status: data.status,
          lastSeen: data.last_seen
        });
      });

      setPresenceMap(newPresenceMap);
    } catch (error) {
      console.error('Failed to fetch presence data:', error);
    }
  }, [presenceMap]);

  // WebSocket connection with auto-reconnect
  const connectWebSocket = useCallback(() => {
    const token = localStorage.getItem('auth_token');

    // Only connect if we have a valid token
    if (!token || token === 'null' || token === 'undefined') {
      return;
    }

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Connect to WebSocket
    const wsUrl = `${getWebSocketUrl()}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('✅ WebSocket connected for presence tracking');
      reconnectAttemptsRef.current = 0; // Reset reconnection attempts on successful connection
    };

    ws.onerror = (error) => {
      console.error('⚠️ WebSocket connection error (will auto-reconnect)');
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      wsRef.current = null;

      // Auto-reconnect with exponential backoff
      if (shouldReconnectRef.current) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000); // Max 30 seconds
        reconnectAttemptsRef.current++;

        console.log(`⏳ Reconnecting in ${delay / 1000}s... (attempt ${reconnectAttemptsRef.current})`);

        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, delay);
      }
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        // Handle presence updates
        if (message.type === 'presence') {
          setPresenceMap((prev) => {
            const newMap = new Map(prev);
            newMap.set(message.user_id, {
              status: message.status,
              lastSeen: message.timestamp
            });
            return newMap;
          });
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    wsRef.current = ws;
  }, []);

  // Listen to WebSocket for real-time presence updates
  useEffect(() => {
    shouldReconnectRef.current = true;
    connectWebSocket();

    return () => {
      // Disable reconnection on unmount
      shouldReconnectRef.current = false;

      // Clear reconnection timeout
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      // Close WebSocket
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connectWebSocket]);

  // Start heartbeat interval
  useEffect(() => {
    // Send initial heartbeat
    sendHeartbeat();

    // Set up interval to send heartbeat every 30 seconds
    heartbeatIntervalRef.current = setInterval(() => {
      sendHeartbeat();
    }, 30000); // 30 seconds

    return () => {
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };
  }, [sendHeartbeat]);

  // Fetch presence for tracked users
  useEffect(() => {
    if (userIds.length > 0) {
      refreshPresence(userIds);

      // Refresh every 60 seconds for users not updated via WebSocket
      const refreshInterval = setInterval(() => {
        refreshPresence(userIds);
      }, 60000); // 60 seconds

      return () => clearInterval(refreshInterval);
    }
  }, [userIds.join(',')]); // Only re-run if userIds change

  // Helper to get status for a specific user
  const getStatus = useCallback(
    (userId: string): PresenceStatus => {
      return presenceMap.get(userId)?.status || 'offline';
    },
    [presenceMap]
  );

  // Helper to get last seen for a specific user
  const getLastSeen = useCallback(
    (userId: string): string | null => {
      return presenceMap.get(userId)?.lastSeen || null;
    },
    [presenceMap]
  );

  return {
    presenceMap,
    getStatus,
    getLastSeen,
    refreshPresence
  };
};
