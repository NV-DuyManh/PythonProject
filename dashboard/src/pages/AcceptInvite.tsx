import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Shield, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../contexts/AuthContext';

interface Invitation {
  id: number;
  team_name: string;
  inviter_name: string;
  role: string;
  status: string;
}

export function AcceptInvite() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const { authenticated, user, refresh, setActiveWorkspace } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [invitation, setInvitation] = useState<Invitation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [accepting, setAccepting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchInvite = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/api/v1/invitations/${token}`);
        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.detail || 'Failed to load invitation');
        }
        const data = await res.json();
        setInvitation(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    if (token) {
      fetchInvite();
    }
  }, [token]);

  const handleAccept = async () => {
    if (!authenticated) {
      // User must be logged in to accept.
      // Redirect to login, but keep the invite link to return to.
      navigate('/login', { state: { from: { pathname: `/invite/${token}` } } });
      return;
    }

    setAccepting(true);
    setError(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/invitations/${token}/accept`, {
        method: 'POST',
        credentials: 'include'
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to accept invitation');
      }
      
      const data = await res.json();
      
      // Update local context
      await refresh();
      await setActiveWorkspace(data.workspace_id);
      
      setSuccess(true);
      
      // Redirect after a short delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAccepting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#f4f7fb] flex flex-col items-center justify-center p-4">
        <div className="text-slate-500 font-medium">Loading invitation...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#f4f7fb] flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md bg-white border border-slate-200/60 rounded-3xl p-8 text-center shadow-[0_20px_55px_rgba(15,23,42,0.06)]">
          <div className="mx-auto w-12 h-12 bg-red-50 text-red-600 rounded-full flex items-center justify-center mb-4 border border-red-100">
            <AlertTriangle size={24} />
          </div>
          <h2 className="text-2xl font-black text-slate-900 mb-2">Invalid Invitation</h2>
          <p className="text-slate-500 mb-8 font-medium">{error}</p>
          <Link to="/">
            <Button className="w-full font-bold">Go to Dashboard</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-[#f4f7fb] flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md bg-white border border-slate-200/60 rounded-3xl p-8 text-center shadow-[0_20px_55px_rgba(15,23,42,0.06)]">
          <div className="mx-auto w-12 h-12 bg-green-50 text-green-600 rounded-full flex items-center justify-center mb-4 border border-green-100">
            <CheckCircle size={24} />
          </div>
          <h2 className="text-2xl font-black text-slate-900 mb-2">Invitation Accepted!</h2>
          <p className="text-slate-500 font-medium mb-6">
            You are now a member of {invitation?.team_name}. Redirecting you to the dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f7fb] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white/80 backdrop-blur-xl border border-slate-200/60 rounded-3xl overflow-hidden shadow-[0_20px_55px_rgba(15,23,42,0.06)]">
        <div className="p-8 text-center border-b border-slate-100 bg-white">
          <div className="mx-auto w-14 h-14 bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-600/20">
            <Shield size={26} className="text-white" />
          </div>
          <h2 className="text-3xl font-black text-slate-900 mb-3 tracking-tight">You've been invited!</h2>
          <p className="text-slate-500 font-medium leading-relaxed">
            <strong className="text-slate-900">{invitation?.inviter_name}</strong> has invited you to join the{' '}
            <strong className="text-slate-900">{invitation?.team_name}</strong> workspace on CodeGate.
          </p>
        </div>
        
        <div className="p-8 bg-slate-50/50">
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-8 text-center shadow-sm">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Your Role</p>
            <p className="text-xl font-black text-slate-900">{invitation?.role}</p>
          </div>

          {!authenticated ? (
            <div className="space-y-4">
              <p className="text-sm font-medium text-slate-500 text-center">
                You need to log in to accept this invitation.
              </p>
              <Button onClick={handleAccept} className="w-full flex items-center justify-center gap-2 font-bold py-6 text-[15px] rounded-xl shadow-[0_14px_30px_rgba(79,70,229,0.28)]" size="lg">
                Log in to Accept
                <ArrowRight size={18} />
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex items-center gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <img src={user?.avatar_url || ''} className="w-10 h-10 rounded-full border border-slate-200" alt="" />
                <div className="text-sm">
                  <p className="text-slate-900 font-bold">Logged in as {user?.display_name || user?.username}</p>
                  <p className="text-slate-500 font-medium text-xs">This account will join the workspace</p>
                </div>
              </div>
              <Button 
                onClick={handleAccept} 
                disabled={accepting}
                className="w-full flex items-center justify-center gap-2 font-bold py-6 text-[15px] rounded-xl shadow-[0_14px_30px_rgba(79,70,229,0.28)] transition-all hover:-translate-y-0.5" 
                size="lg"
              >
                {accepting ? 'Accepting...' : 'Accept Invitation'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
