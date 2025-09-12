import axios from 'axios';
import Cookies from 'js-cookie';

// Determine backend URL based on environment
const baseURL =
  window.location.hostname === 'localhost'
    ? 'http://localhost:8000/api/v1/tracker/'
    : 'https://tracker-2528.onrender.com/api/v1/tracker/';

const api = axios.create({
  baseURL,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Store latest CSRF token if returned by server
api.interceptors.response.use(
  (response) => {
    if (response.data && response.data.csrfToken) {
      window.latestCsrfToken = response.data.csrfToken;
    }
    return response;
  },
  (error) => Promise.reject(error)
);

// Attach CSRF token to every request
api.interceptors.request.use((config) => {
  const csrfToken = Cookies.get('csrftoken') || window.latestCsrfToken;
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

export default api;
