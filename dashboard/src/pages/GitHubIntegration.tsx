import { useEffect, useState } from 'react';
import { CodeGateAPI } from '../api/client';
import { RefreshCw, CheckCircle, ExternalLink, Plus, AlertCircle, Trash2, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function GitHubIntegration() {
  const { workspaceVersion, user } = useAuth();
  const [connections, setConnections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [installing, setInstalling] = useState(false);
  const [syncingId, setSyncingId] = useState<number | null>(null);
  const [syncResult, setSyncResult] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getGitHubConnections()
      .then(setConnections)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [workspaceVersion]);

  const handleConnect = async () => {
    try {
      setInstalling(true);
      setError(null);
      const res = await CodeGateAPI.installGitHubApp();
      window.location.href = res.install_url;
    } catch (err: any) {
      setError(err.message || 'Failed to start GitHub installation');
      setInstalling(false);
    }
  };

  const handleDisconnect = async (id: number) => {
    if (!confirm('Are you sure you want to disconnect this installation? Repository history will be preserved.')) return;
    try {
      await CodeGateAPI.disconnectGitHubConnection(id);
      load();
    } catch (err: any) {
      alert('Failed to disconnect: ' + err.message);
    }
  };

  const handleSync = async (id: number) => {
    try {
      setSyncingId(id);
      setError(null);
      setSyncResult(null);
      const res = await CodeGateAPI.syncGitHubConnection(id);
      setSyncResult(`Sync complete: Discovered ${res.discovered}, Created ${res.created}, Updated ${res.updated}, Removed Access ${res.removed_access}.`);
      load();
    } catch (err: any) {
      setError(`Sync failed: ${err.message}`);
    } finally {
      setSyncingId(null);
    }
  };

  return (
    <div>
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">INTEGRATIONS</p>
          <h2 className="page-hero__title">GitHub Integration</h2>
          <p className="page-hero__desc">Manage CodeGate GitHub App installations for this Workspace.</p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-secondary" onClick={load} disabled={loading}>
            <RefreshCw size={15} strokeWidth={2} className={loading ? "spin" : ""} /> Refresh
          </button>
          <button className="btn-primary" onClick={handleConnect} disabled={installing || !user?.active_workspace_id}>
            <Plus size={15} strokeWidth={2} /> {installing ? 'Connecting...' : 'Connect GitHub'}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert--error" style={{ marginBottom: '24px' }}>
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* Render URL param connected msg if redirected from callback */}
      {window.location.search.includes('github=connected') && (
        <div className="alert alert--success" style={{ marginBottom: '24px' }}>
          <CheckCircle size={16} />
          GitHub installation connected successfully! Initial repository sync is running in the background.
        </div>
      )}

      {syncResult && (
        <div className="alert alert--success" style={{ marginBottom: '24px' }}>
          <CheckCircle size={16} />
          {syncResult}
        </div>
      )}

      <div className="dashboard-grid dashboard-grid--stats">
        <div className="dashboard-panel" style={{ gridColumn: '1 / -1' }}>
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Installed Accounts</div>
          </div>
          <div className="dashboard-panel__body" style={{ padding: '0' }}>
            {loading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--cg-muted)' }}>Loading...</div>
            ) : connections.length === 0 ? (
              <div style={{ padding: '48px', textAlign: 'center', color: 'var(--cg-muted)' }}>
                No GitHub connections found for this workspace. Click "Connect GitHub" to get started.
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--cg-border)' }}>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Account</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Type</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Repositories</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Status</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Last Sync</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {connections.map((c) => (
                    <tr key={c.id} style={{ borderBottom: '1px solid var(--cg-border)', background: 'var(--cg-surface-50)' }}>
                      <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--cg-text)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <User size={16} color="var(--cg-text-secondary)" />
                          {c.account_login}
                        </div>
                      </td>
                      <td style={{ padding: '16px 24px', color: 'var(--cg-text-secondary)' }}>
                        {c.account_type}
                      </td>
                      <td style={{ padding: '16px 24px', color: 'var(--cg-text-secondary)' }}>
                        <span className="cg-badge" style={{ background: 'var(--cg-surface-100)', color: 'var(--cg-text-secondary)' }}>
                          {c.repository_selection === 'all' ? 'All Repositories' : 'Selected Only'}
                        </span>
                      </td>
                      <td style={{ padding: '16px 24px' }}>
                        {c.status === 'active' ? (
                          <span className="cg-badge" style={{ background: 'var(--cg-success-bg)', color: 'var(--cg-success)' }}>
                            <CheckCircle size={12} style={{ marginRight: '4px' }} /> Active
                          </span>
                        ) : (
                          <span className="cg-badge" style={{ background: 'var(--cg-error-bg)', color: 'var(--cg-error)' }}>
                            <AlertCircle size={12} style={{ marginRight: '4px' }} /> {c.status}
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '16px 24px', color: 'var(--cg-text-secondary)' }}>
                        {c.last_sync_status === 'SUCCESS' ? (
                          <span className="cg-badge" style={{ background: 'var(--cg-success-bg)', color: 'var(--cg-success)' }}>
                            Success
                          </span>
                        ) : c.last_sync_status === 'FAILED' ? (
                          <span className="cg-badge" style={{ background: 'var(--cg-error-bg)', color: 'var(--cg-error)' }}>
                            Failed
                          </span>
                        ) : (
                          <span style={{ fontSize: '12px' }}>Never</span>
                        )}
                        {c.last_synced_at && <div style={{ fontSize: '11px', marginTop: '4px', color: 'var(--cg-muted)' }}>{new Date(c.last_synced_at).toLocaleString()}</div>}
                      </td>
                      <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                          <button 
                            className="btn-secondary" 
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                            onClick={() => handleSync(c.id)}
                            disabled={syncingId === c.id}
                          >
                            <RefreshCw size={14} className={syncingId === c.id ? 'spin' : ''} style={{ marginRight: '4px' }} /> 
                            {syncingId === c.id ? 'Syncing...' : 'Sync now'}
                          </button>
                          <a href={`https://github.com/settings/installations/${c.installation_id}`} target="_blank" rel="noreferrer" style={{ color: 'var(--cg-accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            Manage repositories <ExternalLink size={12} />
                          </a>
                          <button 
                            className="btn-danger" 
                            style={{ padding: '4px 8px', fontSize: '12px' }}
                            onClick={() => handleDisconnect(c.id)}
                            disabled={c.status === 'disconnected'}
                          >
                            <Trash2 size={12} /> Disconnect
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
