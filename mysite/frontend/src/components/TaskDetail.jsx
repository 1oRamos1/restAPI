import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Editor from '@monaco-editor/react';

function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const isSubmitAgain = location.pathname.endsWith('/submit-again');

  const [task, setTask] = useState(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [editorLang, setEditorLang] = useState('plaintext');
  const [editorValue, setEditorValue] = useState('');
  const [taskCode, setTaskCode] = useState('');
  const [review, setReview] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [nextTaskLoading, setNextTaskLoading] = useState(false);
  const [error, setError] = useState('');

  const [isDarkMode, setIsDarkMode] = useState(false);
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDarkMode(mediaQuery.matches);
    const handler = (e) => setIsDarkMode(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  useEffect(() => {
    api
      .get(`user/tasks/${taskId}/`)
      .then(res => {
        const taskData = res.data;
        setTask(taskData);
        setTitle(taskData.title || 'Task');
        setDescription(taskData.description || '');
        setEditorLang(taskData.language || 'plaintext');
        setTaskCode(taskData.task_code || '');

        if (isSubmitAgain) {
          setReview('');
          setEditorValue(taskData.task_code || '');
        } else {
          setReview(taskData.review || '');
          setEditorValue(taskData.solution || taskData.task_code || '');
        }

        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load task.');
        setLoading(false);
      });
  }, [taskId, isSubmitAgain]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.put(`user/tasks/${taskId}/`, { solution: editorValue });
      setReview(res.data.review);
    } catch {
      alert('Failed to submit solution.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextTask = async () => {
    setNextTaskLoading(true);
    try {
      const res = await api.post(`/user/tracks/${task.user_learning_track_id}/generate-task/`);
      const newTask = res.data;
      navigate(`/tasks/${newTask.id}`);
    } catch (err) {
      alert('Failed to generate next task.');
    } finally {
      setNextTaskLoading(false);
    }
  };

  const gradeMatch = review.match(/Grade:\s*([0-5]\/5)/i);
  const extractedGrade = gradeMatch ? gradeMatch[1] : '';
  const reviewBody = gradeMatch ? review.replace(gradeMatch[0], '').trim() : review;

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center bg-blue0">
        <p className="text-blue70 font-semibold">Loading task...</p>
      </div>
    );

  if (error)
    return (
      <div className="min-h-screen flex items-center justify-center bg-blue0">
        <p className="text-red-600 font-semibold">{error}</p>
      </div>
    );

  return (
    <div className="min-h-screen w-full bg-blue0 dark:bg-blue90 text-black dark:text-white px-6 py-40 flex flex-col rounded-xl">
      <div className="w-full max-w-6xl mx-auto flex-grow rounded-xl">
        <h2 className="text-2xl font-semibold pb-5 text-blue70 dark:text-cyan-300">
          {task.learning_track_name || 'Track Title'} - {task.learning_track_level || 'Level'}
        </h2>

        <h2 className="text-5xl font-extrabold mb-8 text-blue70 dark:text-cyan-300">
          Task {task.task_number}: {title}
        </h2>
        <p className="mb-10 whitespace-pre-line text-blue80 dark:text-cyan-200">{description}</p>

        {submitting ? (
          <div className="text-blue80 font-semibold mb-8">Submitting solution and waiting for review...</div>
        ) : !review ? (
          <form onSubmit={handleSubmit} className="flex flex-col">
            <div className="h-[400px] mb-8 border border-blue80 rounded-md overflow-hidden shadow-sm bg-blue0 dark:bg-gray-900">
              <Editor
                height="100%"
                language={editorLang}
                value={editorValue}
                onChange={(value) => setEditorValue(value || '')}
                theme={isDarkMode ? 'vs-dark' : 'vs-light'}
                options={{
                  fontSize: 14,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                  wordWrap: 'on',
                  lineNumbers: 'on',
                  smoothScrolling: true,
                }}
              />
            </div>
            <button
              type="submit"
              className="bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-8 py-4 rounded-lg font-bold transition shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={submitting}
            >
              Submit Solution
            </button>
          </form>
        ) : (
          <>
            <div className="mt-6 p-6 bg-white dark:bg-gray-900 rounded-lg border border-blue80 dark:border-gray-700 shadow-md">
              <h3 className="font-bold mb-4 text-blue90 dark:text-cyan-300 text-xl">Review:</h3>
              <p className="whitespace-pre-line text-blue90 dark:text-cyan-200">{reviewBody}</p>
              {extractedGrade && (
                <p className="mt-6 text-lg text-blue50 dark:text-cyan-100 font-semibold">
                  Grade: <span className="font-bold">{extractedGrade}</span>
                </p>
              )}
            </div>

            <div className="mt-10 flex flex-wrap gap-4">
              <button
                className="bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md disabled:opacity-50"
                onClick={handleNextTask}
                disabled={nextTaskLoading}
              >
                {nextTaskLoading ? 'Loading Next Task...' : 'Next Task'}
              </button>

              <button
                className="bg-blue70 hover:bg-blue50 dark:bg-cyan-800 dark:text-cyan-100 dark:hover:bg-cyan-500 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md disabled:opacity-50"
                onClick={() => navigate(`/tasks/${task.id}/submit-again`)}
              >
                Submit Again
              </button>

              <button
                className="bg-blue90 hover:bg-gray-500 dark:bg-gray-800 dark:text-cyan-100 dark:hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition shadow-md"
                onClick={() => navigate('/')}
              >
                Exit
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default TaskDetail;
