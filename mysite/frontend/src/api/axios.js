// your current api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/tracker/',
  withCredentials: true,
});

// Add this interceptor
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access');
    console.log("Sending token:", token);  // <--- Add this line here
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);
export default api;
