import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false); // 🔥 modal state

  useEffect(() => {
    api.get('/dj-rest-auth/user/')
      .then(res => {
        setIsAuthenticated(true);
        setUser(res.data);
        console.log("✅ Authenticated user:", res.data);
      })
      .catch(err => {
        setIsAuthenticated(false);
        setUser(null);
        console.log("❌ Guest:", err.response?.status);
      });
  }, []);

  const openLoginModal = () => setShowLoginModal(true);  // 🔥 expose modal trigger
  const closeLoginModal = () => setShowLoginModal(false);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        setIsAuthenticated,
        user,
        showLoginModal,
        openLoginModal,
        closeLoginModal
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
