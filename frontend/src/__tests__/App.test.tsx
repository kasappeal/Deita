import '@testing-library/jest-dom'
import axios from 'axios'
import React from 'react'


import { ChakraProvider } from '@chakra-ui/react'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import { AuthProvider } from '../contexts/AuthContext'

jest.mock('axios', () => {
  // Create a mock axios instance
  const mockAxiosInstance = {
    get: jest.fn(),
    post: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  };
  return {
    __esModule: true,
    default: {
      create: () => mockAxiosInstance,
      get: jest.fn(),
      post: jest.fn(),
      interceptors: mockAxiosInstance.interceptors,
    },
    create: () => mockAxiosInstance,
  };
});

// Create a test wrapper with all required providers
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <AuthProvider>
      <BrowserRouter>
        <ChakraProvider>
          <QueryClientProvider client={queryClient}>
            {children}
          </QueryClientProvider>
        </ChakraProvider>
      </BrowserRouter>
    </AuthProvider>
  )
}

describe('App', () => {

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    )
    
    expect(screen.getByText('Your workspaces - Deita')).toBeInTheDocument()
  })

  it('displays the workspace header', async () => {
    // Setup: navigate to a specific workspace
    window.history.pushState({}, 'Test Workspace', '/workspaces/ws_test');
    
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );
    // Wait for the workspace header to appear after loading
    expect(await screen.findByText('Test Workspace')).toBeInTheDocument();
  });

  beforeEach(() => {
    // Mock GET and POST for the axios instance
    const mockAxiosInstance = (axios as unknown as { create: () => any }).create();
    mockAxiosInstance.get.mockImplementation((url: string) => {
      if (url === '/v1/') {
        return Promise.resolve({ data: { message: 'Hello from backend!', version: '1.0.0', environment: 'test' } });
      }
      if (url === '/v1/health') {
        return Promise.resolve({ data: { status: 'healthy', message: 'All systems go!', version: '1.0.0', timestamp: new Date().toISOString() } });
      }
      if (url.startsWith('/v1/workspaces/') && url.endsWith('/files/')) {
        return Promise.resolve({ data: [] }); // Return empty array for files
      }
      if (url.startsWith('/v1/workspaces/')) {
        return Promise.resolve({ data: { id: 'ws_test', name: 'Test Workspace', visibility: 'public', owner: null, created_at: new Date().toISOString() } });
      }
      if (url === '/v1/auth/me') {
        return Promise.resolve({ data: { id: 'user_1', email: 'test@example.com', name: 'Test User' } });
      }
      return Promise.reject(new Error('not mocked'));
    });
    mockAxiosInstance.post.mockImplementation((url: string, body: any) => {
      if (url === '/v1/workspaces/') {
        return Promise.resolve({ data: { id: 'ws_test', name: body.name, visibility: body.visibility, owner: null, created_at: new Date().toISOString() } });
      }
      return Promise.reject(new Error('not mocked'));
    });
    // Also mock post/get on default export for direct calls
    (axios as any).post = mockAxiosInstance.post;
    (axios as any).get = mockAxiosInstance.get;
  });
})
