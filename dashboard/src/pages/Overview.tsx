import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw, LayoutDashboard, Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';
import type { DashboardOverviewResponse, PRDashboardItem, RepositoryDashboardItem } from '../types';
import { CodeGateAPI } from '../api/client';
import { formatPercentage, formatScore } from '../lib/utils';
import { ErrorState } from '../components/ui/ErrorState';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { PageHeader } from '../components/ui/PageHeader';
import { Badge } from '../components/ui/Badge';
import { PolicyBadge } from '../components/PolicyBadge';
import { PolicyDonutChart, QualityRiskTrendChart } from '../charts/DashboardCharts';
import { useAuth } from '../contexts/AuthContext';

export function Overview() {
  const { workspaceVersion, activeWorkspace, loading: authLoading } = useAuth();
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prs, setPrs] = useState<PRDashboardItem[] | null>(null);
  const [repos, setRepos] = useState<RepositoryDashboardItem[] | null>(null);
  const [queueLoading, setQueueLoading] = useState(true);

  useEffect(() => {
    if (authLoading || !activeWorkspace) return;
    let cancelled = false;
    const fetchOverview = async (retries = 3, delay = import.meta.env.MODE === 'test' ? 0 : 800) => {
      setLoading(true);
      setError(null);
      for (let attempt = 0; attempt < retries; attempt++) {
        try {
          const overview = await CodeGateAPI.getOverview();
          if (!cancelled) { setData(overview); setError(null); setLoading(false); }
          return;
        } catch (err: unknown) {
          if (attempt === retries - 1 && !cancelled) {
            setError(err instanceof Error ? err.message : 'Failed to fetch overview');
            setLoading(false);
          } else { await new Promise(r => setTimeout(r, delay)); }
        }
      }
    };
    fetchOverview();
    return () => { cancelled = true; };
  }, [workspaceVersion, authLoading, activeWorkspace?.id]);

  useEffect(() => {
    if (authLoading || !activeWorkspace) return;
    let cancelled = false;
    setQueueLoading(true);
    setPrs(null);
    setRepos(null);
    Promise.allSettled([CodeGateAPI.getPullRequests(), CodeGateAPI.getRepositories()]).then(([pullRequests, repositories]) => {
      if (cancelled) return;
      if (pullRequests.status === 'fulfilled') setPrs(pullRequests.value);
      if (repositories.status === 'fulfilled') setRepos(repositories.value);
      setQueueLoading(false);
    });
    return () => { cancelled = true; };
  }, [workspaceVersion, authLoading, activeWorkspace?.id]);

  const header = <PageHeader title="Dashboard" description="All repositories · All time" actions={
    <button className="btn-secondary" onClick={() => window.location.reload()}><RefreshCw size={16} />Refresh</button>
  } />;

  if (loading) {
    return (
      <div className="page-stack">
        {header}
        <div className="animate-pulse space-y-4">
          <Skeleton className="h-24 w-full rounded-2xl" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-28 w-full rounded-2xl" />
            ))}
          </div>
          <Skeleton className="h-64 w-full rounded-2xl" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-stack">
        {header}
        <ErrorState title="Unable to load data" onRetry={() => window.location.reload()} description={error} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-stack">
        {header}
        <EmptyState
          icon={LayoutDashboard}
          title="No analysis data yet"
          description="Connect a repository or analyze a Pull Request to populate the dashboard."
        />
      </div>
    );
  }

  const d = data;
  const attention = prs?.filter(pr => ['WARNING', 'BLOCK'].includes(pr.policy_decision || '') || ['FAILED', 'RUNNING', 'QUEUED'].includes(pr.analysis_status || ''));

  return (
    <div className="page-stack">
      {header}

      {/* Anteater Coach Briefing Banner */}
      <div className="coach-banner">
        <img
          src="/mascot/mascot-inspect.jpg"
          alt="Anteater Coach"
          className="coach-banner__mascot"
        />
        <div className="coach-banner__content">
          <div className="coach-banner__title">
            <span>Anteater Code Coach</span>
            <span className="coach-banner__badge">Learning & Review System</span>
          </div>
          <p className="coach-banner__desc">
            {d.analyses_total === 0
              ? "Welcome to CodeGate! Connect your GitHub repository to kick off automated PR reviews and unlock interactive coding lessons."
              : (d.average_quality_score ?? 0) >= 80
              ? "Outstanding performance! Your codebase is adhering to clean architectural practices. Continue maintaining high test coverage on incoming PRs."
              : "Keep pushing! Some pull requests have identified policy warnings or test gaps. Review the interactive lesson cards in your PR queue to boost scores."}
          </p>
        </div>
        <div className="coach-banner__actions">
          {d.analyses_total === 0 ? (
            <Link to="/integrations/github" className="btn-primary text-xs py-2 px-3">
              <Sparkles size={14} /> Connect GitHub
            </Link>
          ) : (
            <Link to="/pull-requests" className="btn-secondary text-xs py-2 px-3">
              Review PRs <ArrowRight size={14} />
            </Link>
          )}
        </div>
      </div>

      {/* KPI Metric Strip */}
      <dl className="metric-strip">
        <div className="relative overflow-hidden">
          <dt className="flex items-center justify-between">
            <span>Average quality</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[var(--cg-primary-light)] text-[var(--cg-primary)]">Health</span>
          </dt>
          <dd className="text-indigo-500">{formatScore(d.average_quality_score)}</dd>
          <small>Score out of 100</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Average risk</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[var(--cg-amber-bg)] text-amber-600 dark:text-amber-400">Safety</span>
          </dt>
          <dd className={(d.average_risk_score ?? 0) > 50 ? 'text-amber-500' : 'text-[var(--cg-text)]'}>
            {formatScore(d.average_risk_score)}
          </dd>
          <small>Lower is better</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Open pull requests</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[var(--cg-surface-soft)] text-[var(--cg-text-secondary)] border border-[var(--cg-border-soft)]">Queue</span>
          </dt>
          <dd>{d.open_pull_requests ?? 'N/A'}</dd>
          <small>{d.pull_requests_total ?? 'N/A'} pull requests in workspace</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Policy block rate</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-[var(--cg-red-bg)] text-[var(--cg-red)]">Enforcement</span>
          </dt>
          <dd className={(d.policy_block_rate ?? 0) > 0 ? 'text-rose-500' : 'text-emerald-500'}>
            {formatPercentage(d.policy_block_rate)}
          </dd>
          <small>{d.policy_block_count ?? 'N/A'} blocked evaluations</small>
        </div>
      </dl>

      {d.analyses_total === 0 && (
        <EmptyState
          icon={LayoutDashboard}
          title="No analysis data yet"
          description="Connect a repository or analyze a Pull Request to populate the dashboard."
        >
          <Link className="btn-primary" to="/integrations/github">
            <Sparkles size={16} /> Connect GitHub
          </Link>
        </EmptyState>
      )}

      {/* Analytics Charts */}
      <div className="dashboard-grid dashboard-grid--analytics">
        <QualityRiskTrendChart
          title="Quality & risk"
          prs={prs || []}
          qualityTrend={d.quality_trend || []}
          riskTrend={d.risk_trend || []}
        />
        <PolicyDonutChart
          title="Policy decisions"
          values={
            d.policy_decision_distribution || {
              PASS: d.policy_pass_count,
              WARNING: d.policy_warning_count,
              BLOCK: d.policy_block_count,
            }
          }
          colors={{ PASS: '#10b981', WARNING: '#f59e0b', BLOCK: '#ef4444' }}
        />
      </div>

      {/* Needs Attention Queue */}
      <section>
        <div className="section-heading">
          <div className="flex items-center gap-2">
            <h2>Needs attention</h2>
            {attention && attention.length > 0 && (
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[var(--cg-amber-bg)] text-amber-600 dark:text-amber-400">
                {attention.length}
              </span>
            )}
          </div>
          <Link className="text-link" to="/pull-requests">View pull requests</Link>
        </div>

        {queueLoading ? (
          <Skeleton className="h-32 w-full rounded-2xl" />
        ) : !attention ? (
          <p className="alert">Pull requests are unavailable. Refresh to try again.</p>
        ) : attention.length === 0 ? (
          <div className="p-6 rounded-2xl bg-[var(--cg-surface)] border border-[var(--cg-border)] text-center flex flex-col items-center gap-2">
            <CheckCircle2 size={32} className="text-emerald-500" />
            <p className="font-semibold text-[var(--cg-text)]">All clear! No pending blockers or failed analyses.</p>
            <p className="text-xs text-[var(--cg-muted)]">All recent pull requests are meeting quality guidelines.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="cg-table">
              <caption className="table-caption">From the latest pull requests returned by the API (up to 20).</caption>
              <thead>
                <tr>
                  <th>Pull request</th>
                  <th>Repository</th>
                  <th>Analysis</th>
                  <th>Policy</th>
                  <th className="numeric">Quality</th>
                  <th className="numeric">Risk</th>
                </tr>
              </thead>
              <tbody>
                {attention.map(pr => (
                  <tr key={pr.pull_request_id}>
                    <td className="cell-primary">
                      <Link className="cell-link" to={`/pull-requests/${pr.pull_request_id}`}>
                        {pr.title}
                      </Link>
                      <div className="cell-muted">#{pr.number} · {pr.author}</div>
                    </td>
                    <td>{pr.repository}</td>
                    <td>
                      <Badge
                        variant={
                          pr.analysis_status === 'FAILED'
                            ? 'danger'
                            : ['RUNNING', 'QUEUED'].includes(pr.analysis_status || '')
                            ? 'info'
                            : 'default'
                        }
                      >
                        {pr.analysis_status || 'Not run'}
                      </Badge>
                    </td>
                    <td><PolicyBadge decision={pr.policy_decision || ''} /></td>
                    <td className="numeric font-bold">{formatScore(pr.quality_score)}</td>
                    <td className="numeric font-bold">{formatScore(pr.risk_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Analysis & Testing Summary Grid */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <section className="dashboard-panel">
          <div className="section-heading">
            <h2>Analysis & testing</h2>
            <Link className="text-link" to="/analytics">Analytics</Link>
          </div>
          {[
            ['Completed analyses', d.analyses_completed ?? 'N/A'],
            ['Failed analyses', d.analyses_failed ?? 'N/A'],
            ['Test pass rate', formatPercentage(d.test_pass_rate)],
            ['Passed / failed test runs', `${d.tests_passed_runs ?? 'N/A'} / ${d.tests_failed_runs ?? 'N/A'}`],
            ['Changed coverage', formatPercentage(d.average_changed_line_coverage)],
            ['Critical / high findings', `${d.critical_findings ?? 'N/A'} / ${d.high_findings ?? 'N/A'}`],
          ].map(([label, value]) => (
            <div key={label} className="metric-block">
              <span className="metric-block__label">{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
          {d.tests_passed_runs === 0 && d.tests_failed_runs === 0 && (
            <p className="muted mt-3">No passed or failed test runs recorded.</p>
          )}
        </section>

        <section className="dashboard-panel">
          <div className="section-heading">
            <h2>Repository health</h2>
            <Link className="text-link" to="/repositories">View repositories</Link>
          </div>
          {queueLoading ? (
            <Skeleton className="h-32 w-full rounded-2xl" />
          ) : !repos ? (
            <p className="muted">Repository data unavailable. Refresh to try again.</p>
          ) : repos.length === 0 ? (
            <div className="text-center py-6">
              <p className="text-sm text-slate-500 mb-3">No repositories connected yet.</p>
              <Link className="btn-primary text-xs" to="/integrations/github">
                Connect a repository
              </Link>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>Repository</th>
                    <th>Quality</th>
                    <th>Warning / block</th>
                  </tr>
                </thead>
                <tbody>
                  {repos.map(repo => (
                    <tr key={repo.repository_id}>
                      <td>
                        <Link className="cell-link" to={`/repositories/${repo.repository_id}`}>
                          {repo.name}
                        </Link>
                      </td>
                      <td className="font-bold">{formatScore(repo.average_quality)}</td>
                      <td>{repo.policy_warning_count ?? 'N/A'} / {repo.policy_block_count ?? 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="muted mt-3">Loaded repositories; up to 20.</p>
        </section>
      </div>
    </div>
  );
}
