import React, { useEffect, useState, useContext } from 'react';
import api from '../api/axios';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function UserTrackDetail() {
  const { trackId, userTrackId } = useParams();
  const [userTrack, setUserTrack] = useState(null);
  const [trackInfo, setTrackInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [btnLoading, setBtnLoading] = useState(false);
  const [error, setError] = useState('');
  const { isAuthenticated, openLoginModal } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!userTrackId || userTrackId === 'null' || userTrackId === 'undefined') {
          const res = await api.get(`/tracks/${trackId}/`);
          setTrackInfo(res.data);
        } else {
          const res = await api.get(`/user/tracks/${userTrackId}/`);
          setUserTrack(res.data);
          setTrackInfo(res.data.learning_track);
        }
      } catch (err) {
        setError('Something went wrong loading the track info.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [trackId, userTrackId]);

  const handleStartJourney = async () => {
  if (!isAuthenticated) {
    openLoginModal();
    return;
  }

  setBtnLoading(true);
  try {
    const res = await api.post('/user/tracks/', { learning_track: trackId });
    const newTrack = res.data;

    const taskRes = await api.post(`/user/tracks/${newTrack.id}/generate-task/`);
    const newTask = taskRes.data;

    navigate(`/tasks/${newTask.id}`);
  } catch (err) {
    setError('Failed to start a new journey.');
  } finally {
    setBtnLoading(false);
  }
};


  const generateTask = async () => {
    if (!isAuthenticated) {
      openLoginModal();
      return;
    }

    setBtnLoading(true);
    setError('');
    try {
      const res = await api.post(`/user/tracks/${userTrackId}/generate-task/`);
      const task = res.data;
      navigate(`/tasks/${task.id}`);
    } catch (err) {
      setError('Failed to generate task');

      if (err.response) {
    } else {
    }
    }finally {
      setBtnLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-blue0 dark:bg-gray-900">
        <p className="text-blue70 dark:text-cyan-200 font-semibold">Loading track details...</p>
      </div>
    );
  }

  const completedTasks = userTrack?.tasks?.filter(task => task.status === 'completed') || [];
  const noTasksDone = completedTasks.length === 0;

  return (
  <div className="min-h-screen w-full bg-blue0 dark:bg-blue90 text-black dark:text-white px-6 py-40 flex flex-col rounded-xl">
    <div className="w-full max-w-6xl mx-auto flex-grow rounded-xl">

      {!isAuthenticated ? (
        <div className="text-center py-20">
          <h1 className="text-4xl font-bold mb-6">Please log in to see your track</h1>
          <button
            onClick={openLoginModal}
            className="px-8 py-4 bg-blue70 text-white rounded-lg hover:bg-blue50 transition"
          >
            Log In / Sign Up
          </button>
        </div>
      ) : (

        <>
          <h1 className="text-5xl font-extrabold text-blue70 dark:text-cyan-300 mb-12 text-center">
            {trackInfo?.title || 'Your Track'}
          </h1>

          {!userTrackId || userTrackId === 'null' || userTrackId === 'undefined' || noTasksDone ? (
            <div className="text-center">
              <button
                onClick={handleStartJourney}
                disabled={btnLoading}
                className="px-8 py-4 text-lg font-bold rounded-lg bg-blue70 hover:bg-blue50 text-white dark:bg-cyan-900 dark:text-cyan-200 transition-all shadow-lg hover:shadow-2xl hover:scale-105 disabled:opacity-50"
              >
                {btnLoading ? 'Starting...' : 'Get in a new Journey!'}
              </button>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-center mb-12">
                <button
                  onClick={generateTask}
                  disabled={btnLoading}
                  className="px-10 py-4 text-lg font-bold rounded-lg bg-blue70 text-blue0 dark:bg-cyan-900 dark:text-cyan-100 hover:bg-blue50 border border-blue70 dark:border-none transition shadow-md hover:scale-[1.05] disabled:opacity-50"
                >
                  {btnLoading ? 'Generating...' : 'Continue Track'}
                </button>
              </div>

              <ul className="grid grid-cols-1 gap-3">
                {completedTasks.slice().reverse().map(task => (
                  <li key={task.id}>
                    <Link
                      to={`/tasks/${task.id}`}
                      className="block rounded-lg p-4 bg-gradient-to-b from-white to-blue0 dark:from-gray-800 dark:to-gray-900 border border-blue50 dark:border-gray-700 text-blue70 dark:text-cyan-200 shadow-md transition-transform hover:scale-[1.03]"
                    >
                      <div className="flex justify-between items-center mb-1">
                        <h3 className="text-base font-semibold truncate max-w-[80%]">
                          {task.task.includes('### Title:')
                            ? task.task.split('### Title:')[1].split('\n')[0].trim()
                            : 'Untitled Task'}
                        </h3>
                        <span className="text-sm font-semibold text-blue200 dark:text-cyan-300">
                          Grade: {task.grade != null ? `${task.grade} / 5` : '-'}
                        </span>
                      </div>
                      <p className="text-blue200 dark:text-cyan-300 text-xs">
                        Click to view solution & feedback
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            </>
          )}

          {error && (
            <p className="text-red-600 dark:text-red-400 text-center font-medium mt-8">{error}</p>
          )}
        </>
      )}
    </div>
  </div>
);
}
export default UserTrackDetail;

