import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import api from './api/axios';

import Login from './pages/Login';
import HomePage from './pages/HomePage';
import CategoryPage from './pages/CategoryPage';
import TrackPage from './pages/TrackPage';
import TaskPage from './pages/TaskPage';
import NewTaskPage from './pages/NewTaskPage';

function App() {
  useEffect(() => {
  api.get('auth/csrf/')
    .then(() => console.log('CSRF cookie set'))
    .catch(() => console.error('Failed to get CSRF cookie'));
}, []);

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/category/:categoryId" element={<CategoryPage />} />
        <Route path="/track/:userLearningTrackId" element={<TrackPage />} />
        <Route path="/tasks/:taskId" element={<TaskPage />} />
        <Route path="/track/:trackId/new-task" element={<NewTaskPage />} />
      </Routes>
    </Router>
  );
}

export default App;

