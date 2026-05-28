import React, { createContext, useState, useEffect } from 'react';
import api from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // 1. הוצאנו את הלוגיקה לפונקציה נפרדת שניתן לקרוא לי מכל מקום
  const checkAuthStatus = async () => {
    try {
      const res = await api.get('/auth/user/', { withCredentials: true });
      setIsAuthenticated(true);
      setUser(res.data);
      if (res.data?.is_pro === true) {
      } else {
      }
      return res.data;
    } catch (err) {
      setIsAuthenticated(false);
      setUser(null);
      throw err;
    }
  };

  // 2. ה-useEffect המקורי רק קורא לפונקציה החדשה בטעינה הראשונית של האתר
  useEffect(() => {
    checkAuthStatus().catch(() => {});
  }, []);

  const openLoginModal = () => setShowLoginModal(true);
  const closeLoginModal = () => setShowLoginModal(false);

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        setIsAuthenticated,
        user,
        setUser,
        checkAuthStatus,
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
