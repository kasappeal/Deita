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
}

// API functions
export const workspaceApi = {
  getFiles: async (workspaceId: string): Promise<FileData[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/files`);
    return response.data;
  },
  
  getTables: async (workspaceId: string): Promise<TableData[]> => {
    const response = await apiClient.get(`/v1/workspaces/${workspaceId}/tables`);
    return response.data;
  },
  
  executeQuery: async (workspaceId: string, query: string): Promise<QueryResult> => {
    const response = await apiClient.post(`/v1/workspaces/${workspaceId}/query`, {
      query
    });
    return response.data;
  },
};

export default apiClient
