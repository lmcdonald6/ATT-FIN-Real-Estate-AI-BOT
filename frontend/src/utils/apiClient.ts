import axios from 'axios';

// API base URL - would come from environment variables in production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sentiment analysis API calls
export const sentimentApi = {
  // Analyze a ZIP code
  analyzeZip: async (zip: string, force: boolean = false) => {
    try {
      const response = await apiClient.post('/analyze', { zip, force });
      return response.data;
    } catch (error) {
      console.error('Error analyzing ZIP code:', error);
      throw error;
    }
  },
  
  // Get sentiment data for a ZIP code
  getSentiment: async (zip: string) => {
    try {
      const response = await apiClient.get(`/api/sentiment/${zip}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching sentiment data:', error);
      throw error;
    }
  },
  
  // Process a batch of ZIP codes or a tier
  processBatch: async (tier: string, mode: string = 'batch') => {
    try {
      const response = await apiClient.post('/analyze/batch', { tier, mode });
      return response.data;
    } catch (error) {
      console.error('Error processing batch:', error);
      throw error;
    }
  },
  
  // Get logs from the Python engine
  getLogs: async (lines: number = 100) => {
    try {
      const response = await apiClient.get(`/analyze/logs?lines=${lines}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching logs:', error);
      throw error;
    }
  }
};

// Persona API calls
export const personaApi = {
  // Get list of available personas
  getPersonas: async () => {
    try {
      const response = await apiClient.get('/api/persona/list');
      return response.data;
    } catch (error) {
      console.error('Error fetching personas:', error);
      throw error;
    }
  },
  
  // Get persona match for a ZIP code
  getPersonaMatch: async (personaId: string, zip: string) => {
    try {
      const response = await apiClient.get(`/api/persona/${personaId}/${zip}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching persona match:', error);
      throw error;
    }
  }
};

// Natural language query API calls
export const askApi = {
  // Ask a question about a neighborhood
  askQuestion: async (query: string, zip?: string) => {
    try {
      const response = await apiClient.post('/api/ask', { query, zip });
      return response.data;
    } catch (error) {
      console.error('Error asking question:', error);
      throw error;
    }
  }
};

export default apiClient;
