import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from 'react';
import apiClient from '../services/api';

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface Workspace {
  id: string;
  name: string;
  visibility: string;
  owner?: string;
  created_at?: string;
  storage_used?: number;
  max_storage?: number;
  is_orphan?: boolean;
  is_yours?: boolean;
}

interface AuthContextType {
  jwt: string | null;
  user: User | null;
  workspace: Workspace | null;
  loading: boolean;
  setJwt: (token: string | null) => void;
  setWorkspace: (ws: Workspace | null) => void;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [jwt, setJwt] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  // Helper: Validate JWT (basic, just checks expiry in payload)
  function isJwtValid(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.exp * 1000 > Date.now();
    } catch {
      return false;
    }
  }

  // Login with magic link token
  const login = useCallback(async (token: string) => {
    const response = await apiClient.post('/v1/auth/verify', { token });
    const { jwt, user: userData } = response.data;
    setJwt(jwt);
    setUser(userData);
    localStorage.setItem('authToken', jwt);
    // Clear any anonymous workspace since user is now authenticated
    localStorage.removeItem('workspaceId');
    setWorkspace(null);
    setLoading(false);
  }, []);

  // Logout
  const logout = () => {
    setJwt(null);
    setUser(null);
    setWorkspace(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('workspaceId');
    // Reload page to reset the app state
    window.location.reload();
  };

  // Check if user is authenticated
  const isAuthenticated = !!jwt && !!user;

  // On mount: check JWT, workspaceId, and fetch/create as needed
  useEffect(() => {
    // Check for magic link token in URL
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (token) {
      // Remove token from URL
      const newUrl = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, newUrl);

      // Verify the token
      login(token).catch(() => {
        // Token verification failed, continue with normal flow
        setLoading(false);
      });
      return;
    }

    const authToken = localStorage.getItem('authToken');
    if (authToken && isJwtValid(authToken)) {
      setJwt(authToken);
      apiClient.get('/v1/auth/me').then(res => {
        setUser(res.data);
        setLoading(false);
      }).catch(() => {
        setJwt(null);
        setUser(null);
        setLoading(false);
      });
      return;
    }
    // Not authenticated, check workspaceId
    const wsId = localStorage.getItem('workspaceId');
    if (wsId) {
      apiClient.get(`/v1/workspaces/${wsId}`)
        .then(res => {
          setWorkspace(res.data);
          setLoading(false);
        })
        .catch(() => {
          localStorage.removeItem('workspaceId');
          setWorkspace(null);
          setLoading(false);
        });
    } else {
      // No workspace in localStorage for anonymous user
      setWorkspace(null);
      setLoading(false);
    }
  }, [login]);

  return (
    <AuthContext.Provider value={{ jwt, user, workspace, loading, setJwt, setWorkspace, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
