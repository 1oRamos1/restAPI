import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link, useParams } from 'react-router-dom';

function TrackList() {
  const { categoryId } = useParams();
  const [tracks, setTracks] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');

  useEffect(() => {
    api.get(`categories/${categoryId}/tracks/`)
      .then(res => setTracks(res.data))
      .catch(err => console.error('Failed to fetch tracks:', err));
  }, [categoryId]);

  const filteredTracks = tracks.filter(track => {
    const matchesSearch = track.title.toLowerCase().includes(search.toLowerCase());
    const matchesLevel = selectedLevel ? track.level === selectedLevel : true;
    return matchesSearch && matchesLevel;
  });

  return (
    <div className="min-h-screen bg-blue0 dark:bg-blue90 font-kumbh text-gray-800 dark:text-gray-100 flex flex-col">
      {/* Section Header */}
      <section className="
        w-full bg-blue70/90 dark:bg-gray-900
        py-8 md:py-10 lg:py-12 xl:py-16
        px-4 md:px-6
        text-white text-center"
      >
        <h1 className="
          text-xl md:text-2xl lg:text-3xl xl:text-4xl
          font-kumbh font-bold tracking-tight
          text-blue0 dark:text-cyan-200 mb-3"
        >
          Choose Your Learning Track
        </h1>
        <p className="
          text-sm md:text-base lg:text-lg xl:text-xl
          text-blue-200 dark:text-cyan-300 max-w-lg mx-auto"
        >
          Dive into curated learning tracks and elevate your coding skills.
        </p>
      </section>

      {/* Filters */}
      <div className="max-w-4xl mx-auto px-4 md:px-6 pt-4 flex flex-col gap-3">
        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search tracks..."
          className="w-full px-3 py-2 rounded-md text-sm text-blue70 dark:text-cyan-100 placeholder-blue200 dark:placeholder-cyan-100 border border-gray-500 bg-blue0 dark:bg-gray-800 focus:outline-none focus:ring-1 focus:ring-cyan-400"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        {/* Level Selector */}
        <div className="overflow-x-auto whitespace-nowrap space-x-2 flex scrollbar-hide">
          {['', 'beginner', 'advanced', 'master'].map(level => (
            <button
              key={level}
              onClick={() => setSelectedLevel(level)}
              className={`px-3 py-1 rounded-full border text-xs font-medium transition-all duration-200 ${
                selectedLevel === level
                  ? 'bg-blue70 text-white dark:bg-cyan-600 dark:text-white'
                  : 'bg-white dark:bg-gray-800 text-blue70 dark:text-cyan-200'
              }`}
            >
              {level === '' ? 'All' : level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Tracks Grid */}
      <section className="max-w-4xl mx-auto w-full px-4 py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 md:gap-6 lg:gap-8 justify-items-center">
          {filteredTracks.map((track) => (
            <Link
              key={track.id}
              to={`/track/${track.id}/${track.user_learning_track_id}`}
              className="
                bg-blue70/90 dark:bg-gray-900
                hover:bg-blue90 dark:hover:bg-cyan-700
                transform hover:scale-105
                transition-all duration-200
                shadow-xl rounded-xl p-4 pt-6
                text-white dark:text-cyan-200
                flex flex-col justify-between
                border border-blue10 dark:border-gray-700
                w-full sm:w-80 md:w-72 lg:w-80 xl:w-80
                h-32 md:h-36 lg:h-40 xl:h-44
              "
            >
              <div className="flex flex-col justify-between h-full">
                <h3 className="text-base md:text-lg lg:text-xl xl:text-xl font-bold text-center">
                  {track.title}
                </h3>
                <p className="text-xs md:text-sm lg:text-base xl:text-base text-blue-200 dark:text-cyan-300 text-center">
                  Level: {track.level}
                </p>
              </div>
            </Link>
          ))}
          {filteredTracks.length === 0 && (
            <p className="text-center col-span-full text-gray-400">
              No tracks found.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}

export default TrackList;

