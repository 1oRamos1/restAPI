// your current api.js
import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/tracker/',
  withCredentials: true,  // send cookies
});

api.interceptors.request.use(config => {
  const csrfToken = Cookies.get('csrftoken');
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;  // add CSRF header to every request
  }
  return config;
});

export default api;
