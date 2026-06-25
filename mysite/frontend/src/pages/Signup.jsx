import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

function Signup() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setIsAuthenticated, openLoginModal } = useContext(AuthContext);

  const handleSignup = async () => {
    if (password1 !== password2) {
      setError("Passwords do not match");
      return;
    }
    try {
      await api.post('/auth/signup/', {
        username,
        email,
        password1,
        password2,
      });
      setIsAuthenticated(true);
      setError('');
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Signup failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue70 to-blue90 dark:from-gray-900 dark:to-gray-900 flex items-center justify-center px-4">
      <div className="bg-blue0 dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md relative overflow-hidden">
        <div className="px-6 py-9 flex flex-col items-center">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-cyan-100 mb-4">Sign Up</h1>

          {error && <p className="text-red-600 mb-2 text-sm">{error}</p>}

          <div className="w-full max-w-sm flex flex-col gap-3">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="p-3 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="p-3 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
            />
            <input
              type="password"
              placeholder="Password"
              value={password1}
              onChange={(e) => setPassword1(e.target.value)}
              className="p-3 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
            />
            <input
              type="password"
              placeholder="Confirm Password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              className="p-3 border border-gray-300 rounded-md bg-white text-gray-900 placeholder-gray-400"
            />

            <button
              onClick={handleSignup}
              className="bg-blue70 hover:bg-blue50 text-white px-6 py-2 rounded-md font-semibold transition dark:bg-cyan-900 dark:text-cyan-200 shadow-md"
            >
              Sign Up
            </button>

            <button
              onClick={openLoginModal}
              className="mt-2 border border-cyan-600 text-blue70 py-2 rounded-md font-semibold hover:bg-blue70 hover:text-white dark:hover:bg-cyan-900 dark:hover:text-cyan-200"
            >
              Already have an account? Log In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Signup;