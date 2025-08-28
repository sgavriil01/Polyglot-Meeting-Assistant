import axios from 'axios';

// Use relative URL for production (HuggingFace Spaces) or localhost for development
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';

// Session management using localStorage and headers
let sessionId = localStorage.getItem('session_id') || null;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Keep for any other cookies
});

// Request interceptor to add session ID header
api.interceptors.request.use((config) => {
  if (sessionId) {
    config.headers['X-Session-ID'] = sessionId;
  }
  return config;
});

// Response interceptor to capture session ID from headers
api.interceptors.response.use((response) => {
  const newSessionId = response.headers['x-session-id'];
  if (newSessionId && newSessionId !== sessionId) {
    sessionId = newSessionId;
    localStorage.setItem('session_id', sessionId);
    console.log('📝 Session ID updated:', sessionId.substring(0, 8) + '...');
  }
  return response;
});

// API service functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get statistics
  getStats: async () => {
    const response = await api.get('/statistics');
    return response.data;
  },

  // Search meetings
  searchMeetings: async (query, topK = 10, contentTypes = null) => {
    const response = await api.post('/search', {
      query,
      top_k: topK,
      content_types: contentTypes,
    });
    return response.data;
  },

  // Upload file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get meetings list
  getMeetings: async () => {
    const response = await api.get('/meetings');
    return response.data;
  },

  // Export results
  exportResults: async (query, format = 'json') => {
    const response = await api.get('/export', {
      params: { q: query, format },
    });
    return response.data;
  },
};

export default apiService;


