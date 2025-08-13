import React from 'react';
import CreateTrack from '../components/CreateTrack';

export default function CreateTrackPage() {
  return (
    <div className="min-h-screen bg-blue70/90 dark:bg-gray-900 flex justify-center pt-16">
      <div className="w-full max-w-5xl mx-6 md:mx-0">
        <div className="bg-white dark:bg-gray-900 shadow-2xl p-10 rounded-none text-black dark:text-white">
          <CreateTrack />
        </div>
      </div>
    </div>
  );
}

