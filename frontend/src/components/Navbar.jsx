import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Guide', path: '/instructions' },
    ...(isAuthenticated ? [{ name: 'Dashboard', path: '/dashboard' }] : []),
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200/80">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-baseline gap-2">
              <span className="font-bold text-slate-950 text-base tracking-tight">Synapt</span>
              <span className="hidden sm:inline text-xs font-medium text-slate-500 uppercase tracking-wider">Supply Chain Crisis Assistant</span>
            </Link>

            <div className="hidden md:flex items-center gap-6">
              {navLinks.map((link) => {
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`text-sm py-4 border-b-2 -mb-px transition-colors ${
                      isActive
                        ? 'text-slate-950 border-slate-950 font-semibold'
                        : 'text-slate-500 border-transparent hover:text-slate-900'
                    }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="flex items-center gap-4 text-sm">
            {isAuthenticated ? (
              <>
                <span className="hidden sm:inline text-xs text-slate-600 font-medium">
                  {user?.username}
                  <span className="text-slate-400"> · {user?.role || 'admin'}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="text-slate-700 hover:text-slate-950 border border-slate-300 hover:border-slate-800 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
                >
                  Sign out
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="bg-slate-900 hover:bg-slate-800 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition-colors"
              >
                Sign in
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
