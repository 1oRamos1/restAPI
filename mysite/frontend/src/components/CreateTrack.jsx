import React, { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { AuthContext } from '../context/AuthContext';

export default function CreateTrack() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useContext(AuthContext);

  const [step, setStep] = useState(1);
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState('auto'); // default 'auto'
  const [level, setLevel] = useState('beginner');

  const [options, setOptions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user && user.is_pro === false) {
      navigate('/');
    }
  }, [user, navigate]);

  if (user === undefined) return null;

  const validateInput = (text) => {
    const cleaned = text.trim().toLowerCase();
    const wordCount = cleaned.split(/\s+/).length;
    if (cleaned.length < 10 || cleaned.length > 300) return false;
    if (wordCount < 3 || wordCount > 15) return false;
    if (!/^[a-zA-Z0-9.,?!'"()[\]{}<>/@#%^&*+=_\-\s\\]+$/.test(cleaned)) return false;

    const banned = ['asdf', 'qwerty', 'test', 'lorem', 'fuck', 'shit'];
    if (banned.some((word) => cleaned.includes(word))) return false;
    if (new Set(cleaned).size < 5) return false;

    return true;
  };

  const sanitizeLanguage = (lang) => {
    const allowed = ['python', 'js', 'cpp'];
    return allowed.includes(lang) ? lang : 'python'; // default to python if invalid
  };

  const handleSearchOptions = async () => {
    setError('');
    if (!validateInput(description)) {
      setError('Please enter a meaningful description (3–15 words, no nonsense).');
      return;
    }

    try {
      setLoading(true);
      const payload = {
        description,
        level,
        language,
      };
      const res = await api.post('/custom-track/options/', payload);
      if (res.data.options && res.data.options.length > 0) {
        setOptions(res.data.options);
        setStep(2);
      } else {
        setError('No options returned. Try different input.');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to fetch options.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTrack = async (selectedOption) => {
    if (!selectedOption) return;

    setError('');
    setLoading(true);

    try {
      const resolvedLanguage =
        language === 'auto'
          ? sanitizeLanguage(selectedOption.language)
          : sanitizeLanguage(language);

      const payload = {
        description,
        language: resolvedLanguage,
        level,
      };

      const response = await api.post('/custom-track/create/', payload);
      const { track_id, user_track_id } = response.data;

      navigate(`/track/${track_id}/${user_track_id}`);
    } catch (error) {
      console.error('Full error response:', error.response?.data);
      setError(error.response?.data?.detail || 'Failed to create track. Are you Pro?');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshOptions = async () => {
    setError('');
    setLoading(true);
    try {
      const payload = {
        description,
        level,
        language,
      };
      const res = await api.post('/custom-track/options/', payload);
      if (res.data.options && res.data.options.length > 0) {
        setOptions(res.data.options);
      } else {
        setError('No options returned. Try different input.');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to fetch options.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-blue0 dark:bg-blue90 text-black dark:text-white px-6 py-40 flex flex-col rounded-xl">
      <div className="w-full max-w-6xl mx-auto flex-grow rounded-xl">

        {step === 1 && (
          <>
            <h1 className="text-5xl font-extrabold text-blue70 dark:text-cyan-300 mb-12 text-center">
                Create Your Own Learning Track
            </h1>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={8}
              className="w-3/4 mx-auto p-3 border dark:border-gray-700 rounded shadow-sm dark:bg-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 block"
              placeholder='Describe what you want to learn. For example: "I want to learn algorithms using C++"'
            />

            <div className="w-3/4 mx-auto mt-6 flex gap-4">
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="flex-1 p-3 rounded border dark:border-gray-700 dark:bg-gray-900"
              >
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="js">JavaScript</option>
                <option value="auto">Never mind</option>
              </select>

              <select
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="flex-1 p-3 rounded border dark:border-gray-700 dark:bg-gray-900"
              >
                <option value="beginner">Beginner</option>
                <option value="advanced">Advanced</option>
                <option value="master">Master</option>
              </select>
            </div>

            {error && (
              <p className="text-red-600 text-sm mt-2 w-3/4 mx-auto">{error}</p>
            )}

            <div className="mt-6">
              <button
                onClick={handleSearchOptions}
                disabled={loading}
                className="w-3/4 mx-auto p-3 border bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md disabled:opacity-50 block"
              >
                {loading ? 'Searching...' : 'Search Tracks'}
              </button>
            </div>

            {loading }
          </>
        )}

        {step === 2 && (
          <>
             <div className="w-3/4 mx-auto space-y-5">
    <h2 className="text-5xl font-extrabold text-blue70 dark:text-cyan-300 mb-12 text-center">
      Choose your Track
    </h2>
    {options.map((opt, idx) => (
      <div
        key={idx}
        className="p-3 border-2 border-blue70 dark:border-cyan-700 rounded-xl cursor-pointer
                   bg-white dark:bg-gray-900 hover:bg-blue0 dark:hover:bg-cyan-700
                   hover:shadow-xl transform transition-all duration-200
                   hover:scale-105 hover:ring-blue40 dark:hover:ring-cyan-500"
       onClick={() => handleCreateTrack(opt)}
      >
        <h3 className="text-xl text-blue70 dark:text-cyan-300 font-semibold">{opt.title}</h3>
        <p className="text-md text-blue80 dark:text-cyan-500 mt-1 pb-2">{opt.short_description}</p>
        <p className="text-sm italic text-gray-600 dark:text-gray-300">
          {opt.level} • {opt.language}
        </p>
      </div>
    ))}
  </div>

            {error && (
              <p className="text-red-600 text-sm mt-4 w-3/4 mx-auto">{error}</p>
            )}

            <div className="w-3/4 mx-auto mt-6 text-center">
              <button
                onClick={handleRefreshOptions}
                disabled={loading}
                className="p-3 border bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : 'Generate New Options'}
              </button>
            </div>

            {loading && (
              <p className="text-center mt-4 text-sm text-blue-500">
                Loading...
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
