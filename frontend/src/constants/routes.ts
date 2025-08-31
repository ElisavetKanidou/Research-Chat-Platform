// constants/routes.ts
export const ROUTES = {
  // Public routes
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  VERIFY_EMAIL: '/verify-email',

  // Protected routes
  DASHBOARD: '/dashboard',
  PAPERS: '/papers',
  PAPER_WORKSPACE: '/papers/:id',
  PAPER_EDITOR: '/papers/:id/editor',
  PAPER_CHAT: '/papers/:id/chat',
  PAPER_PROGRESS: '/papers/:id/progress',
  
  // Global features
  CHAT: '/chat',
  ANALYTICS: '/analytics',
  SETTINGS: '/settings',
  PROFILE: '/profile',

  // Collaboration
  COLLABORATIONS: '/collaborations',
  INVITATIONS: '/invitations',

  // API endpoints
  API: {
    BASE: '/api',
    AUTH: '/api/auth',
    PAPERS: '/api/papers',
    CHAT: '/api/chat',
    ANALYTICS: '/api/analytics',
    USERS: '/api/users',
    UPLOAD: '/api/upload',
    EXPORT: '/api/export',
  }
} as const;

export const buildRoute = (route: string, params: Record<string, string | number>): string => {
  let builtRoute = route;
  Object.entries(params).forEach(([key, value]) => {
    builtRoute = builtRoute.replace(`:${key}`, String(value));
  });
  return builtRoute;
};

// Clean solution: Create a Set for O(1) lookup and explicit typing
const publicRoutes = new Set<string>([
  ROUTES.HOME,
  ROUTES.LOGIN,
  ROUTES.REGISTER,
  ROUTES.FORGOT_PASSWORD,
  ROUTES.RESET_PASSWORD,
  ROUTES.VERIFY_EMAIL,
]);

export const isPublicRoute = (path: string): boolean => {
  return publicRoutes.has(path);
};

export const getDefaultRouteForUser = (isAuthenticated: boolean): string => {
  return isAuthenticated ? ROUTES.DASHBOARD : ROUTES.LOGIN;
};