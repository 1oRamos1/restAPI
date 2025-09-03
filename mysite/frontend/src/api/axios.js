import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: 'https://tracker-production-387a.up.railway.app/',
    withCredentials: true,
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken',
});

// Response interceptor to update CSRF token
api.interceptors.response.use(
    (response) => {
        // If response contains csrfToken, store it
        if (response.data && response.data.csrfToken) {
            // You can store it in a variable or use it directly
            window.latestCsrfToken = response.data.csrfToken;
        }
        return response;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.request.use(config => {
    // Try to get CSRF token from cookie first, then from stored variable
    let csrfToken = Cookies.get('csrftoken') || window.latestCsrfToken;

    console.log('CSRF Token:', csrfToken);

    if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
});

export default api;