import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

function TaskDetail() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [solution, setSolution] = useState('');
  const [grading, setGrading] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const token = localStorage.getItem('access');

  useEffect(() => {
    axios
      .get(`user/tasks/${taskId}/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then(res => {
        setTask(res.data);
        setSolution(res.data.solution || '');
        setGrading(res.data.grading || null);
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to load task.');
        setLoading(false);
      });
  }, [taskId, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.put(
        `http://localhost:8000/api/v1/tracker/user/tasks/${taskId}/`,
        { solution },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      alert('Solution submitted!');
      navigate(-1);
    } catch (err) {
      alert('Failed to submit solution.');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">{task.title}</h1>
      <p className="mb-2">{task.description}</p>

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

      {grading !== null && (
        <p className="mt-4">
          <strong>Grading:</strong> {grading}
        </p>
      )}

      <Link to={-1} className="text-gray-500 underline mt-4 inline-block">← Back</Link>
    </div>
  );
}

export default TaskDetail;
