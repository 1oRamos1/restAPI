import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { Link, useParams } from 'react-router-dom';

function TrackList() {
  const { categoryId } = useParams();
  const [tracks, setTracks] = useState([]);

  useEffect(() => {
    api.get(`categories/${categoryId}/tracks/`)
      .then(res => setTracks(res.data))
      .catch(err => console.error(err));
  }, [categoryId]);

  return (
    <div>
      <h1>Tracks in Category</h1>
      <ul>
        {tracks.map(track => (
          <li key={track.id}>
            <Link to={`/track/${track.id}`}>{track.title || track.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TrackList;
