import axios from 'axios';

const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    withCredentials: true,
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken',
});




// Before every POST/PUT/DELETE — fetch a fresh CSRF token
api.interceptors.request.use(async (config) => {
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
        try {
            const res = await axios.get(
                `${process.env.REACT_APP_API_URL}auth/csrf/`,
                { withCredentials: true }
            );
            config.headers['X-CSRFToken'] = res.data.csrfToken;
        } catch (e) {
            // continue anyway
        }
    }
    return config;
});

export default api;
