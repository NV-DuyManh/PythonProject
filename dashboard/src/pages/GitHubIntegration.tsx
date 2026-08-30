import { useEffect, useState } from 'react';
import { CodeGateAPI } from '../api/client';
import { GitBranch, RefreshCw, CheckCircle, ExternalLink } from 'lucide-react';

export function GitHubIntegration() {
  const [connections, setConnections] = useState<{ id: number; account_login: string; status: string; auth_type: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getGitHubConnections()
      .then(setConnections)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  return (
    <div>
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">INTEGRATIONS</p>
          <h2 className="page-hero__title">GitHub Integration</h2>
          <p className="page-hero__desc">Manage your CodeGate GitHub App installations.</p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-primary" onClick={load}>
            <RefreshCw size={15} strokeWidth={2} /> Refresh
          </button>
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid--stats">
        <div className="dashboard-panel" style={{ gridColumn: '1 / -1' }}>
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Installed Accounts</div>
          </div>
          <div className="dashboard-panel__body" style={{ padding: '0' }}>
            {loading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--cg-muted)' }}>Loading...</div>
            ) : error ? (
              <div style={{ padding: '24px', color: 'var(--cg-red)' }}>{error}</div>
            ) : connections.length === 0 ? (
              <div style={{ padding: '48px', textAlign: 'center', color: 'var(--cg-muted)' }}>
                No GitHub connections found.
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--cg-border)' }}>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Account</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Auth Type</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600 }}>Status</th>
                    <th style={{ padding: '12px 24px', color: 'var(--cg-text-secondary)', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {connections.map(c => (
                    <tr key={c.id} style={{ borderBottom: '1px solid var(--cg-border)' }}>
                      <td style={{ padding: '16px 24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 500 }}>
                          <GitBranch size={16} />
                          {c.account_login}
                        </div>
                      </td>
                      <td style={{ padding: '16px 24px' }}>
                        <span className="badge badge--gray">{c.auth_type.toUpperCase()}</span>
                      </td>
                      <td style={{ padding: '16px 24px' }}>
                        {c.status === 'active' ? (
                          <span className="badge badge--pass"><CheckCircle size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }}/> Active</span>
                        ) : (
                          <span className="badge badge--gray">{c.status}</span>
                        )}
                      </td>
                      <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                        <a href={`https://github.com/apps/codegate/installations/new`} target="_blank" rel="noreferrer" style={{ color: 'var(--cg-accent)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          Configure <ExternalLink size={12} />
                        </a>
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
