/**
 * Environment configuration
 * Centralized access to environment variables with type safety and defaults
 */

export const env = {
  // API Configuration
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/v1',
  
  // App Configuration
  APP_NAME: import.meta.env.VITE_APP_NAME || 'Deita',
  ENVIRONMENT: import.meta.env.VITE_ENVIRONMENT || 'development',
  
  // Feature flags and other config
  IS_PRODUCTION: import.meta.env.VITE_ENVIRONMENT === 'production',
  IS_DEVELOPMENT: import.meta.env.VITE_ENVIRONMENT === 'development',
} as const

// Type for environment values
export type Environment = typeof env

// Validation function to ensure required environment variables are present
export function validateEnvironment(): void {
  const requiredVars = ['API_URL', 'APP_NAME'] as const
  
  for (const varName of requiredVars) {
    if (!env[varName]) {
      throw new Error(`Required environment variable ${varName} is not set`)
    }
  }
  
  console.log('Environment configuration loaded:', {
    API_URL: env.API_URL,
    APP_NAME: env.APP_NAME,
    ENVIRONMENT: env.ENVIRONMENT,
    IS_PRODUCTION: env.IS_PRODUCTION,
  })
}