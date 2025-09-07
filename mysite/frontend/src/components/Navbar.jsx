import React, { useContext, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';
import { SparklesIcon } from '@heroicons/react/24/solid'

export default function Navbar({ onLoginClick }) {
  const navigate = useNavigate();
  const { isAuthenticated, setIsAuthenticated, user } = useContext(AuthContext);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const stored = localStorage.theme;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = stored === 'dark' || (!stored && prefersDark);
    setDarkMode(isDark);
    document.documentElement.classList.toggle('dark', isDark);
  }, []);

  const toggleDark = () => {
    const nextMode = !darkMode;
    setDarkMode(nextMode);
    document.documentElement.classList.toggle('dark', nextMode);
    localStorage.theme = nextMode ? 'dark' : 'light';
  };

  const handleLogout = async () => {
      if (!window.confirm('Are you sure you want to logout?')) return;

      try {
        // Get CSRF token
        const csrftoken = document.cookie
          .split('; ')
          .find(row => row.startsWith('csrftoken='))
          ?.split('=')[1];

        // Logout from Django
        await api.post('auth/logout/', {}, {
          headers: { 'X-CSRFToken': csrftoken },
          withCredentials: true,
        });

        // Disable Google auto-login
        if (window.google?.accounts?.id) {
          window.google.accounts.id.disableAutoSelect();
        }

        // Update frontend state
        setIsAuthenticated(false);
        navigate('/');
        window.location.reload();
      } catch (err) {
        console.error('Logout failed:', err);
      }
    };


  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 shadow-lg border-b border-cyan-100 dark:border-gray-700">
      <div className="w-full px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-3xl font-extrabold text-blue80 dark:text-cyan-100 tracking-tight">
          Codyssey
        </Link>

        <div className="flex space-x-4 items-center">
          {/* Always visible buttons */}
          <Link to="/" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
            Home
          </Link>

          <Link to="/categories" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
            Our Courses
          </Link>

          {/* Authenticated user buttons */}
          {isAuthenticated && (
            <>
              <Link to="/my-tracks" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
                My Journey
              </Link>

              {/* Create Track button - only for pro users */}
              {user?.is_pro && (
                <Link to="/create-track" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
                  Create New Track
                </Link>
              )}

              <button
                onClick={handleLogout}
                className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow"
              >
                Log Out
              </button>
            </>
          )}

          {/* Login button for non-authenticated users */}
          {!isAuthenticated && (
            <button
              onClick={onLoginClick}
              className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow"
            >
              Log In
            </button>
          )}

          {/* Pro version button/status */}
          {isAuthenticated && user?.is_pro ? (
            <button
    disabled
    className="flex items-center gap-2 px-4 py-2 rounded-full font-semibold
               bg-gradient-to-r from-yellow-200 via-yellow-600 to-yellow-200
               text-white dark:from-blue40 dark:via-blue70 dark:to-blue40
               cursor-default"
  >
    <SparklesIcon className="w-5 h-5 text-white" />
    Premium
  </button>
          ) : (
            <Link
              to="/buy-pro"
              className="bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-semibold px-4 py-2 rounded-full shadow-md hover:scale-105 transition-transform duration-300"
            >
              Pro Version
            </Link>
          )}

          {/* Always visible dark mode toggle */}
          <button
              onClick={toggleDark}
              className="flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium
                         bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-500
                         text-gray-800 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-600
                         transition"
            >
        {darkMode ? (
         <>
      {/* Sun Icon for Light Mode */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-4 h-5"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M6.995 12c0 2.761 2.246 5.005 5.005 5.005s5.005-2.244 5.005-5.005c0-2.761-2.246-5.005-5.005-5.005s-5.005 2.244-5.005 5.005zm13.002-.75h2.003v1.5h-2.003v-1.5zm-18 0h2.003v1.5H1.997v-1.5zm8.498-7.504h1.5v2.003h-1.5V3.746zm0 18.008h1.5v2.003h-1.5v-2.003zM4.222 5.636l1.061-1.061 1.415 1.415-1.061 1.061-1.415-1.415zm13.081 13.081l1.061-1.061 1.415 1.415-1.061 1.061-1.415-1.415zM18.364 4.222l1.415 1.415-1.061 1.061-1.415-1.415 1.061-1.061zM5.636 19.778l1.415-1.415 1.061 1.061-1.415 1.415-1.061-1.061z" />
      </svg>
      Light
    </>
  ) : (
    <>
      {/* Moon Icon for Dark Mode */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-4 h-5"
        fill="currentColor"
        viewBox="0 0 24 24"
      >
        <path d="M21.75 15.5a8.25 8.25 0 01-11.25-11.25 9 9 0 1011.25 11.25z" />
      </svg>Dark</>
  )}
</button>
        </div>
      </div>
    </nav>
  );
}