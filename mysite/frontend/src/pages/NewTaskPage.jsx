import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/axios'; // your axios instance with auth interceptor

function TrackDetail() {
  const { trackId } = useParams();
  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!trackId) return;

    api
      .post(`user/tracks/${trackId}/generate-task/`)
      .then(res => setTrack(res.data))
      .catch(err => {
        console.error('Failed to fetch track:', err);
        setTrack(null);
      });
  }, [trackId]);

  const generateNextTask = async () => {
    setLoading(true);
    try {
      const res = await api.post(`user/tracks/${trackId}/generate-task/`, {});
      setTrack(prev => ({
        ...prev,
        tasks: prev?.tasks ? [...prev.tasks, res.data] : [res.data],
      }));
    } catch (err) {
      console.error('Error generating task:', err);
    }
    setLoading(false);
  };

  if (!track) {
    return (
      <div className="p-4">
        <p className="mb-4">No tasks yet for this track.</p>
        <button
          onClick={generateNextTask}
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Start Track'}
        </button>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{track.title}</h1>
      <p className="text-sm text-gray-600 mb-2">
        Progression: {track.progression || 0}%
      </p>

      <h2 className="text-xl font-semibold mt-4">Tasks:</h2>
      <ul className="mb-4">
        {track.tasks && track.tasks.length > 0 ? (
          track.tasks.map(task => (
            <li key={task.id} className="border p-2 my-2 rounded">
              <strong>Task {task.num_of_task}</strong>: {task.task}
              <div className="text-sm text-gray-500">Status: {task.status}</div>
            </li>
          ))
        ) : (
          <li>No tasks yet. Click the button to generate your first task.</li>
        )}
      </ul>

      <button
        onClick={generateNextTask}
        className="bg-blue-600 text-white px-4 py-2 rounded"
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate Next Task'}
      </button>
    </div>
  );
}

export default TrackDetail;
