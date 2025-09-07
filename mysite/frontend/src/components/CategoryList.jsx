import React, { useState, useEffect } from 'react';
import { Link, useLocation, useSearchParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';

function CategoryList({ language: initialLanguage = '', size = 'large', limit }) {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();

  const languageFromURL = searchParams.get('language') || initialLanguage;
  const [language, setLanguage] = useState(languageFromURL);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    api
      .get('categories/', { params: language ? { language } : {} })
      .then((res) => {
        const limited = limit ? res.data.slice(0, limit) : res.data;
        setCategories(limited);
      })
      .catch((err) => console.error('API error:', err));
  }, [language, limit]);

  const cardSizeClasses =
    size === 'small'
      ? 'w-full sm:w-64 md:w-48 lg:w-44 h-24 md:h-28 lg:h-32 text-base md:text-lg'
      : 'w-full sm:w-80 md:w-72 lg:w-80 h-32 md:h-36 text-xl md:text-2xl';

  const showDropdown = location.pathname !== '/'; // don't show on homepage

  return (
    <div className="w-full font-kumbh">
      {showDropdown && (
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <select
            value={language}
            onChange={(e) => {
              const selected = e.target.value;
              setLanguage(selected);
              if (selected) {
                navigate(`/categories?language=${selected}`);
              } else {
                navigate('/categories');
              }
            }}
            className="w-full md:w-72 px-4 py-2 rounded-md text-sm text-gray-400 dark:text-cyan-700
                       bg-blue0 dark:bg-gray-800 border border-gray-500
                       focus:outline-none focus:ring-2 focus:ring-cyan-400"
          >
            <option value="">All</option>
            <option value="python">Python</option>
            <option value="js">JavaScript</option>
            <option value="c++">C++</option>
          </select>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8 justify-items-center">
        {Array.isArray(categories) && categories.length > 0 ? (
          categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/category/${cat.id}`}
              className={`relative bg-blue70/90 dark:bg-gray-900 hover:bg-blue90 dark:hover:bg-cyan-700
                transform hover:scale-105 transition-all duration-300 shadow-xl rounded-xl
                p-4 pt-6 text-white dark:text-cyan-200 flex flex-col justify-between
                border border-blue10 dark:border-gray-700 ${cardSizeClasses}`}
            >
              <h3 className="font-bold text-center mb-2">{cat.name}</h3>
              <div
                className={`absolute bottom-0 left-0 right-0
                  text-xs md:text-sm text-blue5 bg-black/40 dark:bg-white/10
                  text-center pointer-events-none backdrop-blur-sm
                  rounded-b-xl
                  ${showDropdown ? 'py-3' : 'py-1'}`}
              >
                <span className="font-semibold capitalize">{cat.language}</span>
              </div>
            </Link>
          ))
        ) : (
          <p className="text-center col-span-full text-gray-400">
            No categories found.
          </p>
        )}
      </div>
    </div>
  );
}

export default CategoryList;
