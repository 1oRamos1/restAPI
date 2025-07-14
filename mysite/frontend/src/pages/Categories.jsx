import React from 'react';
import CategoryList from '../components/CategoryList';

export default function Categories() {
  return (
    <div className="min-h-screen bg-blue0 dark:bg-blue90 text-blue70 dark:text-cyan-200 px-15 pt-40 pb-24">
      <div className="max-w-7xl mx-auto font-kumbh">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <CategoryList />
      </div>
    </div>
    </div>
  );
}
