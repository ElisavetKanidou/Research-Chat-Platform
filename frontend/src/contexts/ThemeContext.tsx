// contexts/ThemeContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'light' | 'dark' | 'auto';
type ResolvedTheme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  resolvedTheme: ResolvedTheme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  isDark: boolean;
  isLight: boolean;
  systemPreference: ResolvedTheme;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
  attribute?: string;
  enableSystem?: boolean;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ 
  children,
  defaultTheme = 'light',
  storageKey = 'researchhub-theme',
  attribute = 'data-theme',
  enableSystem = true
}) => {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === 'undefined') return defaultTheme;
    
    try {
      const stored = localStorage.getItem(storageKey);
      return (stored as Theme) || defaultTheme;
    } catch {
      return defaultTheme;
    }
  });

  const [systemPreference, setSystemPreference] = useState<ResolvedTheme>('light');
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>('light');

  // Listen for system theme changes
  useEffect(() => {
    if (!enableSystem || typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const updateSystemPreference = () => {
      const preference: ResolvedTheme = mediaQuery.matches ? 'dark' : 'light';
      setSystemPreference(preference);
    };

    // Set initial value
    updateSystemPreference();

    // Listen for changes
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', updateSystemPreference);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(updateSystemPreference);
    }
    
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', updateSystemPreference);
      } else {
        // Fallback for older browsers
        mediaQuery.removeListener(updateSystemPreference);
      }
    };
  }, [enableSystem]);

  // Update resolved theme when theme or system preference changes
  useEffect(() => {
    const resolved: ResolvedTheme = theme === 'auto' ? systemPreference : theme as ResolvedTheme;
    setResolvedTheme(resolved);
  }, [theme, systemPreference]);

  // Apply theme to document
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const root = document.documentElement;
    
    // Remove existing theme classes/attributes
    root.classList.remove('light', 'dark');
    root.removeAttribute('data-theme');
    root.removeAttribute('data-color-scheme');
    
    // Apply new theme
    if (attribute === 'class') {
      root.classList.add(resolvedTheme);
    } else {
      root.setAttribute(attribute, resolvedTheme);
    }
    
    // Set color-scheme for better browser defaults
    root.style.colorScheme = resolvedTheme;
    
    // Also set a data attribute for CSS selectors
    root.setAttribute('data-color-scheme', resolvedTheme);
    
    // Update meta theme-color for mobile browsers
    const themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (themeColorMeta) {
      const color = resolvedTheme === 'dark' ? '#0f172a' : '#ffffff';
      themeColorMeta.setAttribute('content', color);
    }
  }, [resolvedTheme, attribute]);

  // Persist theme preference
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      // Handle localStorage errors silently
    }
  }, [theme, storageKey]);

  const handleSetTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    
    // Dispatch custom event for other parts of the app
    window.dispatchEvent(new CustomEvent('themechange', { 
      detail: { theme: newTheme } 
    }));
  };

  const toggleTheme = () => {
    if (theme === 'light') {
      handleSetTheme('dark');
    } else if (theme === 'dark') {
      handleSetTheme('light');
    } else {
      // If auto, toggle to opposite of current system preference
      handleSetTheme(systemPreference === 'light' ? 'dark' : 'light');
    }
  };

  const contextValue: ThemeContextType = {
    theme,
    resolvedTheme,
    setTheme: handleSetTheme,
    toggleTheme,
    isDark: resolvedTheme === 'dark',
    isLight: resolvedTheme === 'light',
    systemPreference,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

// Hook for using theme in CSS-in-JS or styled-components
export const useThemeValue = () => {
  const { resolvedTheme } = useTheme();
  return resolvedTheme;
};

// Hook for theme-aware styles
export const useThemeStyles = <T extends Record<string, any>>(
  styles: { light: T; dark: T }
): T => {
  const { resolvedTheme } = useTheme();
  return styles[resolvedTheme];
};

// HOC for theme-aware components
export function withTheme<P extends object>(
  Component: React.ComponentType<P & { theme: ResolvedTheme }>
) {
  return function ThemedComponent(props: P) {
    const { resolvedTheme } = useTheme();
    return <Component {...props} theme={resolvedTheme} />;
  };
}

// Utility function for theme-aware class names
export const themeClass = (lightClass: string, darkClass: string, theme?: ResolvedTheme) => {
  if (theme) {
    return theme === 'dark' ? darkClass : lightClass;
  }
  
  // If no theme provided, return both with theme selectors
  return `${lightClass} dark:${darkClass}`;
};