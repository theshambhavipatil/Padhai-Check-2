// Backend Configuration
// Update this file to connect to your FastAPI backend

export const BACKEND_CONFIG = {
  // Base URL for your FastAPI backend
  // Development: 'http://localhost:5000' (backend uses port 5000 by default in .replit/replit.md)
  // Production: 'https://api.padhaicheck.com' or your deployed URL
  BASE_URL: 'http://localhost:5000',

  // API Endpoints
  ENDPOINTS: {
    UPLOAD: '/api/upload',
    VERIFY: '/api/verify',
    TRENDS: '/api/trends',
    CLAIM_DETAILS: (id: string) => `/api/claim/${id}`,
  },
  
  // Enable/Disable mock data fallback
  // Set to false to use real backend, true to use mock data for testing
  USE_MOCK_FALLBACK: false,

  // Request timeout (milliseconds)
  TIMEOUT: 30000,
  
  // File upload settings
  UPLOAD: {
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/jpg', 'image/webp', 'application/pdf'],
  },
};

// Helper function to get full endpoint URL
export function getEndpointURL(endpoint: string): string {
  return `${BACKEND_CONFIG.BASE_URL}${endpoint}`;
}