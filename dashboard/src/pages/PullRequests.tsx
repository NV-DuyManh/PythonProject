import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { PRDashboardItem } from '../types';
import { GitPullRequest, RefreshCw, AlertTriangle, Search } from 'lucide-react';

function policyBadgeClass(decision: string | null): string {
  if (!decision) return 'badge badge--gray';
  switch (decision.toUpperCase()) {
    case 'PASS': return 'badge badge--pass';
    case 'WARNING': return 'badge badge--warning';
    case 'BLOCK': return 'badge badge--block';
    default: return 'badge badge--gray';
  }
}

function qualityBadgeClass(grade: string | null): string {
  if (!grade) return 'badge badge--gray';
  switch (grade.toUpperCase()) {
    case 'A': return 'badge badge--grade-a';
    case 'B': return 'badge badge--grade-b';
    case 'C': return 'badge badge--grade-c';
    case 'D': return 'badge badge--grade-d';
    case 'F': return 'badge badge--grade-f';
    default: return 'badge badge--gray';
  }
}

function riskBadgeClass(level: string | null): string {
  if (!level) return 'badge badge--gray';
  switch (level.toUpperCase()) {
    case 'LOW': return 'badge badge--green';
    case 'MEDIUM': return 'badge badge--amber';
    case 'HIGH': return 'badge badge--red';
    case 'CRITICAL': return 'badge badge--red';
    default: return 'badge badge--gray';
  }
}

export function PullRequests() {
  const [data, setData] = useState<PRDashboardItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getPullRequests()
      .then(setData)
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
          <p className="page-hero__kicker">CODE REVIEW</p>
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
        <div className="empty-state">
          <GitPullRequest size={56} strokeWidth={1.2} className="empty-state__icon" />
          <div className="empty-state__title">No pull requests yet</div>
          <div className="empty-state__desc">
            Pull requests will appear here after CodeGate receives a GitHub webhook or an analysis is created.
          </div>
          <div className="empty-state__steps">
            <div className="empty-state__step">
              <span className="empty-state__step-num">1</span>
              Connect repository
            </div>
            <div className="empty-state__step">
              <span className="empty-state__step-num">2</span>
              Open or synchronize a pull request
            </div>
            <div className="empty-state__step">
              <span className="empty-state__step-num">3</span>
              Run CodeGate analysis
            </div>
          </div>
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
                    <Link to={`/pull-requests/${pr.pull_request_id}`} className="cell-link">
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
                      <>
                        <span className={qualityBadgeClass(pr.quality_grade)}>{pr.quality_grade}</span>
                        <span className="cell-muted" style={{ marginLeft: '6px' }}>{pr.quality_score.toFixed(0)}</span>
                      </>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td>
                    {pr.risk_level ? (
                      <span className={riskBadgeClass(pr.risk_level)}>{pr.risk_level}</span>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td>
                    <span className={policyBadgeClass(pr.policy_decision)}>
                      {pr.policy_decision || '—'}
                    </span>
                  </td>
                  <td>
                    {pr.test_outcome ? (
                      <span className={`badge ${pr.test_outcome === 'PASSED' ? 'badge--green' : pr.test_outcome === 'FAILED' ? 'badge--red' : 'badge--gray'}`}>
                        {pr.test_outcome}
                      </span>
                    ) : (
                      <span className="cell-muted">—</span>
                    )}
                  </td>
                  <td>
                    {pr.changed_line_coverage !== null
                      ? `${pr.changed_line_coverage.toFixed(1)}%`
                      : <span className="cell-muted">—</span>}
                  </td>
                  <td>
                    {(pr.critical_findings + pr.high_findings) > 0 ? (
                      <span className="badge badge--red">
                        {pr.critical_findings + pr.high_findings}
                      </span>
                    ) : (
                      <span className="cell-muted">0</span>
                    )}
                  </td>
                  <td className="cell-muted">
                    {new Date(pr.updated_at).toLocaleDateString()}
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
