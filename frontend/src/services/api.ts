import axios from 'axios'
import { env } from '../config/env'

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: env.API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('authToken')
      // Could dispatch a logout action here
    }
    return Promise.reject(error)
  }
)

// Type definitions
export interface FileData {
  id: string;
  filename: string;
  size: number;
  table_name: string;
  row_count: number;
  csv_metadata?: Record<string, unknown>;
  uploaded_at: string;
}

export interface TableData {
  id: string;
  name: string;
  slug: string;
  rows: number;
  columns: number;
}

export interface QueryResult {
  columns: string[];
  rows: (string | number | boolean | null)[][];
  time: number;
  has_more: boolean;
}

export interface AIQueryResult {
  sql_query?: string;
  confidence?: number;
  is_sql_translatable?: boolean;
  tables_used?: string[];
  answer?: string;
  missing_information?: string[];
}

export interface QueryData {
  id: string;
  name: string;
  query: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  visibility: 'public' | 'private';
  owner?: string;
  created_at: string;
  storage_used?: number;
  max_storage?: number;
  is_orphan?: boolean;
  is_yours?: boolean;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  workspace_id: string;
  user_id?: string;
  message_metadata?: Record<string, unknown>;
  is_sql_query: boolean;
  created_at: string;
}

// API functions
export const workspaceApi = {
  updateWorkspace: async (workspaceId: string, data: { name?: string; visibility?: 'public' | 'private' }): Promise<Workspace> => {
    const response = await apiClient.put(`/v1/workspaces/${workspaceId}`, data);
    return response.data;
  },
  claimWorkspace: async (workspaceId: string): Promise<Workspace> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/claim`);
    return response.data;
  },
  getFiles: async (workspaceId: string): Promise<FileData[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/files/`);
    return response.data;
  },
  
  getTables: async (workspaceId: string): Promise<TableData[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/tables/`);
    return response.data;
  },
  
  executeQuery: async (workspaceId: string, query: string, page: number = 1, signal?: AbortSignal, count?: boolean): Promise<QueryResult> => {
    const countParam = count ? '&count=true' : '';
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/query?page=${page}${countParam}`, {
      query
    }, {
      signal
    });
    return response.data;
  },

  exportQueryAsCsv: async (workspaceId: string, query: string): Promise<Blob> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/query/csv`, {query}, {
      responseType: 'blob',
    });
    return response.data;
  },

  saveQuery: async (workspaceId: string, name: string, query: string): Promise<{id: string, name: string, query: string, created_at: string}> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/queries/`, {
      name,
      query
    });
    return response.data;
  },

  getQueries: async (workspaceId: string): Promise<QueryData[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/queries/`);
    return response.data;
  },

  deleteQuery: async (workspaceId: string, queryId: string): Promise<void> => {
    await apiClient.delete(`/v1/workspaces/${workspaceId}/queries/${queryId}`);
  },

  deleteFile: async (workspaceId: string, fileId: string): Promise<void> => {
    await apiClient.delete(`/v1/workspaces/${workspaceId}/files/${fileId}`);
  },

  getWorkspaces: async (): Promise<Workspace[]> => {
    const response = await apiClient.get('/v1/workspaces/');
    return response.data;
  },

  createWorkspace: async (name: string, visibility: 'public' | 'private' = 'public'): Promise<Workspace> => {
    const response = await apiClient.post('/v1/workspaces/', { name, visibility });
    return response.data;
  },

  deleteWorkspace: async (workspaceId: string): Promise<void> => {
    await apiClient.delete(`/v1/workspaces/${workspaceId}`);
  },

  // Chat API methods
  getChatMessages: async (workspaceId: string): Promise<ChatMessage[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/chat/messages`);
    return response.data;
  },

  clearChatMessages: async (workspaceId: string): Promise<void> => {
    await apiClient.delete(`/v1/workspaces/${workspaceId}/chat/messages`);
  },

  queryWithAI: async (workspaceId: string, prompt: string): Promise<AIQueryResult> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/ai/query`, {
      query: prompt
    });
    return response.data;
  },
};

export default apiClient
