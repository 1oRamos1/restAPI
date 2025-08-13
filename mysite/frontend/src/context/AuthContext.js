import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  useEffect(() => {
    api.get('/dj-rest-auth/user/', { withCredentials: true })
      .then(res => {
        setIsAuthenticated(true);
        setUser(res.data);
        console.log("✅ Authenticated user:", res.data);
        if (res.data?.is_pro === true) {
          console.log("💎 Pro user detected");
        } else {
          console.log("👤 Regular user");
        }
      })
      .catch(err => {
        setIsAuthenticated(false);
        setUser(null);
        console.log("❌ Guest:", err.response?.status);
      });
  }, []);

  const openLoginModal = () => setShowLoginModal(true);
  const closeLoginModal = () => setShowLoginModal(false);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        setIsAuthenticated,
        user,
        isPro: user?.is_pro === true,
        showLoginModal,
        openLoginModal,
        closeLoginModal
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
