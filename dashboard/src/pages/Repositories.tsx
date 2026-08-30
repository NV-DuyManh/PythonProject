import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { RepositoryDashboardItem } from '../types';
import { GitBranch, RefreshCw, AlertTriangle } from 'lucide-react';

export function Repositories() {
  const [data, setData] = useState<RepositoryDashboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getRepositories()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div>
        <div className="skeleton skeleton--hero" />
        <div className="skeleton skeleton--table" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-state">
        <AlertTriangle className="error-state__icon" />
        <div className="error-state__title">Unable to load data</div>
        <div className="error-state__desc">{error}</div>
        <button className="btn-primary" onClick={load}>
          <RefreshCw size={14} /> Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">CODE MANAGEMENT</p>
          <h2 className="page-hero__title">Repositories</h2>
          <p className="page-hero__desc">Monitor engineering health across connected repositories.</p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-primary" onClick={load}>
            <RefreshCw size={15} strokeWidth={2} /> Refresh
          </button>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="empty-state">
          <GitBranch size={56} strokeWidth={1.2} className="empty-state__icon" />
          <div className="empty-state__title">No repositories connected</div>
          <div className="empty-state__desc">
            Repositories will appear here once CodeGate has analyzed pull requests from them.
          </div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="cg-table">
            <thead>
              <tr>
                <th>Repository</th>
                <th>Provider</th>
                <th>Open PRs</th>
                <th>Avg Quality</th>
                <th>Avg Risk</th>
                <th>Block Rate</th>
                <th>Test Pass Rate</th>
                <th>Last Analysis</th>
              </tr>
            </thead>
            <tbody>
              {data.map((repo) => (
                <tr key={repo.repository_id}>
                  <td>
                    <Link to={`/repositories/${repo.repository_id}`} className="cell-link">
                      {repo.name}
                    </Link>
                  </td>
                  <td>
                    <span className="badge badge--indigo">{repo.provider}</span>
                  </td>
                  <td>{repo.open_pr_count}</td>
                  <td>
                    {repo.average_quality !== null
                      ? <span style={{ fontWeight: 700, color: repo.average_quality >= 80 ? 'var(--cg-green)' : repo.average_quality >= 60 ? 'var(--cg-amber)' : 'var(--cg-red)' }}>{repo.average_quality.toFixed(1)}</span>
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>
                    {repo.average_risk !== null
                      ? <span style={{ fontWeight: 700, color: repo.average_risk >= 75 ? 'var(--cg-red)' : repo.average_risk >= 50 ? 'var(--cg-amber)' : 'var(--cg-green)' }}>{repo.average_risk.toFixed(1)}</span>
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>
                    {repo.block_rate !== null
                      ? `${repo.block_rate.toFixed(1)}%`
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>
                    {repo.test_pass_rate !== null
                      ? `${repo.test_pass_rate.toFixed(1)}%`
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td className="cell-muted">
                    {repo.last_analysis_at
                      ? new Date(repo.last_analysis_at).toLocaleDateString()
                      : 'Never'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
