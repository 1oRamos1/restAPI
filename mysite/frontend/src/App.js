import React, { useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider } from './context/AuthContext';

import Layout from './layout/Layout';
import Signup from './pages/Signup';
import PasswordReset from './pages/PasswordReset';
import PasswordResetConfirm from './pages/PasswordResetConfirm';
import HomePage from './pages/HomePage';
import Categories from './pages/Categories';
import CategoryPage from './pages/CategoryPage';
import TrackPage from './pages/TrackPage';
import UserTracksList from './pages/UserTracksList';
import TaskPage from './pages/TaskPage';
import NewTaskPage from './pages/NewTaskPage';
import BuyProPage from './pages/BuyProPage';
import PaymentPage from './pages/PaymentPage';
import CreateTrackPage from './pages/CreateTrackPage';


// 🔁 Set theme on initial load
function applyTheme() {
  const userPref = localStorage.theme;
  const systemPref = window.matchMedia('(prefers-color-scheme: dark)').matches;
  if (userPref === 'dark' || (!userPref && systemPref)) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

function App() {
  useEffect(() => {
    applyTheme();
  }, []);

  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <GoogleOAuthProvider clientId="1054941900001-8o9cl0tqu27744cof3dsrti6v6f9r6ns.apps.googleusercontent.com">
      <AuthProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/password-reset" element={<PasswordReset />} />
            <Route path="/password/reset/confirm/:uid/:token/" element={<PasswordResetConfirm />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/" element={<HomePage />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/category/:categoryId" element={<CategoryPage />} />
            <Route path="/my-tracks" element={<UserTracksList />} />
            <Route path="/buy-pro" element={<BuyProPage />} />
            <Route path="/payment" element={<PaymentPage />} />
            <Route path="/create-track" element={<CreateTrackPage />} />
            <Route path="/track/:trackId/:userTrackId" element={<TrackPage />} />
            <Route path="/tasks/:taskId" element={<TaskPage />} />
            <Route path="/tasks/:taskId/submit-again" element={<TaskPage isSubmitAgain />} />
            <Route path="/track/:trackId/new-task" element={<NewTaskPage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
