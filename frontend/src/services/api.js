import axios from 'axios';

// Use relative URL for production (HuggingFace Spaces) or localhost for development
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies in requests
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


