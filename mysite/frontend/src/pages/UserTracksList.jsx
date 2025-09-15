import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import { TrashIcon } from '@heroicons/react/24/outline';

function UserTracksList() {
  const [tracks, setTracks] = useState([]);
  const [filteredTracks, setFilteredTracks] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);
  const [currentSummary, setCurrentSummary] = useState('');

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [trackToDelete, setTrackToDelete] = useState(null);

  useEffect(() => {
    const fetchUserTracks = async () => {
      try {
        const res = await api.get('/user/tracks/');
        const sorted = res.data.sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated));
        setTracks(sorted);
        setFilteredTracks(sorted);
      } catch (err) {
        console.error(err);
        setError('Failed to load your tracks.');
      } finally {
        setLoading(false);
      }
    };
    fetchUserTracks();
  }, []);

  useEffect(() => {
    const filtered = tracks.filter(track =>
      track.learning_track.title.toLowerCase().includes(search.toLowerCase())
    );
    setFilteredTracks(filtered);
  }, [search, tracks]);

  const openSummaryModal = (summary) => {
    setCurrentSummary(summary || 'No summary available.');
    setSummaryModalOpen(true);
  };

  const closeSummaryModal = () => {
    setSummaryModalOpen(false);
    setCurrentSummary('');
  };

  const openDeleteModal = (trackId) => {
    setTrackToDelete(trackId);
    setDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setTrackToDelete(null);
    setDeleteModalOpen(false);
  };

  const handleDelete = async () => {
    if (!trackToDelete) return;
    try {
      await api.delete(`/user/tracks/`, { data: { user_learning_track_id: trackToDelete } });
      setTracks(prev => prev.filter(t => t.id !== trackToDelete));
      setFilteredTracks(prev => prev.filter(t => t.id !== trackToDelete));
    } catch (err) {
      console.error(err);
      alert('Failed to delete track.');
    } finally {
      closeDeleteModal();
    }
  };

  if (loading) return <div className="p-6 text-center text-blue70 dark:text-cyan-200 font-semibold">Loading your tracks...</div>;
  if (error) return <div className="p-6 text-center text-red-600 dark:text-red-400 font-semibold">{error}</div>;
  if (!tracks.length) {
    return (
      <div className="min-h-screen bg-blue0 dark:bg-blue90 text-blue70 dark:text-cyan-200 px-6 py-40 flex flex-col items-center justify-center">
        <h2 className="text-2xl font-bold mb-6 text-center">You haven't started any tracks yet.</h2>
        <Link
          to="/categories"
          className="px-8 py-4 text-lg font-bold rounded-lg
                     bg-blue70 hover:bg-blue50 text-white
                     dark:bg-cyan-900 dark:text-cyan-200
                     transition-all duration-300 ease-in-out
                     shadow-lg hover:shadow-2xl hover:scale-105"
        >
          Start Your Journey
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-blue0 dark:bg-blue90 text-blue70 dark:text-cyan-200 px-15 pt-40 pb-24">
      <div className="max-w-7xl mx-auto font-kumbh">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <input
            type="text"
            placeholder="Search tracks..."
            className="w-full md:w-72 px-4 py-2 rounded-md text-sm text-blue70 dark:text-cyan-100 placeholder-blue200 dark:placeholder-cyan-100 border border-gray-500 bg-blue0 dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-cyan-400"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredTracks.map(track => (
            <div
              key={track.id}
              className="relative bg-blue70/90 dark:bg-gray-900 hover:bg-blue90 dark:hover:bg-cyan-700
                         transform hover:scale-105 transition-all duration-300 shadow-xl rounded-xl
                         p-5 text-white dark:text-cyan-200 flex flex-col h-full border border-blue10 dark:border-gray-700"
            >
              <div className="flex justify-end mb-2">
                <button
                  onClick={() => openDeleteModal(track.id)}
                  title="Delete Track"
                  className="text-red-500 hover:text-red-700 transition"
                >
                 <TrashIcon className="h-5 w-5 dark:bg-transparent text-blue0 hover:white dark:bg-gray-900 dark:hover:bg-cyan-700" />
                </button>
              </div>

              <Link
                to={`/track/${track.learning_track.id}/${track.id}`}
                className="flex flex-col justify-start h-full"
              >
                <h3 className="text-2xl font-kumbh font-semibold truncate mb-2 group-hover:text-white dark:group-hover:text-cyan-100">
                  {track.learning_track.title}
                </h3>
                <p className="text-md text-blue-100 dark:text-cyan-300">
                  Tasks Done: {track.tasks?.length ?? 0}
                </p>
                <p className="text-md text-blue-100 dark:text-cyan-300">
                  Language: {track.learning_track.category.language || 'Unknown'}
                </p>
                <p className="text-sm text-blue-100 dark:text-cyan-300 mt-2">
                  {track.learning_track.level || 'Unknown'}
                </p>
              </Link>

              <div className="flex justify-between items-center text-xs text-blue-100 dark:text-cyan-300 mt-auto pt-2">
                <span>
                  Last Updated: {new Date(track.last_updated).toLocaleDateString()}
                </span>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    openSummaryModal(track.summary);
                  }}
                  className="bg-blue70/90 text-blue0 dark:bg-cyan-600 dark:text-blue0
                             border-2 border-blue5 dark:border-2 dark:border-blue5
                             px-4 py-2 rounded-md font-semibold
                             hover:bg-cyan-800 dark:hover:bg-cyan-700
                             hover:scale-105 hover:shadow-xl
                             transition transform duration-200"
                >
                  Track Summary
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Track Summary Modal */}
        {summaryModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 max-w-lg w-full shadow-lg">
              <h3 className="text-xl font-bold mb-4 text-blue90 dark:text-cyan-300">Track Summary</h3>
              <p className="whitespace-pre-line text-blue90 dark:text-cyan-200 mb-6">{currentSummary}</p>
              <button
                onClick={closeSummaryModal}
                className="bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-2 rounded-lg font-semibold transition shadow-md"
              >
                Close
              </button>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-6 max-w-md w-full shadow-lg text-center">
              <h3 className="text-xl font-bold mb-4 text-blue90 dark:text-cyan-300">Confirm Deletion</h3>
              <p className="mb-6 text-blue90 dark:text-cyan-200">
                Are you sure you want to delete this track? This action cannot be undone.
              </p>
              <div className="flex justify-center gap-4">
                <button
                  onClick={handleDelete}
                  className="bg-red-500 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-semibold transition shadow-md"
                >
                  Delete
                </button>
                <button
                  onClick={closeDeleteModal}
                  className="bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-2 rounded-lg font-semibold transition shadow-md"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserTracksList;

