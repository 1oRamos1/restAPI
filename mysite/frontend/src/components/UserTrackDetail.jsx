import React, { useEffect, useState, useContext } from 'react';
import api from '../api/axios';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const LEVELS = [
  { key: 'explorer', label: 'Explorer', color: 'bg-blue-500', textColor: 'text-blue-600 dark:text-blue-400', emoji: '🥉' },
  { key: 'builder',  label: 'Builder',  color: 'bg-purple-500', textColor: 'text-purple-600 dark:text-purple-400', emoji: '🥈' },
  { key: 'master',   label: 'Master',   color: 'bg-yellow-500', textColor: 'text-yellow-600 dark:text-yellow-400', emoji: '🥇' },
];

function Fireworks() {
  const items = [
    { emoji: '✨', left: '80%', top: '5%', delay: '0.2s' },
    { emoji: '🌟', left: '20%', top: '60%', delay: '0.1s' },
    { emoji: '🎉', left: '75%', top: '55%', delay: '0.3s' },
    { emoji: '✨', left: '90%', top: '30%', delay: '0.5s' },
    { emoji: '🌟', left: '5%', top: '40%', delay: '0.6s' },
    { emoji: '🎉', left: '50%', top: '65%', delay: '0.4s' },
    { emoji: '✨', left: '30%', top: '20%', delay: '0.7s' },
    { emoji: '🌟', left: '60%', top: '10%', delay: '0.8s' },
    { emoji: '🎉', left: '10%', top: '50%', delay: '0.9s' },
  ];
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden z-0">
      {items.map((item, i) => (
        <div
          key={i}
          className="absolute text-xl animate-bounce"
          style={{ left: item.left, top: item.top, animationDelay: item.delay, animationDuration: '1s' }}
        >
          {item.emoji}
        </div>
      ))}
    </div>
  );
}

function CompletionPopup({ userTrackId, onClose, onRestart }) {
  const navigate = useNavigate();
  const [restarting, setRestarting] = useState(false);

  const handleRestart = async () => {
    setRestarting(true);
    try {
      await api.post(`/user/tracks/${userTrackId}/restart/`);
      onRestart();
      onClose();
    } catch {
      alert('Failed to restart track.');
    } finally {
      setRestarting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center px-4">
      <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md p-8 text-center overflow-hidden">
        <Fireworks />
        <div className="relative z-10">
        <button
          onClick={onClose}
          className="absolute top-3 right-4 text-2xl text-gray-400 hover:text-gray-600"
        >×</button>

        <div className="text-5xl mb-4">🥇</div>
        <h2 className="text-3xl font-extrabold text-yellow-500 mb-2">Congratulations!</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          You've completed all 15 tasks and reached <strong>Master</strong> level!
          Ready for your next challenge?
        </p>

        <div className="flex flex-col gap-3">
          <button
            onClick={handleRestart}
            disabled={restarting}
            className="w-full py-3 rounded-lg bg-yellow-500 hover:bg-yellow-400 text-white font-bold transition shadow-md disabled:opacity-50"
          >
            {restarting ? 'Restarting...' : '🔄 Restart This Track (Master Mode)'}
          </button>

          <button
            onClick={() => navigate('/courses')}
            className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold transition shadow-md"
          >
            🚀 Start New Journey
          </button>
        </div>
        </div>
      </div>
    </div>
  );
}

function ProgressBar({ currentLevel, progressScore }) {
  const currentIdx = LEVELS.findIndex(l => l.key === currentLevel);
  const safeIdx = currentIdx === -1 ? 0 : currentIdx;
  const level = LEVELS[safeIdx];
  const isMaster = safeIdx === LEVELS.length - 1;
  const fillPercent = isMaster && progressScore >= 15 ? 100 : Math.min((progressScore / 15) * 100, 100);

  return (
    <div className="w-full max-w-2xl mx-auto mb-12">
      {/* Level labels */}
      <div className="flex justify-between mb-3">
        {LEVELS.map((l, idx) => (
          <div key={l.key} className="flex flex-col items-center gap-1" style={{ width: '33%' }}>
            <span className="text-lg">{l.emoji}</span>
            <span className={`text-xs font-bold ${idx === safeIdx ? l.textColor : 'text-gray-400 dark:text-gray-600'}`}>
              {l.label}
            </span>
          </div>
        ))}
      </div>

      {/* Progress track */}
      <div className="relative h-4 bg-gray-200 dark:bg-cyan-950 rounded-full overflow-hidden shadow-inner">
        {/* Level segment dividers */}
        <div className="absolute inset-0 flex pointer-events-none">
          <div className="w-1/3 border-r-2 border-white dark:border-gray-800 opacity-50" />
          <div className="w-1/3 border-r-2 border-white dark:border-gray-800 opacity-50" />
          <div className="w-1/3" />
        </div>

        {/* Completed levels fill */}
        {safeIdx > 0 && (
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 via-purple-500 to-purple-500 opacity-40"
            style={{ width: `${(safeIdx / 3) * 100}%` }}
          />
        )}

        {/* Current level fill */}
        <div
          className={`absolute top-0 h-full transition-all duration-700 ease-out rounded-full ${level.color}`}
          style={{
            left: `${(safeIdx / 3) * 100}%`,
            width: `${(fillPercent / 100) * (100 / 3)}%`,
          }}
        />
      </div>

      {/* Score label */}
      <div className="flex justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
        <span>{isMaster && progressScore >= 15 ? '🎉 Max Level!' : `${progressScore}/15 tasks`}</span>
        <span className={`font-semibold ${level.textColor}`}>{level.label} {level.emoji}</span>
      </div>
    </div>
  );
}

function UserTrackDetail() {
  const { trackId, userTrackId } = useParams();
  const [userTrack, setUserTrack] = useState(null);
  const [trackInfo, setTrackInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [btnLoading, setBtnLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCompletion, setShowCompletion] = useState(false);
  const { isAuthenticated, openLoginModal } = useContext(AuthContext);
  const navigate = useNavigate();

  const isCompleted = userTrack?.current_level === 'master' && userTrack?.progress_score >= 15;

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
          // Show popup if completed
          if (res.data.current_level === 'master' && res.data.progress_score >= 15) {
            setShowCompletion(true);
          }
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
    } finally {
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

        {showCompletion && (
          <CompletionPopup
            userTrackId={userTrackId}
            onClose={() => setShowCompletion(false)}
            onRestart={() => {
              setUserTrack(prev => ({ ...prev, current_level: 'master', progress_score: 0 }));
            }}
          />
        )}

        {!isAuthenticated ? (
          <div className="text-center py-20">
            <h1 className="text-md mb-6">Please log in to see your track</h1>
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

            {/* Progress Bar — only when user has a track */}
            {userTrack && (
              <ProgressBar
                currentLevel={userTrack.current_level || 'explorer'}
                progressScore={userTrack.progress_score || 0}
              />
            )}

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
                    onClick={isCompleted ? () => setShowCompletion(true) : generateTask}
                    disabled={btnLoading}
                    className={`px-10 py-4 text-lg font-bold rounded-lg border transition shadow-md hover:scale-[1.05] disabled:opacity-50 ${
                      isCompleted
                        ? 'bg-yellow-500 text-white border-yellow-500 cursor-pointer hover:bg-yellow-400'
                        : 'bg-blue70 text-blue0 dark:bg-cyan-900 dark:text-cyan-100 hover:bg-blue50 border-blue70 dark:border-none'
                    }`}
                  >
                    {isCompleted ? '🥇 View Completion' : btnLoading ? 'Generating...' : 'Continue Track'}
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
                            {task.title || 'Untitled Task'}
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