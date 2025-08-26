import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/axios';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_AUTH_GOOGLE_CLIENT_ID

function getCsrfTokenFromCookie() {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    ?.split('=')[1];
}

export default function LoginModal({ onClose }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setIsAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    try {
      if (!window.google?.accounts?.id) return;

      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleLogin,
      });

      window.google.accounts.id.renderButton(
        document.getElementById('google-login-button'),
        {
          theme: 'outline',
          size: 'large',
          width: '380',
        }
      );
    } catch (e) {
      console.error('Google login script not ready:', e);
    }
  }, []);

 const handleGoogleLogin = async (response) => {
  try {
    await api.get('/auth/csrf/'); // Get token
    await api.post('/dj-rest-auth/google/', { id_token: response.credential }); // Login

    setIsAuthenticated(true);
    setError('');
    onClose();
    window.location.reload();
  } catch (err) {
    console.error(err);
    setError('Google login failed. Try again.');
  }
};

const handleLogin = async () => {
  try {
    await api.post(
      '/auth/login/',
      { username, password },
      {
        withCredentials: true,
        headers: {
          'X-CSRFToken': getCsrfTokenFromCookie(),
        },
      }
    );
    setIsAuthenticated(true);
    setError('');
    onClose();
    window.location.reload();
  } catch (err) {
    const detail = err.response?.data?.detail;
    if (
      detail?.toLowerCase().includes('no active account') ||
      detail?.toLowerCase().includes('unable to log in') ||
      detail?.toLowerCase().includes('not found')
    ) {
      setError("You're not signed in. Please sign up.");
    } else {
      setError('Login failed. Check your credentials.');
    }
  }
};

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center px-4">
      <div className="bg-blue0 rounded-xl shadow-xl w-full max-w-md relative overflow-hidden">
        <div className="px-6 py-9 flex flex-col items-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Login</h1>

          {error && <p className="text-red-600 mb-2 text-sm">{error}</p>}

          <div className="w-full max-w-sm flex flex-col gap-3">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="p-3 border border-gray-300 rounded-md"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="p-3 border border-gray-300 rounded-md"
            />

            <button
              onClick={handleLogin}
              className="bg-blue70 hover:bg-blue50 text-white px-6 py-2 rounded-md font-semibold transition dark:bg-cyan-900 dark:text-cyan-200 shadow-md"
            >
              Login
            </button>

            <div className="text-center">
              <button
                onClick={() => {
                  onClose();
                  navigate('/password-reset');
                }}
                className="text-sm text-blue70 dark:text-cyan-700 underline hover:text-blue90 dark:hover:text-cyan-400 mt-1"
              >
                Forgot Password?
              </button>
            </div>

            <div className="text-center text-gray-500 mt-2">or</div>

            <div
              id="google-login-button"
              className="flex justify-center w-full mt-1"
            ></div>

            <button
              onClick={() => {
                onClose();
                navigate('/signup');
              }}
              className="mt-2 border border-cyan-600 text-blue70 py-2 rounded-md font-semibold hover:bg-blue70 hover:text-white dark:hover:bg-cyan-900 dark:hover:text-cyan-200"
            >
              Sign Up
            </button>
          </div>

          <button
            onClick={onClose}
            className="absolute top-2 right-4 text-2xl text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
}
