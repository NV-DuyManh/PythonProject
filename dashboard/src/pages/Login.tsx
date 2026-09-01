import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GitBranch, Loader2 } from 'lucide-react';

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
            <span className="text-white font-black text-2xl tracking-tight">CG</span>
          </div>
        </div>
        <h2 className="mt-8 text-center text-3xl font-black text-slate-900 tracking-tight">
          Welcome to CodeGate
        </h2>
        <p className="mt-2 text-center text-sm font-medium text-slate-500">
          Local PR Quality & Intelligence Platform
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-[440px]">
        <div className="bg-white/80 backdrop-blur-xl py-10 px-4 shadow-[0_20px_55px_rgba(15,23,42,0.06)] sm:rounded-3xl sm:px-10 border border-slate-200/60">
          <button
            onClick={handleLogin}
            className="w-full flex justify-center items-center py-3.5 px-4 rounded-xl shadow-sm text-[15px] font-bold text-white bg-slate-900 hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-900/10 transition-all hover:-translate-y-0.5"
          >
            <GitBranch className="w-5 h-5 mr-2.5 opacity-90" />
            Continue with GitHub
          </button>
          
          <div className="mt-8">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs font-semibold uppercase tracking-wider">
                <span className="px-3 bg-white text-slate-400">Secure Local OAuth</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
