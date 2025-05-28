import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link, useParams, useNavigate } from 'react-router-dom';

function UserTrackDetail() {
  const { trackId } = useParams();
  const [userTrack, setUserTrack] = useState(null);
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    api.get(`user/tracks/${trackId}/`)
      .then(res => {
        setUserTrack(res.data);
        // Assuming userTrack includes a list of tasks or tasks are related
        // But since you didn't provide a tasks endpoint per track, fetch tasks separately if needed
      })
      .catch(err => console.error(err));
  }, [trackId]);

  // You probably want to fetch tasks separately for this user track:
  useEffect(() => {
    api.get('user/tasks/')  // You may need to create this endpoint to get user's tasks or filter by track
      .then(res => {
        // Filter tasks by userTrack id if needed
        const filteredTasks = res.data.filter(t => t.user_learning_track === parseInt(trackId));
        setTasks(filteredTasks);
      })
      .catch(err => console.error(err));
  }, [trackId]);

  function continueProgress() {
    // Navigate to task page or generate next task page
    navigate(`/track/${trackId}/new-task`);
  }

  if (!userTrack) return <p>Loading...</p>;

  return (
    <div>
      <h1>{userTrack.learning_track.title || userTrack.learning_track.name} Progress</h1>
      <h2>Tasks Done</h2>
      <ul>
        {tasks.map(task => (
          <li key={task.id}>
            <Link to={`/task/${task.id}`}>{task.task.substring(0, 50)}...</Link> - Status: {task.status}
          </li>
        ))}
      </ul>
      <button onClick={continueProgress}>Continue Progress (Generate Next Task)</button>
    </div>
  );
}

export default UserTrackDetail;
