import React, { useState } from 'react';
import api from '../api/axios';

export default function PasswordReset() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleReset = async () => {
  try {
    const response = await api.post('/dj-rest-auth/password/reset/', { email });
    setSubmitted(true);
    setError('');
  } catch (err) {
    setError(err.response?.data?.error || 'Something went wrong.');
    setSubmitted(false);
  }
};


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue70 to-blue90 dark:from-gray-900 dark:to-gray-900 flex items-center justify-center px-4">
      <div className="bg-blue0 dark:bg-gray-800 rounded-xl shadow-xl p-10 w-full max-w-md text-center">
        <h1 className="text-2xl font-bold text-blue70 dark:text-cyan-100 mb-6">Reset Your Password</h1>

        {submitted ? (
  <p className="text-green-600 dark:text-green-300">
    Check your email for the reset link.
  </p>
) : (
  <>
    {error && <p className="text-red-600 mb-4 text-sm">{error}</p>}
    <input
      type="email"
      placeholder="Enter your email"
      value={email}
      onChange={(e) => setEmail(e.target.value)}
      className="w-full mb-4 p-3 border border-gray-300 rounded-md"
    />
    <button onClick={handleReset}
    className="w-full bg-blue70 hover:bg-blue50 text-white py-2 rounded-md
    font-semibold transition dark:bg-cyan-900 dark:text-cyan-200 shadow-md" >
     Send Reset Link </button>
  </>
        )}
      </div>
    </div>
  );
}
