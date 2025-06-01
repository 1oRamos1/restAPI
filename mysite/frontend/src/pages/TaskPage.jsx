import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';

function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [solution, setSolution] = useState('');
  const [grading, setGrading] = useState(null);
  const [review, setReview] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get(`user/tasks/${taskId}/`)
      .then(res => {
        setTask(res.data);
        setSolution(res.data.solution || '');
        setGrading(res.data.grading || null);
        setReview(res.data.review || '');
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load task.');
        setLoading(false);
      });
  }, [taskId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.put(`user/tasks/${taskId}/`, { solution });
      setGrading(res.data.grading);
      setReview(res.data.review);
    } catch {
      alert('Failed to submit solution.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextTask = async () => {
    try {
      const res = await api.post(`/user/tracks/${task.user_learning_track_id}/generate-task/`);
      const newTask = res.data;
      navigate(`/tasks/${newTask.id}`);
    } catch (err) {
      console.error('Failed to generate next task:', err);
      alert('Failed to generate next task.');
    }
  };

  if (loading) return <div>Loading task...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="p-4">
      <p className="mb-4 whitespace-pre-line">{task.task}</p>

      {submitting ? (
        <div className="text-blue-600 font-semibold">Submitting solution and waiting for review...</div>
      ) : grading === null ? (
        <form onSubmit={handleSubmit}>
          <label className="block mb-1 font-semibold" htmlFor="solution">Your Solution:</label>
          <textarea
            id="solution"
            value={solution}
            onChange={(e) => setSolution(e.target.value)}
            rows={8}
            className="w-full border p-2 mb-4"
            required
          />
          <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
            Submit Solution
          </button>
        </form>
      ) : (
        <>
          <div className="mt-4 p-4 border rounded bg-gray-100">
            <h3 className="font-bold mb-2">AI Review:</h3>
            <p className="whitespace-pre-line">{review}</p>
            <p className="mt-2"><strong>Grading:</strong> {grading} / 5</p>
          </div>

          <div className="mt-6 flex gap-4">
            <button
              className="bg-yellow-500 text-white px-4 py-2 rounded"
              onClick={() => {
                setGrading(null);
                setReview('');
                setSolution('');
              }}
            >
              Submit Again
            </button>
            <button
              className="bg-green-600 text-white px-4 py-2 rounded"
              onClick={handleNextTask}
            >
              Next Task
            </button>
            <button
              className="bg-gray-600 text-white px-4 py-2 rounded"
              onClick={() => navigate('/')}
            >
              Exit
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default TaskDetail;


