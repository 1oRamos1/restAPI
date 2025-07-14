import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link } from 'react-router-dom';

function UserTracksList() {
  const [tracks, setTracks] = useState([]);
  const [filteredTracks, setFilteredTracks] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [summaryModalOpen, setSummaryModalOpen] = useState(false);
  const [currentSummary, setCurrentSummary] = useState('');

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

  if (loading) return <div className="p-6 text-center text-blue70 dark:text-cyan-200 font-semibold">Loading your tracks...</div>;
  if (error) return <div className="p-6 text-center text-red-600 dark:text-red-400 font-semibold">{error}</div>;
  if (!tracks.length) return <div className="p-6 text-center text-blue70 dark:text-cyan-200 font-semibold">You haven't started any tracks yet.</div>;

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
                         p-6 text-white dark:text-cyan-200 flex flex-col h-full border border-blue10 dark:border-gray-700"
            >
              <Link
                to={`/track/${track.learning_track.id}/${track.id}`}
                className="flex flex-col justify-start h-full pb-8"
              >
                <h3 className="text-2xl font-kumbh font-semibold truncate mb-2 group-hover:text-white dark:group-hover:text-cyan-100">
                  {track.learning_track.title}
                </h3>
                <p className="text-sm text-blue-100 dark:text-cyan-300 mb-1">
                  Last Updated: {new Date(track.last_updated).toLocaleDateString()}
                </p>
                <p className="text-sm text-blue-100 dark:text-cyan-300">
                  Tasks Done: {track.tasks?.length ?? 0}
                </p>
              </Link>

              {/* Track Summary Button */}
              <button
                onClick={(e) => {
                  e.preventDefault(); // prevent Link navigation
                  openSummaryModal(track.summary);
                }}
                className="mt-2 text-xs bg-cyan-600 text-blue0 dark:bg-cyan-600 dark:text-blue0
                  px-3 py-1 rounded-lg font-semibold shadow-md hover:bg-cyan-500 dark:hover:bg-cyan-700
                  transition"
                style={{ position: 'absolute', bottom: '15px', left: '24px' }}
              >
                Track Summary
              </button>

              <span
                className={`absolute bottom-4 right-4 px-3 py-1 text-[11px] font-semibold rounded-full ${
                  track.tasks?.length
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200'
                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                }`}
              >
                {track.tasks?.length ? 'In Progress' : 'New'}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
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
    </div>
  );
}

export default UserTracksList;

