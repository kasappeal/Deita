import '@testing-library/jest-dom'

// Mock the config/env module for Jest tests
jest.mock('./config/env', () => ({
  env: {
    API_URL: 'http://localhost:8000/v1',
    APP_NAME: 'Deita',
    ENVIRONMENT: 'test',
    IS_PRODUCTION: false,
    IS_DEVELOPMENT: false,
  },
  validateEnvironment: jest.fn(),
}))

// Mock import.meta for any direct usage
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        VITE_API_URL: 'http://localhost:8000/v1',
        VITE_APP_NAME: 'Deita',
        VITE_ENVIRONMENT: 'test',
      }
    }
  },
  writable: true
})