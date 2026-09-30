import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GitBranch, Shield, Sparkles, BookOpen } from 'lucide-react';
import { AuthShell } from '../components/ui/AuthShell';
import { Skeleton } from '../components/ui/Skeleton';

export function Login() {
  const { authenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && authenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [authenticated, loading, navigate]);

  const handleLogin = () => {
    window.location.href = 'http://127.0.0.1:8000/api/v1/auth/github/login';
  };

  if (loading) {
    return (
      <div className="auth-page">
        <Skeleton className="h-32 w-full max-w-md rounded-2xl" />
      </div>
    );
  }

  return (
    <AuthShell
      title="Welcome to CodeGate"
      description="Sign in to your engineering workspace."
      badgeText="Next-Gen Automated Code Review"
    >
      <div className="flex flex-col gap-4">
        <button
          onClick={handleLogin}
          className="btn-primary w-full py-3 text-[15px] shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/35"
        >
          <GitBranch size={19} strokeWidth={2.2} />
          Continue with GitHub
        </button>

        <p className="text-center text-xs text-slate-500 font-medium">
          Authentication is handled by GitHub.
        </p>

        <div className="border-t border-slate-100 pt-4 mt-2 grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100/80">
            <Sparkles size={16} className="mx-auto text-indigo-600 mb-1" />
            <div className="text-[11px] font-bold text-slate-800">Smart PRs</div>
            <div className="text-[10px] text-slate-400">Automated AI scan</div>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100/80">
            <BookOpen size={16} className="mx-auto text-purple-600 mb-1" />
            <div className="text-[11px] font-bold text-slate-800">Lessons</div>
            <div className="text-[10px] text-slate-400">Best practice tips</div>
          </div>
          <div className="p-2 rounded-xl bg-slate-50 border border-slate-100/80">
            <Shield size={16} className="mx-auto text-emerald-600 mb-1" />
            <div className="text-[11px] font-bold text-slate-800">Policy Gate</div>
            <div className="text-[10px] text-slate-400">Block bad commits</div>
          </div>
        </div>
      </div>
    </AuthShell>
  );
}
