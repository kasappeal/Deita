import { createContext, ReactNode, useContext, useEffect, useState } from 'react';
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
}

interface AuthContextType {
  jwt: string | null;
  user: User | null;
  workspace: Workspace | null;
  loading: boolean;
  setJwt: (token: string | null) => void;
  setWorkspace: (ws: Workspace | null) => void;
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

  // Helper: Generate random workspace name
  function randomWorkspaceName() {
    const animals = ['Otter', 'Fox', 'Bear', 'Hawk', 'Wolf', 'Lynx', 'Seal', 'Crane', 'Swan', 'Panda'];
    const colors = ['Blue', 'Green', 'Red', 'Yellow', 'Purple', 'Orange', 'Silver', 'Gold', 'Indigo', 'Teal'];
    return `${colors[Math.floor(Math.random()*colors.length)]} ${animals[Math.floor(Math.random()*animals.length)]}`;
  }

  // On mount: check JWT, workspaceId, and fetch/create as needed
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token && isJwtValid(token)) {
      setJwt(token);
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
      // Create new workspace
      const name = randomWorkspaceName();
      apiClient.post('/v1/workspaces/', { name, visibility: 'public' })
        .then(res => {
          setWorkspace(res.data);
          localStorage.setItem('workspaceId', res.data.id);
          setLoading(false);
        })
        .catch(() => {
          setWorkspace(null);
          setLoading(false);
        });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ jwt, user, workspace, loading, setJwt, setWorkspace }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
