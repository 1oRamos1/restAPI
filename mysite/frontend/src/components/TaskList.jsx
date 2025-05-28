import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useParams } from 'react-router-dom';

function TaskDetail() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [solution, setSolution] = useState('');

  useEffect(() => {
    api.get(`user/tasks/${taskId}/`)
      .then(res => {
        setTask(res.data);
        setSolution(res.data.solution || '');
      })
      .catch(err => console.error(err));
  }, [taskId]);

  function handleSubmit(e) {
    e.preventDefault();
    api.put(`user/tasks/${taskId}/`, { solution })
      .then(res => {
        setTask(res.data);
        alert('Solution submitted and graded');
      })
      .catch(err => console.error(err));
  }

  if (!task) return <p>Loading task...</p>;

  return (
    <div>
      <h1>Task Detail</h1>
      <p><strong>Task:</strong> {task.task}</p>
      <p><strong>Status:</strong> {task.status}</p>
      <p><strong>Grade:</strong> {task.grade || 'N/A'}</p>
      <p><strong>Review:</strong> {task.review || 'No review yet'}</p>

      <form onSubmit={handleSubmit}>
        <label>Submit Your Solution:</label><br />
        <textarea
          value={solution}
          onChange={e => setSolution(e.target.value)}
          rows={6}
          cols={50}
        />
        <br />
        <button type="submit">Submit Solution</button>
      </form>
    </div>
  );
}

export default TaskDetail;

