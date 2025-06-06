import axios from 'axios';

const API_BASE_URL = '/api';
export const planTrip = async (tripData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/plan-trip`, tripData);
    return response.data;
  } catch (error) {
    console.error("Error calling planTrip API:", error.response || error.message);
    throw error.response?.data || { error: "Network error or server unavailable. Please try again." };
  }
};

export const getHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return response.data;
    } catch (error) {
        console.error("Error calling health API:", error.response || error.message);
        throw error.response?.data || { error: "Backend health check failed." };
    }
}