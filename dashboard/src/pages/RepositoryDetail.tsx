import { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useParams, Link } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Badge } from '../components/ui/Badge';
import { formatScore, formatPercentage, formatDate } from '../lib/utils';
import {
  GitBranch,
  ShieldCheck,
  ShieldAlert,
  Activity,
  Bug,
  Clock,
  TrendingUp,
  FileCheck,
  CheckCircle,
  AlertTriangle,
  ArrowLeft,
  FolderGit2,
} from 'lucide-react';
import { DistributionChart } from '../charts/DashboardCharts';
import { TestingConfiguration } from '../components/TestingConfiguration';

export function RepositoryDetail() {
  const { workspaceVersion } = useAuth();
  const { repositoryId } = useParams<{ repositoryId: string }>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!repositoryId) return;
    setLoading(true);
    setError(null);
    CodeGateAPI.getRepositoryDetail(parseInt(repositoryId, 10))
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [repositoryId]);

  useEffect(() => { load(); }, [load, workspaceVersion]);

  if (loading) {
    return (
      <div className="page-stack animate-pulse">
        <div className="skeleton skeleton--hero" />
        <div className="dashboard-grid dashboard-grid--stats">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton skeleton--stat" />)}
        </div>
        <div className="skeleton skeleton--panel" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <ErrorState
          title="Unable to load repository"
          description={error || 'Repository not found'}
          onRetry={load}
        />
      </div>
    );
  }

  const { repository, health, policy_summary, testing_summary, coverage_summary, finding_summary, recent_prs } = data;

  return (
    <div className="page-stack">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs font-semibold text-[var(--cg-muted)]">
        <Link to="/repositories" className="hover:text-[var(--cg-primary)] flex items-center gap-1">
          <ArrowLeft size={14} /> Repositories
        </Link>
        <span>/</span>
        <span className="text-[var(--cg-text)] font-bold">Details</span>
      </div>

      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={repository.active ? 'success' : 'default'}>
              {repository.active ? 'Active Repository' : 'Inactive'}
            </Badge>
            <span className="text-xs font-semibold text-[var(--cg-text-secondary)] bg-[var(--cg-surface-soft)] border border-[var(--cg-border-soft)] px-2 py-0.5 rounded">
              {repository.provider}
            </span>
          </div>
          <h1 className="page-hero__title flex items-center gap-2.5">
            <FolderGit2 size={26} className="text-indigo-500" />
            {repository.name}
          </h1>
          <div className="page-hero__desc">
            {health?.last_analysis_at && (
              <span className="inline-flex items-center gap-1.5 text-xs text-[var(--cg-muted)]">
                <Clock size={13} className="text-indigo-500" />
                Last analyzed: {formatDate(health.last_analysis_at)}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* KPI CARDS */}
      <div className="dashboard-grid dashboard-grid--stats">
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon"><TrendingUp size={24} strokeWidth={2} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Quality</div>
            <div className="stat-card__value">{formatScore(health?.average_quality)}</div>
            <div className="stat-card__note">Out of 100</div>
          </div>
        </div>

        <div className="stat-card stat-card--amber">
          <div className="stat-card__icon"><ShieldAlert size={24} strokeWidth={2} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Risk</div>
            <div className="stat-card__value">{formatScore(health?.average_risk)}</div>
            <div className="stat-card__note">Risk index</div>
          </div>
        </div>

        <div className="stat-card stat-card--red">
          <div className="stat-card__icon"><AlertTriangle size={24} strokeWidth={2} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Block Rate</div>
            <div className="stat-card__value">{formatPercentage(policy_summary?.block_rate)}</div>
            <div className="stat-card__note">Policy blocks</div>
          </div>
        </div>

        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon"><FileCheck size={24} strokeWidth={2} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Changed Coverage</div>
            <div className="stat-card__value">{formatPercentage(coverage_summary?.average_changed_coverage)}</div>
            <div className="stat-card__note">PR code tested</div>
          </div>
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid--charts">
        <DistributionChart title="Quality grades" values={data.quality_distribution || {}} />
        <DistributionChart title="Risk levels" values={data.risk_distribution || {}} colors={{ LOW: 'var(--cg-green)', MEDIUM: 'var(--cg-amber)', HIGH: 'var(--cg-red)', CRITICAL: 'var(--cg-red)' }} />
        <DistributionChart title="Policy decisions" values={data.policy_distribution || {}} colors={{ PASS: 'var(--cg-green)', WARNING: 'var(--cg-amber)', BLOCK: 'var(--cg-red)' }} />
      </div>

      {/* HEALTH OVERVIEW */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title flex items-center gap-2">
              <Activity size={18} strokeWidth={2} className="text-indigo-600" />
              Engineering Health
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="evidence-grid">
              <div className="metric-block">
                <div className="metric-block__label">Open PRs</div>
                <div className="metric-block__value">{health?.open_pr_count ?? 0}</div>
              </div>
              <div className="metric-block">
                <div className="metric-block__label">Analyses</div>
                <div className="metric-block__value">{health?.analysis_count ?? 0}</div>
              </div>
              <div className="metric-block metric-block--green">
                <div className="metric-block__label">Completed</div>
                <div className="metric-block__value text-emerald-600">{health?.analyses_completed ?? 'N/A'}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title flex items-center gap-2">
              <ShieldCheck size={18} strokeWidth={2} className="text-emerald-600" />
              Policy Summary
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="evidence-grid">
              <div className="metric-block metric-block--green">
                <div className="metric-block__label">Pass</div>
                <div className="metric-block__value text-emerald-600">{policy_summary?.pass_count ?? 0}</div>
              </div>
              <div className="metric-block metric-block--amber">
                <div className="metric-block__label">Warning</div>
                <div className="metric-block__value text-amber-600">{policy_summary?.warning_count ?? 0}</div>
              </div>
              <div className="metric-block metric-block--red">
                <div className="metric-block__label">Block</div>
                <div className="metric-block__value text-rose-600">{policy_summary?.block_count ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* TESTS & FINDINGS */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title flex items-center gap-2">
              <CheckCircle size={18} strokeWidth={2} className="text-indigo-600" />
              Testing
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="metric-block">
              <div className="metric-block__label">Test Pass Rate</div>
              <div className="metric-block__value text-emerald-600">{formatPercentage(testing_summary?.test_pass_rate)}</div>
            </div>
          </div>
        </div>

        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title flex items-center gap-2">
              <Bug size={18} strokeWidth={2} className="text-rose-600" />
              Findings
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="evidence-grid">
              <div className="metric-block metric-block--red">
                <div className="metric-block__label">Critical</div>
                <div className="metric-block__value text-rose-600">{finding_summary?.critical ?? 0}</div>
              </div>
              <div className="metric-block metric-block--amber">
                <div className="metric-block__label">High</div>
                <div className="metric-block__value text-amber-600">{finding_summary?.high ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {repositoryId && <TestingConfiguration repositoryId={parseInt(repositoryId, 10)} />}

      {/* RECENT PULL REQUESTS */}
      <div className="dashboard-panel">
        <div className="dashboard-panel__head">
          <div className="dashboard-panel__title flex items-center gap-2">
            <GitBranch size={18} strokeWidth={2} className="text-indigo-600" />
            Recent Pull Requests
          </div>
          <div className="dashboard-panel__meta">{recent_prs?.length ?? 0} PRs</div>
        </div>
        <div className="dashboard-panel__body">
          {recent_prs && recent_prs.length > 0 ? (
            <div className="table-wrapper" style={{ boxShadow: 'none', border: '1px solid var(--cg-border)' }}>
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Title</th>
                    <th>Author</th>
                    <th>State</th>
                    <th>Quality</th>
                    <th>Risk</th>
                    <th>Policy</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {recent_prs.map((pr: any) => (
                    <tr key={pr.pull_request_id}>
                      <td className="font-bold text-indigo-600">
                        <Link to={`/pull-requests/${pr.pull_request_id}`} className="cell-link">
                          #{pr.number}
                        </Link>
                      </td>
                      <td className="cell-primary font-medium">
                        <Link to={`/pull-requests/${pr.pull_request_id}`} className="cell-link">
                          {pr.title?.length > 60 ? pr.title.substring(0, 60) + '…' : pr.title}
                        </Link>
                      </td>
                      <td className="cell-muted">{pr.author}</td>
                      <td>
                        <Badge variant={pr.state === 'OPEN' ? 'success' : pr.state === 'MERGED' ? 'indigo' : 'default'}>
                          {pr.state}
                        </Badge>
                      </td>
                      <td className="font-bold">{formatScore(pr.quality_score)}</td>
                      <td className="font-bold">{formatScore(pr.risk_score)}</td>
                      <td>
                        {pr.policy_decision ? (
                          <Badge variant={pr.policy_decision === 'PASS' ? 'success' : pr.policy_decision === 'WARNING' ? 'warning' : pr.policy_decision === 'BLOCK' ? 'danger' : 'default'}>
                            {pr.policy_decision}
                          </Badge>
                        ) : '—'}
                      </td>
                      <td className="cell-muted">{formatDate(pr.updated_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              icon={GitBranch}
              image="/mascot/mascot-empty.jpg"
              title="No pull requests"
              description="This repository has no pull requests yet. Create a pull request to see analysis data here."
            />
          )}
        </div>
      </div>
    </div>
  );
}
