import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

export async function analyzeZip(zip: string) {
  const { data } = await axios.get(`${API_BASE_URL}/analyze?zip_code=${zip}`);
  return data;
}

// Additional API functions
export async function getSentiment(zip: string) {
  const { data } = await axios.get(`${API_BASE_URL}/sentiment?zip_code=${zip}`);
  return data;
}

export async function getForecast(zip: string, months: number = 12) {
  const { data } = await axios.get(`${API_BASE_URL}/forecast?zip_code=${zip}&months=${months}`);
  return data;
}

export async function getDiscoverRecommendations(persona: string, limit: number = 5) {
  const { data } = await axios.get(`${API_BASE_URL}/discover?persona=${persona}&limit=${limit}`);
  return data;
}

export async function askQuestion(query: string, zip?: string) {
  const { data } = await axios.post(`${API_BASE_URL}/gpt-query`, { query, zip });
  return data;
}

// Create a default axios instance with common configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
