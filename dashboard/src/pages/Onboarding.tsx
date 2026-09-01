import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, Users } from 'lucide-react';

export function Onboarding() {
  const { authenticated, loading, workspaces, refresh } = useAuth();
  const navigate = useNavigate();
  const [workspaceName, setWorkspaceName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!loading && !authenticated) {
      navigate('/login', { replace: true });
    } else if (!loading && workspaces.length > 0) {
      navigate('/dashboard', { replace: true });
    }
  }, [authenticated, loading, workspaces, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspaceName.trim()) return;

    setIsSubmitting(true);
    setError('');

    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/workspaces', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ name: workspaceName })
      });
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to create workspace');
      }
      
      await refresh();
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to create workspace');
      setIsSubmitting(false);
    }
  };

  if (loading || (authenticated && workspaces.length > 0)) {
    return (
      <div className="min-h-screen bg-[#f4f7fb] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-600/20">
            <Users className="w-6 h-6 text-white" />
          </div>
        </div>
        <h2 className="mt-8 text-center text-3xl font-black text-slate-900 tracking-tight">
          Welcome to CodeGate
        </h2>
        <p className="mt-2 text-center text-sm font-medium text-slate-500">
          Create your first workspace to get started
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[440px]">
        <div className="bg-white/80 backdrop-blur-xl py-10 px-4 shadow-[0_20px_55px_rgba(15,23,42,0.06)] sm:rounded-3xl sm:px-10 border border-slate-200/60">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="workspaceName" className="block text-sm font-bold text-slate-700">
                Workspace Name
              </label>
              <div className="mt-2">
                <input
                  id="workspaceName"
                  name="workspaceName"
                  type="text"
                  required
                  value={workspaceName}
                  onChange={(e) => setWorkspaceName(e.target.value)}
                  className="appearance-none block w-full px-4 py-3.5 border border-slate-200 rounded-xl shadow-sm bg-white placeholder-slate-400 text-slate-900 font-medium focus:outline-none focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 sm:text-sm transition-all"
                  placeholder="e.g., Engineering Team"
                />
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm font-medium p-3 bg-red-50 rounded-lg border border-red-100">{error}</div>
            )}

            <div>
              <button
                type="submit"
                disabled={isSubmitting || !workspaceName.trim()}
                className="w-full flex justify-center items-center py-3.5 px-4 border border-transparent rounded-xl shadow-[0_14px_30px_rgba(79,70,229,0.28)] text-[15px] font-bold text-white bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 focus:outline-none focus:ring-4 focus:ring-indigo-600/20 disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed transition-all hover:-translate-y-0.5"
              >
                {isSubmitting ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  'Create Workspace'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
