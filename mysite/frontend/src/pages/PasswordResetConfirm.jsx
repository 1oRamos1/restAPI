import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';

export default function PasswordResetConfirm() {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const [newPassword1, setNewPassword1] = useState('');
  const [newPassword2, setNewPassword2] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleResetConfirm = async () => {
    if (newPassword1 !== newPassword2) {
      setError("Passwords do not match.");
      return;
    }

    try {
      await api.post('http://localhost:8000/dj-rest-auth/password/reset/confirm/', {
        uid,
        token,
        new_password1: newPassword1,
        new_password2: newPassword2
      });
      setSuccess(true);
      setError('');
      setTimeout(() => navigate('/login'), 2500);
    } catch (err) {
      setError('Reset failed. The link may be invalid or expired.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue70 to-blue90 dark:from-gray-900 dark:to-gray-900 flex items-center justify-center px-4">
      <div className="bg-blue0 dark:bg-gray-800 rounded-xl shadow-xl p-10 w-full max-w-md text-center">
        <h1 className="text-2xl font-bold text-blue70 dark:text-cyan-100 mb-6">Set New Password</h1>

        {success ? (
          <p className="text-green-600 dark:text-green-300">
            Your password has been changed. Redirecting to login...
          </p>
        ) : (
          <>
            {error && <p className="text-red-600 mb-4 text-sm">{error}</p>}

            <input
              type="password"
              placeholder="New password"
              value={newPassword1}
              onChange={(e) => setNewPassword1(e.target.value)}
              className="w-full mb-3 p-3 border border-gray-300 rounded-md"
            />

            <input
              type="password"
              placeholder="Confirm new password"
              value={newPassword2}
              onChange={(e) => setNewPassword2(e.target.value)}
              className="w-full mb-4 p-3 border border-gray-300 rounded-md"
            />

            <button
              onClick={handleResetConfirm}
              className="w-full bg-blue70 hover:bg-blue50 text-white py-2 rounded-md font-semibold transition dark:bg-cyan-900 dark:text-cyan-200 shadow-md"
            >
              Confirm Reset
            </button>
          </>
        )}
      </div>
    </div>
  );
}
