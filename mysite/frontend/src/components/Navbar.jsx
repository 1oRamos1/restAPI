import React, { useContext, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

export default function Navbar({ onLoginClick }) {
  const navigate = useNavigate();
  const { isAuthenticated, setIsAuthenticated } = useContext(AuthContext);
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

  const handleLogout = () => {
    if (!window.confirm('Are you sure you want to logout?')) return;

    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

    api.post('dj-rest-auth/logout', {}, {
      headers: { 'X-CSRFToken': csrftoken },
      withCredentials: true,
    })
      .then(() => {
        setIsAuthenticated(false);
        navigate('/');
      })
      .catch(err => console.error('Logout failed:', err));
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 shadow-lg border-b border-cyan-100 dark:border-gray-700">
      <div className="w-full px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-3xl font-extrabold text-blue80 dark:text-cyan-100 tracking-tight">
          CodeTracks
        </Link>

        <div className="flex space-x-4 items-center">
          <Link to="/" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
            Home
          </Link>

          <Link to='/categories' className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
            Our Courses
          </Link>

          {isAuthenticated && (
            <Link to="/my-tracks" className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
              My Journey
            </Link>
          )}

          {isAuthenticated ? (
            <button onClick={handleLogout} className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
              Log Out
            </button>
          ) : (
            <button onClick={onLoginClick} className="px-4 py-2 rounded-full font-semibold text-blue70 dark:text-cyan-100 hover:bg-blue70 dark:hover:bg-cyan-800 hover:text-white transition shadow">
              Log In
            </button>
          )}

          <Link to="/buy-pro" className="bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-semibold px-4 py-2 rounded-full shadow-md hover:scale-105 transition-transform duration-300">
            Pro Version
          </Link>

          <button onClick={toggleDark} className="px-3 py-2 rounded-full text-sm font-medium bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-500 text-gray-800 dark:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-600 transition">
            {darkMode ? '☀ Light' : '🌙 Dark'}
          </button>
        </div>
      </div>
    </nav>
  );
}

