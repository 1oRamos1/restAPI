import React from 'react';
import TrackList from '../components/TrackList';

export default function CategoryPage() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-50 via-cyan-100 to-white">
      <main className="w-full">
        <TrackList />
      </main>
    </div>
  );
}
