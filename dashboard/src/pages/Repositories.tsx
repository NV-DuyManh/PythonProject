import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { RepositoryDashboardItem } from '../types';
import { GitBranch, RefreshCw } from 'lucide-react';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Skeleton } from '../components/ui/Skeleton';
import { formatPercentage, formatScore, formatDate } from '../lib/utils';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../contexts/AuthContext';

export function Repositories() {
  const { workspaceVersion } = useAuth();
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

  useEffect(() => { load(); }, [workspaceVersion]);

  if (loading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="w-full h-[140px] rounded-[22px]" />
        <Skeleton className="w-full h-[400px] rounded-[16px]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <ErrorState onRetry={load} description={error} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
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
        <div className="p-8">
          <EmptyState
            icon={GitBranch}
            title="No repositories connected"
            description="Repositories will appear here once CodeGate has analyzed pull requests from them."
          />
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="cg-table">
            <thead>
              <tr>
                <th>Repository</th>
                <th>Provider</th>
                <th>Access Status</th>
                <th>Open PRs</th>
                <th>Avg Quality</th>
                <th>Avg Risk</th>
                <th>Block Rate</th>
                <th>Test Pass Rate</th>
                <th>Last Synced</th>
              </tr>
            </thead>
            <tbody>
              {data.map((repo) => (
                <tr key={repo.repository_id}>
                  <td>
                    <Link to={`/repositories/${repo.repository_id}`} className="cell-link font-medium">
                      {repo.name}
                    </Link>
                  </td>
                  <td>
                    <Badge variant="indigo">{repo.provider}</Badge>
                  </td>
                  <td>
                    {repo.access_status === 'ACTIVE' ? (
                      <Badge variant="success">Active</Badge>
                    ) : repo.access_status === 'ACCESS_REMOVED' ? (
                      <Badge variant="destructive">Access Removed</Badge>
                    ) : (
                      <Badge variant="secondary">{repo.access_status || 'Unknown'}</Badge>
                    )}
                  </td>
                  <td>{repo.open_pr_count ?? 0}</td>
                  <td>
                    {repo.average_quality !== null
                      ? <span className="font-medium" style={{ color: repo.average_quality >= 80 ? 'var(--cg-green)' : repo.average_quality >= 60 ? 'var(--cg-amber)' : 'var(--cg-red)' }}>{formatScore(repo.average_quality)}</span>
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>
                    {repo.average_risk !== null
                      ? <span className="font-medium" style={{ color: repo.average_risk <= 30 ? 'var(--cg-green)' : repo.average_risk <= 70 ? 'var(--cg-amber)' : 'var(--cg-red)' }}>{formatScore(repo.average_risk)}</span>
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>{repo.block_rate !== null ? formatPercentage(repo.block_rate) : <span className="cell-muted">—</span>}</td>
                  <td>{repo.test_pass_rate !== null ? formatPercentage(repo.test_pass_rate) : <span className="cell-muted">—</span>}</td>
                  <td className="cell-muted">
                    {repo.last_synced_at ? formatDate(repo.last_synced_at) : 'Never'}
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
