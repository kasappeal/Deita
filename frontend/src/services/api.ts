import axios from 'axios'

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
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

// API functions
export const workspaceApi = {
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
      timeout: 0 // 120000, // 2 minutes timeout for export operations
    });
    return response.data;
  },

  saveQuery: async (workspaceId: string, name: string, query: string): Promise<{id: string, name: string, query: string, created_at: string}> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/queries`, {
      name,
      query
    });
    return response.data;
  },

  deleteFile: async (workspaceId: string, fileId: string): Promise<void> => {
    await apiClient.delete(`/v1/workspaces/${workspaceId}/files/${fileId}`);
  },
};

export default apiClient
