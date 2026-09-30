import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { AuthShell } from '../components/ui/AuthShell';
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
      await refresh();
      await setActiveWorkspace(data.workspace_id);
      
      setSuccess(true);
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
      <AuthShell title="Invitation" description="CodeGate workspace invitation">
        <p role="status" className="text-center text-slate-500 py-4 font-medium">Loading invitation...</p>
      </AuthShell>
    );
  }

  if (error) {
    return (
      <AuthShell title="Invalid Invitation" mascotImage="/mascot/mascot-empty.jpg">
        <div className="form-stack">
          <p className="alert alert--error" role="alert">
            <AlertTriangle size={18} />{error}
          </p>
          <Link className="btn-secondary w-full text-center justify-center" to="/">
            Go to Dashboard
          </Link>
        </div>
      </AuthShell>
    );
  }

  if (success) {
    return (
      <AuthShell title="Invitation Accepted!" mascotImage="/mascot/mascot-celebrate.jpg">
        <p role="status" className="alert alert--success">
          <CheckCircle size={18} />
          You are now a member of {invitation?.team_name}. Redirecting you to the dashboard...
        </p>
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="You've been invited!"
      description={
        <>
          <strong>{invitation?.inviter_name}</strong> invited you to collaborate in <strong>{invitation?.team_name}</strong>.
        </>
      }
      badgeText="Workspace Collaboration"
      mascotImage="/mascot/mascot-welcome.jpg"
    >
      <div className="form-stack">
        <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Your Assigned Role</span>
          <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
            {invitation?.role}
          </span>
        </div>

        {!authenticated ? (
          <>
            <p className="text-xs text-slate-500 text-center font-medium">
              Log in to accept this invitation.
            </p>
            <Button onClick={handleAccept} className="w-full">
              Log in to Accept
              <ArrowRight size={16} />
            </Button>
          </>
        ) : (
          <>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-indigo-50/40 border border-indigo-100">
              {user?.avatar_url ? (
                <img src={user.avatar_url} className="avatar" alt="" />
              ) : (
                <span className="avatar">{user?.username?.charAt(0).toUpperCase() || 'U'}</span>
              )}
              <div>
                <p className="font-semibold text-slate-900 text-sm">Logged in as {user?.display_name || user?.username}</p>
                <p className="muted text-xs">This account will join the workspace</p>
              </div>
            </div>
            <Button onClick={handleAccept} disabled={accepting} className="w-full">
              {accepting ? 'Accepting...' : 'Accept Invitation'}
            </Button>
          </>
        )}
      </div>
    </AuthShell>
  );
}
