import React, { useContext } from 'react';
import Navbar from '../components/Navbar';
import LoginModal from '../components/LoginModal';
import { Outlet } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

function Layout() {
  const { showLoginModal, openLoginModal, closeLoginModal } = useContext(AuthContext);

  return (
    <div className="min-h-screen w-full text-black dark:bg-gray-900 dark:text-white flex flex-col">
      <Navbar onLoginClick={openLoginModal} />
      <main className="flex-grow w-full">
        <Outlet />
      </main>

      <footer className="w-full bg-blue0 dark:bg-blue90 dark:text-cyan-100 text-gray-700 text-sm font-medium text-center py-5">
        &copy; {new Date().getFullYear()} Your Learning Platform. All rights reserved.
      </footer>

      {showLoginModal && <LoginModal onClose={closeLoginModal} />}
    </div>
  );
}

export default Layout;
