import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { PRDashboardItem } from '../types';
import { GitPullRequest, RefreshCw, Search } from 'lucide-react';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { formatPercentage, formatDate } from '../lib/utils';
import { Badge } from '../components/ui/Badge';

export function PullRequests() {
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

  useEffect(() => { load(); }, []);

  const filtered = data.filter((pr) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return pr.title.toLowerCase().includes(s) ||
           pr.author.toLowerCase().includes(s) ||
           pr.repository.toLowerCase().includes(s);
  });

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
      <div className="p-8">
        <ErrorState onRetry={load} description={error} />
      </div>
    );
  }

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <p className="page-hero__kicker">CODE REVIEW</p>
          </div>
          <h2 className="page-hero__title">Pull Requests</h2>
          <p className="page-hero__desc">Track quality, risk, tests and merge readiness.</p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-primary" onClick={load}>
            <RefreshCw size={15} strokeWidth={2} /> Refresh
          </button>
        </div>
      </div>

      {/* FILTER CARD */}
      <div className="filter-card">
        <div className="filter-card__info">
          <div className="filter-card__label">SEARCH & FILTER</div>
          <h3>{data.length} Pull Request{data.length !== 1 ? 's' : ''}</h3>
          <div className="filter-card__desc">Filter by title, author, or repository.</div>
        </div>
        <div className="filter-card__controls">
          <div style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '14px', top: '14px', color: 'var(--cg-muted)' }} />
            <input
              type="text"
              placeholder="Search pull requests..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '38px' }}
            />
          </div>
        </div>
      </div>

      {/* TABLE or EMPTY STATE */}
      {filtered.length === 0 ? (
        <div className="p-8">
          <EmptyState
            icon={GitPullRequest}
            title={data.length === 0 ? "No pull requests yet" : "No results found"}
            description={data.length === 0 
              ? "Pull requests will appear here after CodeGate receives a GitHub webhook or an analysis is created."
              : "Try adjusting your search terms."}
          />
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="cg-table">
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
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((pr) => (
                <tr key={pr.pull_request_id}>
                  <td>
                    <Link to={`/pull-requests/${pr.pull_request_id}`} className="cell-link font-medium">
                      {pr.title}
                    </Link>
                    <div className="cell-muted" style={{ marginTop: '2px' }}>
                      <span style={{ color: 'var(--cg-primary)' }}>#{pr.number}</span> · {pr.state}
                    </div>
                  </td>
                  <td>{pr.repository}</td>
                  <td>{pr.author}</td>
                  <td>
                    {pr.quality_score !== null ? (
                      <div className="flex items-center gap-2">
                        <Badge variant={pr.quality_grade === 'A' ? 'success' : pr.quality_grade === 'B' ? 'success' : pr.quality_grade === 'C' ? 'warning' : 'danger'}>
                          {pr.quality_grade}
                        </Badge>
                        <span className="cell-muted">{pr.quality_score.toFixed(0)}</span>
                      </div>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td>
                    {pr.risk_level ? (
                      <Badge variant={pr.risk_level === 'LOW' ? 'success' : pr.risk_level === 'MEDIUM' ? 'warning' : 'danger'}>
                        {pr.risk_level}
                      </Badge>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td>
                    <Badge variant={pr.policy_decision === 'PASS' ? 'success' : pr.policy_decision === 'WARNING' ? 'warning' : pr.policy_decision === 'BLOCK' ? 'danger' : 'default'}>
                      {pr.policy_decision || '—'}
                    </Badge>
                  </td>
                  <td>
                    {pr.test_outcome ? (
                      <Badge variant={pr.test_outcome === 'PASSED' ? 'success' : pr.test_outcome === 'FAILED' ? 'danger' : 'default'}>
                        {pr.test_outcome}
                      </Badge>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td className="whitespace-nowrap">
                    {formatPercentage(pr.changed_line_coverage)}
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
                  <td className="cell-muted whitespace-nowrap">
                    {formatDate(pr.updated_at)}
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
