import React, { useContext } from 'react';
import CategoryList from '../components/CategoryList';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const { user } = useContext(AuthContext);

  return (
    <div className="flex flex-col min-h-screen w-full font-kumbh text-gray-800 bg-gradient-to-br dark:bg-gray-900">
      <main className="flex-grow">

        {/* Section 1: Header */}
        <header className="w-full flex flex-row min-h-[750px] overflow-hidden">
          <div className="flex-[2.5] bg-[#155e94] text-white dark:bg-blue80 dark:text-cyan-200 px-16 py-24 flex flex-col justify-center z-10">
            <h1 className="mb-6 text-5xl md:text-[5rem] font-extrabold leading-tight text-blue0 dark:text-cyan-200">
              Hello {user ? user.username : 'Guest'}!
            </h1>
            <p className="text-xl md:text-2xl font-extrabold max-w-md text-blue-200 dark:text-cyan-200">
              Ready to grow your skills? Our learning paths guide you every step of the way—whether you’re just starting out or leveling up.
            </p>
          </div>
          <div className="flex-[1.5] relative bg-blue0 dark:bg-gray-800">
            <img
              src="/ezgif.com-gif-maker.gif"
              alt="Robot Guide"
              className="absolute right-0 top-1/2 -translate-y-1/2 w-80 h-60 md:w-96 md:h-96 object-contain pointer-events-none"
              style={{ userSelect: 'none' }}
            />
          </div>
        </header>

        {/* Section 2: Greeting Banner */}
        <section className="w-full bg-blue80 dark:bg-blue100 py-60 px-6 text-white dark:text-cyan-200">
          <div className="max-w-6xl mx-auto text-center">
            <h2 className="text-6xl font-extrabold tracking-tight mb-6 text-blue0 dark:text-cyan-200">
              Welcome to CodeTracks
            </h2>
            <p className="text-xl text-blue-200 dark:text-cyan-200 max-w-3xl mx-auto leading-relaxed">
              Unlock your potential with expertly curated learning paths that guide you through real-world coding challenges.
              Track your progress, sharpen your skills, and build projects that matter — all in one seamless platform.
            </p>
          </div>
        </section>

        {/* Section 3: Python */}
        <section className="w-full bg-white dark:bg-gray-900">
          <div className="flex min-h-[600px] flex-row">
            <div className="flex-1 bg-blue0 dark:bg-gray-900 px-20 py-16 flex flex-col justify-center">
              <CategoryList language="python" size="small"/>
              <div className="mt-8">
                <Link
                  to={`/categories?language=python`}
                  className="text-sm font-semibold text-gray-400 dark:text-cyan-400 hover:underline"
                >
                  See All →
                </Link>
              </div>
            </div>
            <div className="flex-1 bg-blue70/90 dark:bg-blue90 px-20 py-16 text-white dark:text-cyan-200 flex flex-col justify-center">
              <h3 className="text-5xl font-extrabold mb-6">Python</h3>
              <p className="text-lg text-blue-100 dark:text-cyan-200 leading-relaxed">
                Dive into beginner‑friendly and advanced Python tracks covering fundamentals, OOP, data
                structures and automation projects.
              </p>
            </div>
          </div>
        </section>

        {/* Section 4: JavaScript */}
        <section className="w-full bg-white dark:bg-gray-900">
          <div className="flex min-h-[600px] flex-row">
            <div className="flex-1 bg-blue70/90 dark:bg-blue90 px-20 py-16 text-white dark:text-cyan-200 flex flex-col justify-center">
              <h3 className="text-5xl font-extrabold mb-6">JavaScript</h3>
              <p className="text-lg text-blue-100 dark:text-cyan-200 leading-relaxed">
                Master DOM manipulation, ES6+ syntax and modern frameworks to build responsive, interactive
                web applications.
              </p>
            </div>
            <div className="flex-1 bg-blue0 dark:bg-gray-900 px-20 py-16 flex flex-col justify-center">
              <CategoryList language="js" size="small"/>
              <div className="mt-8">
                <Link
                  to={`/categories?language=js`}
                  className="text-sm font-semibold text-gray-400 dark:text-cyan-400 hover:underline"
                >
                  See All →
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Section 5: C++ */}
        <section className="w-full bg-white dark:bg-gray-900">
          <div className="flex min-h-[600px] flex-row">
            <div className="flex-1 bg-blue0 dark:bg-gray-900 px-20 py-16 flex flex-col justify-center">
              <CategoryList language="c++" size="small" />
              <div className="mt-8">
                <Link
                  to={`/categories?language=${encodeURIComponent('c++')}`}
                  className="text-sm font-semibold text-gray-400 dark:text-cyan-400 hover:underline"
                >
                  See All →
                </Link>
              </div>
            </div>
            <div className="flex-1 bg-blue70/90 dark:bg-blue90 px-20 py-16 text-white dark:text-cyan-200 flex flex-col justify-center">
              <h3 className="text-5xl font-extrabold mb-6">C++</h3>
              <p className="text-lg text-blue-100 dark:text-cyan-200 leading-relaxed">
                Explore low‑level programming, data structures and algorithms with C++ — perfect for
                performance‑critical and competitive‑programming work.
              </p>
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}
