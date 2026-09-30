import { PageHeader } from '../components/ui/PageHeader';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { PRDashboardItem } from '../types';
import { GitPullRequest, RefreshCw, Search } from 'lucide-react';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Skeleton } from '../components/ui/Skeleton';
import { formatPercentage, formatDate } from '../lib/utils';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../contexts/AuthContext';

export function PullRequests() {
  const { workspaceVersion } = useAuth();
  const [data, setData] = useState<PRDashboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getPullRequests()
      .then((prs) => setData(prs))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [workspaceVersion]);

  const filtered = data.filter((pr) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return pr.title.toLowerCase().includes(s) ||
           pr.author.toLowerCase().includes(s) ||
           pr.repository.toLowerCase().includes(s);
  });

  if (loading) {
    return (
      <div className="page-stack animate-pulse">
        <Skeleton className="w-full h-16 rounded-2xl" />
        <Skeleton className="w-full h-[64px] rounded-2xl" />
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
        title="Pull Requests"
        description="Review queue, automated scans, and student lesson insights."
        actions={
          <button className="btn-secondary" onClick={load}>
            <RefreshCw size={16} />Refresh
          </button>
        }
      />

      <div className="filter-card">
        <label className="search-field">
          <span className="sr-only">Search pull requests</span>
          <Search size={16} />
          <input
            type="search"
            placeholder="Search title, author, repository…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </label>
        <span className="scope-note font-medium text-slate-500">
          {filtered.length} of {data.length} loaded pull requests
        </span>
      </div>

      {/* TABLE or EMPTY STATE */}
      {filtered.length === 0 ? (
        <div className="py-4">
          <EmptyState
            icon={GitPullRequest}
            image={data.length === 0 ? "/mascot/mascot-empty.jpg" : undefined}
            title={data.length === 0 ? "No pull requests yet" : "No results found"}
            description={
              data.length === 0
                ? "Pull requests will appear here after CodeGate receives a GitHub webhook or an analysis is created."
                : "Try adjusting your search terms."
            }
          />
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="cg-table">
            <caption className="table-caption">Loaded results; the API returns up to 20 records.</caption>
            <thead>
              <tr>
                <th>Pull Request</th>
                <th>Repository</th>
                <th>Author</th>
                <th>Quality</th>
                <th>Risk</th>
                <th>Policy</th>
                <th>Tests</th>
                <th>Coverage</th>
                <th>Findings</th>
                <th>Analysis</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((pr) => (
                <tr key={pr.pull_request_id}>
                  <td>
                    <Link to={`/pull-requests/${pr.pull_request_id}`} className="cell-link font-semibold text-slate-900">
                      {pr.title}
                    </Link>
                    <div className="cell-muted" style={{ marginTop: '2px' }}>
                      <span className="font-bold text-indigo-600">#{pr.number}</span> · {pr.state}
                    </div>
                  </td>
                  <td className="font-medium text-slate-700">{pr.repository}</td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold flex items-center justify-center">
                        {pr.author?.charAt(0)?.toUpperCase() || '?'}
                      </span>
                      <span>{pr.author}</span>
                    </div>
                  </td>
                  <td>
                    {pr.quality_score != null ? (
                      <div className="flex items-center gap-2">
                        <Badge variant={pr.quality_grade === 'A' ? 'success' : pr.quality_grade === 'B' ? 'success' : pr.quality_grade === 'C' ? 'warning' : 'danger'}>
                          {pr.quality_grade}
                        </Badge>
                        <span className="cell-muted font-bold">{pr.quality_score.toFixed(0)}</span>
                      </div>
                    ) : (
                      <span className="cell-muted">N/A</span>
                    )}
                  </td>
                  <td>
                    {pr.risk_level ? (
                      <Badge variant={pr.risk_level === 'LOW' ? 'success' : pr.risk_level === 'MEDIUM' ? 'warning' : 'danger'}>
                        {pr.risk_level}
                      </Badge>
                    ) : (
                      <span className="cell-muted">N/A</span>
                    )}
                  </td>
                  <td>
                    <Badge variant={pr.policy_decision === 'PASS' ? 'success' : pr.policy_decision === 'WARNING' ? 'warning' : pr.policy_decision === 'BLOCK' ? 'danger' : 'default'}>
                      {pr.policy_decision || 'Not evaluated'}
                    </Badge>
                  </td>
                  <td>
                    {pr.test_outcome ? (
                      <Badge variant={pr.test_outcome === 'PASSED' ? 'success' : pr.test_outcome === 'FAILED' ? 'danger' : 'default'}>
                        {pr.test_outcome}
                      </Badge>
                    ) : (
                      <span className="cell-muted">N/A</span>
                    )}
                  </td>
                  <td>
                    <span className="font-mono font-medium">
                      {pr.changed_line_coverage != null ? formatPercentage(pr.changed_line_coverage) : 'N/A'}
                    </span>
                  </td>
                  <td>
                    {(pr.critical_findings + pr.high_findings) > 0 ? (
                      <Badge variant="danger">
                        {pr.critical_findings + pr.high_findings}
                      </Badge>
                    ) : (
                      <span className="cell-muted">0</span>
                    )}
                  </td>
                  <td>
                    <Badge variant={pr.analysis_status === 'COMPLETED' ? 'success' : pr.analysis_status === 'FAILED' ? 'danger' : ['RUNNING', 'QUEUED'].includes(pr.analysis_status || '') ? 'info' : 'default'}>
                      {pr.analysis_status || 'Not run'}
                    </Badge>
                  </td>
                  <td className="cell-muted">
                    {pr.updated_at ? formatDate(pr.updated_at) : 'N/A'}
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
