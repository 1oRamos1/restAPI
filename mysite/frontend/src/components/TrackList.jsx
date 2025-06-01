import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link, useParams } from 'react-router-dom';

function TrackList() {
  const { categoryId } = useParams();
  const [tracks, setTracks] = useState([]);

  useEffect(() => {
    api.get(`categories/${categoryId}/tracks/`)
      .then(res => setTracks(res.data))
      .catch(err => console.error('Failed to fetch tracks:', err));
  }, [categoryId]);

  return (
    <div>
      <h1>Tracks in Category</h1>
      <ul>
        {tracks.map(track => (
          <li key={track.id}>
         <Link to={`/track/${track.user_learning_track_id}`}>
              {track.title || 'Unnamed Track'}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TrackList;