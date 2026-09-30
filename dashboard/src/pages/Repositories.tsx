import { PageHeader } from '../components/ui/PageHeader';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { RepositoryDashboardItem } from '../types';
import { GitBranch, RefreshCw, Sparkles, FolderGit2 } from 'lucide-react';
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
      <div className="page-stack animate-pulse">
        <Skeleton className="w-full h-16 rounded-2xl" />
        <Skeleton className="w-full h-[400px] rounded-2xl" />
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
    <div className="page-stack">
      <PageHeader
        title="Repositories"
        description="Connected source code repositories, health metrics, and automated review coverage."
        actions={
          <button className="btn-secondary" onClick={load}>
            <RefreshCw size={16} />Refresh
          </button>
        }
      />

      {data.length === 0 ? (
        <div className="py-4">
          <EmptyState
            icon={GitBranch}
            image="/mascot/mascot-empty.jpg"
            title="No repositories connected"
            description="Repositories will appear here once CodeGate has analyzed pull requests from them."
          >
            <Link className="btn-primary" to="/integrations/github">
              <Sparkles size={16} /> Connect GitHub App
            </Link>
          </EmptyState>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="cg-table">
            <caption className="table-caption">Loaded results; the API returns up to 20 records.</caption>
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
                    <Link to={`/repositories/${repo.repository_id}`} className="cell-link font-semibold text-slate-900 flex items-center gap-2">
                      <FolderGit2 size={16} className="text-indigo-600 flex-shrink-0" />
                      {repo.name}
                    </Link>
                  </td>
                  <td>
                    <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                      {repo.provider}
                    </span>
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
                  <td>
                    <span className="font-bold text-slate-800">{repo.open_pr_count ?? 0}</span>
                  </td>
                  <td>
                    {repo.average_quality !== null ? (
                      <span className="font-bold" style={{ color: repo.average_quality >= 80 ? 'var(--cg-green)' : repo.average_quality >= 60 ? 'var(--cg-amber)' : 'var(--cg-red)' }}>
                        {formatScore(repo.average_quality)}
                      </span>
                    ) : (
                      <span className="cell-muted">N/A</span>
                    )}
                  </td>
                  <td>
                    {repo.average_risk !== null ? (
                      <span className="font-bold" style={{ color: repo.average_risk <= 30 ? 'var(--cg-green)' : repo.average_risk <= 70 ? 'var(--cg-amber)' : 'var(--cg-red)' }}>
                        {formatScore(repo.average_risk)}
                      </span>
                    ) : (
                      <span className="cell-muted">N/A</span>
                    )}
                  </td>
                  <td>
                    <span className="font-mono">
                      {repo.block_rate !== null ? formatPercentage(repo.block_rate) : 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className="font-mono">
                      {repo.test_pass_rate !== null ? formatPercentage(repo.test_pass_rate) : 'N/A'}
                    </span>
                  </td>
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
