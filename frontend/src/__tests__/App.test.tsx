import '@testing-library/jest-dom'
import axios from 'axios'
import React from 'react'

import { ChakraProvider } from '@chakra-ui/react'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from 'react-query'
import { BrowserRouter } from 'react-router-dom'

import App from '../App'

jest.mock('axios', () => {
  // Create a mock axios instance
  const mockAxiosInstance = {
    get: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() },
    },
  }
  return {
    __esModule: true,
    default: {
      create: () => mockAxiosInstance,
      get: jest.fn(),
      interceptors: mockAxiosInstance.interceptors,
    },
    // For type compatibility
    create: () => mockAxiosInstance,
  }
})

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
    <BrowserRouter>
      <ChakraProvider>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </ChakraProvider>
    </BrowserRouter>
  )
}

describe('App', () => {

  it('renders without crashing', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    )
    
    expect(screen.getByText('Deita')).toBeInTheDocument()
  })

  it('displays the welcome message', () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    )
    
    expect(screen.getByText('Welcome to Deita')).toBeInTheDocument()
  })

  beforeEach(() => {
    // Mock GET /v1/ and /v1/health for the axios instance
    const mockAxiosInstance = (axios as any).create();
    mockAxiosInstance.get.mockImplementation((url: string) => {
      if (url === '/v1/') {
        return Promise.resolve({ data: { message: 'Hello from backend!', version: '1.0.0', environment: 'test' } })
      }
      if (url === '/v1/health') {
        return Promise.resolve({ data: { status: 'healthy', message: 'All systems go!', version: '1.0.0', timestamp: new Date().toISOString() } })
      }
      return Promise.reject(new Error('not mocked'))
    })
  })
})
