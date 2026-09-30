import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { AuthShell } from '../components/ui/AuthShell';
import { Skeleton } from '../components/ui/Skeleton';
import { GraduationCap, Code2, Rocket, ArrowRight } from 'lucide-react';

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

  const presets = [
    { name: 'CS466 Capstone Team', icon: GraduationCap, type: 'education' as const },
    { name: 'Engineering Core', icon: Code2, type: 'engineering' as const },
    { name: 'Dev Studio Lab', icon: Rocket, type: 'personal' as const },
  ];

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
        body: JSON.stringify({ name: workspaceName.trim() })
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
      <div className="auth-page">
        <Skeleton className="h-32 w-full max-w-md rounded-2xl" />
      </div>
    );
  }

  return (
    <AuthShell
      title="Create your workspace"
      description="A shared place for your repositories, reviews, and interactive coding lessons."
      badgeText="Step 1 of 1 · Workspace Setup"
      mascotImage="/mascot/mascot-welcome.jpg"
    >
      <form className="form-stack" onSubmit={handleSubmit}>
        {/* Anteater Coach Speech Bubble */}
        <div className="p-3.5 rounded-xl bg-indigo-50/70 border border-indigo-100 flex items-start gap-3">
          <span className="text-xl">🐾</span>
          <div className="text-xs text-indigo-950 leading-relaxed">
            <strong>Anteater Coach:</strong> Workspaces organize your projects and student reviews. Every PR opened here will receive instant feedback and lessons!
          </div>
        </div>

        <div className="form-field">
          <label htmlFor="workspaceName" className="flex items-center justify-between">
            <span>Workspace Name</span>
            <span className="text-xs text-slate-400 font-normal">Give your team a home</span>
          </label>
          <input
            id="workspaceName"
            name="workspaceName"
            type="text"
            required
            value={workspaceName}
            onChange={e => setWorkspaceName(e.target.value)}
            placeholder="e.g., CS466-Group-04 or Alpha-Devs"
            aria-invalid={!!error}
            className="w-full text-base"
          />
        </div>

        {/* Quick Suggestion Chips */}
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">
            Suggested Presets
          </label>
          <div className="flex flex-wrap gap-2">
            {presets.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => {
                  setWorkspaceName(preset.name);
                }}
                className={`text-xs px-3 py-1.5 rounded-lg border flex items-center gap-1.5 transition-all ${
                  workspaceName === preset.name
                    ? 'bg-indigo-50 border-indigo-300 text-indigo-700 font-semibold'
                    : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
              >
                <preset.icon size={13} />
                {preset.name}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="alert alert--error" role="alert">{error}</p>}

        <button
          type="submit"
          disabled={isSubmitting || !workspaceName.trim()}
          className="btn-primary w-full py-3 text-[15px] shadow-lg shadow-indigo-500/20"
        >
          {isSubmitting ? (
            'Creating workspace...'
          ) : (
            <>
              Create Workspace
              <ArrowRight size={17} strokeWidth={2.2} />
            </>
          )}
        </button>
      </form>
    </AuthShell>
  );
}
