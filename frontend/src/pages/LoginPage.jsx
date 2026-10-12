import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  if (isAuthenticated) {
    return null;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleUseDemoCredentials = () => {
    setUsername('admin');
    setPassword('admin');
  };

  const inputClass =
    'w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-slate-900 focus:ring-1 focus:ring-slate-900/10 transition-colors';

  return (
    <div className="flex-1 flex items-center justify-center py-16 px-4">
      <div className="w-full max-w-sm bg-white p-8 rounded-2xl border border-slate-200/90 shadow-[0_4px_20px_rgba(15,23,42,0.04)]">
        <h1 className="text-2xl font-bold tracking-tight text-slate-950">Operator sign in</h1>
        <p className="mt-1.5 text-xs sm:text-sm text-slate-500">Access the crisis response center & warehouse.</p>

        <form onSubmit={handleSubmit} className="mt-7 space-y-4">
          {error && (
            <div role="alert" className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2.5 text-red-700 text-xs sm:text-sm">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
              Username
            </label>
            <input
              id="username"
              type="text"
              required
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              className={inputClass}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className={inputClass}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold py-2.5 rounded-lg shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="mt-6 text-xs text-slate-500 text-center">
          Demo: <span className="font-mono text-slate-700 font-medium">admin / admin</span>
          {' · '}
          <button
            type="button"
            onClick={handleUseDemoCredentials}
            className="text-slate-950 font-semibold underline underline-offset-2 hover:text-slate-700"
          >
            Auto-fill
          </button>
        </p>
      </div>
    </div>
  );
}
