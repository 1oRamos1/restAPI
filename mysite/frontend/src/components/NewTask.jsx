import React, { useState } from 'react';
import api from '../api/axios';
import { useParams, useNavigate } from 'react-router-dom';

function NewTask() {
  const { userLearningTrackId } = useParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const generateTask = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.post(`user/tracks/${userLearningTrackId}/generate-task/`);
      const task = res.data;
      navigate(`/tasks/${task.id}`);
    } catch (err) {
      console.error('Task generation error:', err);
      setError('Failed to generate task. Are you logged in?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Generate New Task</h1>
      <button onClick={generateTask} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Next Task'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default NewTask;



