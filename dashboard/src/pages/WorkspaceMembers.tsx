import { useEffect, useState } from 'react';
import { UserPlus, Mail, ShieldAlert, Trash2, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/Button';

interface Member {
  user_id: number;
  github_login: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
  joined_at: string;
}

interface Invitation {
  id: number;
  role: string;
  invitee_github_login: string | null;
  invitee_email: string | null;
  status: string;
  expires_at: string;
  created_at: string;
}

const ROLES = ['ADMIN', 'MAINTAINER', 'REVIEWER', 'DEVELOPER'];

export function WorkspaceMembers() {
  const { activeWorkspace, user: currentUser } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Invite modal state
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteRole, setInviteRole] = useState('DEVELOPER');
  const [inviteLogin, setInviteLogin] = useState('');
  const [inviteLink, setInviteLink] = useState<string | null>(null);
  const [inviting, setInviting] = useState(false);
  
  // The backend enforces true security.
  const isAdmin = activeWorkspace?.role === 'ADMIN';
  const canInvite = activeWorkspace?.role === 'ADMIN' || activeWorkspace?.role === 'MAINTAINER';
  const availableRoles = isAdmin ? ROLES : ROLES.filter(r => r !== 'ADMIN');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch('http://127.0.0.1:8000/api/v1/workspaces/active/members', {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to fetch members data');
      const data = await res.json();
      setMembers(data.members);
      setInvitations(data.invitations);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeWorkspace) {
      fetchData();
    }
  }, [activeWorkspace]);

  const handleCreateInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviting(true);
    setError(null);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/workspaces/active/invitations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          role: inviteRole,
          invitee_github_login: inviteLogin.trim() || null,
        })
      });
      
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create invitation');
      }
      
      const data = await res.json();
      // Assume frontend runs on same domain as current URL, or use a specific configured URL
      const link = `${window.location.origin}/invite/${data.token}`;
      setInviteLink(link);
      fetchData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setInviting(false);
    }
  };

  const handleRevokeInvite = async (invitationId: number) => {
    if (!confirm('Are you sure you want to revoke this invitation?')) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/workspaces/active/invitations/${invitationId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to revoke invitation');
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/workspaces/active/members/${userId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ role: newRole })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to update role');
      }
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!confirm('Are you sure you want to remove this member from the workspace? They will lose access immediately.')) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/workspaces/active/members/${userId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to remove member');
      }
      fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) {
    return <div className="p-8 text-slate-500 font-medium">Loading members...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">ACCESS CONTROL</p>
          <h2 className="page-hero__title flex items-center gap-2">
            Workspace Members
          </h2>
          <p className="page-hero__desc">
            Manage who has access to {activeWorkspace?.name} and their permissions.
          </p>
        </div>
        {canInvite && (
          <div className="page-hero__actions">
            <Button onClick={() => setShowInviteModal(true)} className="flex items-center gap-2">
              <UserPlus size={18} />
              Invite Teammate
            </Button>
          </div>
        )}
      </div>
      
      {error && !showInviteModal && (
        <div className="bg-red-50 border border-red-100 text-red-600 p-4 rounded-xl mb-2 font-medium">
          {error}
        </div>
      )}

      {/* Members List */}
      <div className="table-wrapper">
        <table className="cg-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Joined</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {members.map(member => (
              <tr key={member.user_id}>
                <td>
                  <div className="flex items-center gap-3">
                    {member.avatar_url ? (
                      <img src={member.avatar_url} alt="" className="w-8 h-8 rounded-full border border-slate-200" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-white shadow-sm">
                        {member.github_login.charAt(0).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <div className="font-bold text-slate-900">
                        {member.display_name || member.github_login}
                        {member.user_id === currentUser?.id && (
                          <span className="ml-2 text-[10px] font-bold bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full uppercase tracking-wider">You</span>
                        )}
                      </div>
                      <div className="text-slate-500 text-xs font-medium">@{member.github_login}</div>
                    </div>
                  </div>
                </td>
                <td>
                  {isAdmin && member.user_id !== currentUser?.id ? (
                    <select
                      value={member.role}
                      onChange={(e) => handleRoleChange(member.user_id, e.target.value)}
                      className="bg-white border border-slate-200 text-slate-900 font-medium text-sm rounded-lg focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 block px-3 py-1.5 outline-none transition-all shadow-sm"
                    >
                      {availableRoles.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  ) : (
                    <span className={`px-2.5 py-1 rounded-md text-xs font-bold tracking-wide ${
                      member.role === 'ADMIN' ? 'bg-purple-50 text-purple-700 border border-purple-100' :
                      member.role === 'MAINTAINER' ? 'bg-blue-50 text-blue-700 border border-blue-100' :
                      'bg-slate-100 text-slate-600 border border-slate-200'
                    }`}>
                      {member.role}
                    </span>
                  )}
                </td>
                <td className="cell-muted">
                  {new Date(member.joined_at).toLocaleDateString()}
                </td>
                <td className="text-right">
                  {isAdmin && member.user_id !== currentUser?.id && (
                    <button 
                      onClick={() => handleRemoveMember(member.user_id)}
                      className="text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors p-2"
                      title="Remove member"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Pending Invitations */}
      {canInvite && invitations.length > 0 && (
        <>
          <h3 className="text-lg font-black text-slate-900 mb-2 mt-4 flex items-center gap-2">
            <Mail size={18} className="text-indigo-500" />
            Pending Invitations
          </h3>
          <div className="table-wrapper">
            <table className="cg-table">
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Role</th>
                  <th>Expires</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {invitations.map(inv => (
                  <tr key={inv.id}>
                    <td className="font-medium text-slate-900">
                      {inv.invitee_github_login ? `@${inv.invitee_github_login}` : (inv.invitee_email || 'Anyone with link')}
                    </td>
                    <td>
                      <span className="px-2.5 py-1 rounded-md text-xs font-bold tracking-wide bg-slate-100 text-slate-600 border border-slate-200">
                        {inv.role}
                      </span>
                    </td>
                    <td className="cell-muted">
                      {new Date(inv.expires_at).toLocaleDateString()}
                    </td>
                    <td className="text-right">
                      <button 
                        onClick={() => handleRevokeInvite(inv.id)}
                        className="text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors px-3 py-1.5 text-sm font-bold"
                      >
                        Revoke
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <div className="bg-white border border-slate-200/60 rounded-3xl p-8 max-w-md w-full shadow-[0_20px_55px_rgba(15,23,42,0.12)] relative">
            <button 
              onClick={() => {
                setShowInviteModal(false);
                setInviteLink(null);
                setError(null);
              }}
              className="absolute top-6 right-6 w-8 h-8 flex items-center justify-center rounded-full text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            >
              <X size={20} />
            </button>
            
            <h2 className="text-2xl font-black text-slate-900 mb-6 tracking-tight">Invite Teammate</h2>
            
            {error && (
              <div className="bg-red-50 border border-red-100 text-red-600 font-medium p-3 rounded-xl mb-6 text-sm">
                {error}
              </div>
            )}
            
            {inviteLink ? (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-xl text-sm font-medium flex items-start gap-3 shadow-sm">
                  <ShieldAlert size={18} className="mt-0.5 shrink-0 text-green-600" />
                  <p>Invitation created successfully. Share this link securely with your teammate.</p>
                </div>
                
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    readOnly 
                    value={inviteLink} 
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 font-mono font-medium focus:outline-none focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 transition-all shadow-sm"
                    onClick={(e) => (e.target as HTMLInputElement).select()}
                  />
                  <Button 
                    onClick={() => {
                      navigator.clipboard.writeText(inviteLink);
                      alert('Link copied to clipboard!');
                    }}
                    variant="secondary"
                    className="shrink-0"
                  >
                    Copy
                  </Button>
                </div>
                
                <Button 
                  onClick={() => {
                    setShowInviteModal(false);
                    setInviteLink(null);
                  }}
                  className="w-full mt-2"
                >
                  Done
                </Button>
              </div>
            ) : (
              <form onSubmit={handleCreateInvite} className="space-y-5">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">
                    GitHub Username <span className="text-slate-400 font-medium">(Optional)</span>
                  </label>
                  <input
                    type="text"
                    value={inviteLogin}
                    onChange={(e) => setInviteLogin(e.target.value)}
                    placeholder="e.g. octocat"
                    className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 font-medium placeholder-slate-400 focus:outline-none focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 transition-all shadow-sm"
                  />
                  <p className="text-xs font-medium text-slate-500 mt-2">
                    If provided, only this GitHub user can accept the invitation.
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-900 font-medium focus:outline-none focus:ring-4 focus:ring-indigo-600/10 focus:border-indigo-600 transition-all shadow-sm appearance-none"
                    style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundPosition: `right 0.5rem center`, backgroundRepeat: `no-repeat`, backgroundSize: `1.5em 1.5em`, paddingRight: `2.5rem` }}
                  >
                    {availableRoles.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>
                
                <div className="pt-6 flex justify-end gap-3">
                  <Button 
                    type="button" 
                    variant="ghost" 
                    onClick={() => setShowInviteModal(false)}
                    className="font-bold text-slate-600 hover:text-slate-900"
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={inviting}>
                    {inviting ? 'Creating...' : 'Create Invite Link'}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
