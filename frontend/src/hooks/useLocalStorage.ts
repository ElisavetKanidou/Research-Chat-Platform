// hooks/useLocalStorage.ts - COMPLETE FILE
import { useState, useEffect, useCallback } from 'react';

type SetValue<T> = (value: T | ((prevValue: T) => T)) => void;

/**
 * Hook for managing localStorage with TypeScript support
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, SetValue<T>, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') {
      return initialValue;
    }
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue: SetValue<T> = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(storedValue) : value;
        setStoredValue(valueToStore);
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
        }
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.warn(`Error parsing localStorage value for key "${key}":`, error);
        }
      } else if (e.key === key && e.newValue === null) {
        setStoredValue(initialValue);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

/**
 * Hook for localStorage with additional features
 */
export function useLocalStorageState<T>(
  key: string,
  initialValue: T,
  options: {
    serialize?: (value: T) => string;
    deserialize?: (value: string) => T;
    syncAcrossTabs?: boolean;
  } = {}
) {
  const {
    serialize = JSON.stringify,
    deserialize = JSON.parse,
    syncAcrossTabs = true,
  } = options;

  const [state, setState] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? deserialize(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue: SetValue<T> = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function ? value(state) : value;
        setState(valueToStore);
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, serialize(valueToStore));
        }
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, serialize, state]
  );

  const removeValue = useCallback(() => {
    try {
      setState(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  const resetValue = useCallback(() => {
    setValue(initialValue);
  }, [setValue, initialValue]);

  useEffect(() => {
    if (!syncAcrossTabs || typeof window === 'undefined') return;

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key) {
        try {
          if (e.newValue !== null) {
            setState(deserialize(e.newValue));
          } else {
            setState(initialValue);
          }
        } catch (error) {
          console.warn(`Error parsing localStorage value for key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key, initialValue, deserialize, syncAcrossTabs]);

  return {
    value: state,
    setValue,
    removeValue,
    resetValue,
    key,
  };
}

/**
 * Hook for localStorage with expiration
 */
export function useLocalStorageWithExpiration<T>(
  key: string,
  initialValue: T,
  ttl: number = 24 * 60 * 60 * 1000
): [T, SetValue<T>, () => void, boolean] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    
    try {
      const item = window.localStorage.getItem(key);
      if (!item) return initialValue;
      
      const parsed = JSON.parse(item);
      if (parsed.expiry && Date.now() > parsed.expiry) {
        window.localStorage.removeItem(key);
        return initialValue;
      }
      
      return parsed.value ?? initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const [isExpired, setIsExpired] = useState(false);

  const setValueWithExpiry: SetValue<T> = useCallback((newValue) => {
    try {
      const valueToStore = newValue instanceof Function ? newValue(value) : newValue;
      const expiry = Date.now() + ttl;
      
      setValue(valueToStore);
      setIsExpired(false);
      
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify({
          value: valueToStore,
          expiry
        }));
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, ttl, value]);

  const removeValue = useCallback(() => {
    try {
      setValue(initialValue);
      setIsExpired(false);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  useEffect(() => {
    const checkExpiration = () => {
      if (typeof window === 'undefined') return;
      
      try {
        const item = window.localStorage.getItem(key);
        if (item) {
          const parsed = JSON.parse(item);
          if (parsed.expiry && Date.now() > parsed.expiry) {
            setValue(initialValue);
            setIsExpired(true);
            window.localStorage.removeItem(key);
          }
        }
      } catch (error) {
        console.warn(`Error checking expiration for key "${key}":`, error);
      }
    };

    const interval = setInterval(checkExpiration, 60000);
    return () => clearInterval(interval);
  }, [key, initialValue]);

  return [value, setValueWithExpiry, removeValue, isExpired];
}

/**
 * Hook for multiple localStorage keys as a single object
 */
export function useMultipleLocalStorage<T extends Record<string, any>>(
  keys: T,
  namespace?: string
): {
  values: T;
  setValues: (updates: Partial<T>) => void;
  setValue: <K extends keyof T>(key: K, value: T[K]) => void;
  removeValue: <K extends keyof T>(key: K) => void;
  clearAll: () => void;
} {
  const getStorageKey = (key: string) => namespace ? `${namespace}:${key}` : key;
  
  const [values, setValues] = useState<T>(() => {
    if (typeof window === 'undefined') return keys;
    
    const initialValues = { ...keys };
    
    Object.keys(keys).forEach((key) => {
      try {
        const item = window.localStorage.getItem(getStorageKey(key));
        if (item) {
          initialValues[key as keyof T] = JSON.parse(item);
        }
      } catch (error) {
        console.warn(`Error reading localStorage key "${getStorageKey(key)}":`, error);
      }
    });
    
    return initialValues;
  });

  const updateValues = useCallback((updates: Partial<T>) => {
    setValues(prev => {
      const newValues = { ...prev, ...updates };
      
      if (typeof window !== 'undefined') {
        Object.entries(updates).forEach(([key, value]) => {
          try {
            window.localStorage.setItem(getStorageKey(key), JSON.stringify(value));
          } catch (error) {
            console.warn(`Error setting localStorage key "${getStorageKey(key)}":`, error);
          }
        });
      }
      
      return newValues;
    });
  }, [namespace]);

  const setValue = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    updateValues({ [key]: value } as unknown as Partial<T>);
  }, [updateValues]);

  const removeValue = useCallback(<K extends keyof T>(key: K) => {
    try {
      setValues(prev => ({ ...prev, [key]: keys[key] }));
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(getStorageKey(key as string));
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${getStorageKey(key as string)}":`, error);
    }
  }, [keys, namespace]);

  const clearAll = useCallback(() => {
    try {
      setValues({ ...keys });
      if (typeof window !== 'undefined') {
        Object.keys(keys).forEach(key => {
          window.localStorage.removeItem(getStorageKey(key));
        });
      }
    } catch (error) {
      console.warn('Error clearing localStorage keys:', error);
    }
  }, [keys, namespace]);

  return {
    values,
    setValues: updateValues,
    setValue,
    removeValue,
    clearAll,
  };
}