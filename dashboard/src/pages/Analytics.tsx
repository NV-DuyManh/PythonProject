import { useEffect, useState } from 'react';
import { RefreshCw, ChartNoAxesCombined } from 'lucide-react';
import { CodeGateAPI } from '../api/client';
import type { DashboardOverviewResponse } from '../types';
import { ErrorState } from '../components/ui/ErrorState';
import { EmptyState } from '../components/ui/EmptyState';
import { Skeleton } from '../components/ui/Skeleton';
import { PageHeader } from '../components/ui/PageHeader';
import { TrendChart, DistributionChart, PolicyTrendChart, SingleMetricTrendChart } from '../charts/DashboardCharts';
import { formatPercentage, formatScore } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';

export function Analytics() {
  const { workspaceVersion } = useAuth();
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [prs, setPrs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      CodeGateAPI.getOverview(),
      CodeGateAPI.getPullRequests().catch(() => [])
    ]).then(([overviewData, prsData]) => {
      setData(overviewData);
      setPrs(prsData || []);
    }).catch(err => setError(err.message)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [workspaceVersion]);

  const header = (
    <PageHeader
      title="Analytics"
      description="Historical code health, risk evolution, and policy performance across all repositories."
      actions={
        <button className="btn-secondary" onClick={load} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'spin' : ''} />Refresh
        </button>
      }
    />
  );

  if (loading) {
    return (
      <div className="page-stack animate-pulse">
        {header}
        <Skeleton className="h-28 w-full rounded-2xl" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-stack">
        {header}
        <ErrorState title="Unable to load analytics" description={error} onRetry={load} />
      </div>
    );
  }

  if (!data || data.analyses_total === 0) {
    return (
      <div className="page-stack">
        {header}
        <EmptyState
          icon={ChartNoAxesCombined}
          image="/mascot/mascot-empty.jpg"
          title="No analytics yet"
          description="Analyze a pull request to see recorded quality, risk and policy results."
        />
      </div>
    );
  }

  const d = data;

  return (
    <div className="page-stack">
      {header}

      <dl className="metric-strip">
        <div>
          <dt className="flex items-center justify-between">
            <span>Average quality</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700">All Time</span>
          </dt>
          <dd className="text-indigo-600">{formatScore(d.average_quality_score)}</dd>
          <small>{d.analyses_completed ?? 'N/A'} completed analyses</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Average risk</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-700">Safety</span>
          </dt>
          <dd className={(d.average_risk_score ?? 0) > 50 ? 'text-amber-600' : 'text-slate-800'}>
            {formatScore(d.average_risk_score)}
          </dd>
          <small>Lower is better</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Policy pass rate</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700">Compliance</span>
          </dt>
          <dd className="text-emerald-600">{formatPercentage(d.policy_pass_rate)}</dd>
          <small>{d.policy_pass_count} passed evaluations</small>
        </div>

        <div>
          <dt className="flex items-center justify-between">
            <span>Changed coverage</span>
            <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700">Verification</span>
          </dt>
          <dd className="text-blue-600">{formatPercentage(d.average_changed_line_coverage)}</dd>
          <small>Recorded coverage evidence</small>
        </div>
      </dl>

      <div className="dashboard-grid dashboard-grid--charts">
        <SingleMetricTrendChart
          title="Quality history"
          metricName="Quality"
          metricKey="quality"
          metricColor="#6366f1"
          gradientId="analyticsQualityGradient"
          prs={prs || []}
          trendPoints={d.quality_trend || []}
        />
        <SingleMetricTrendChart
          title="Risk history"
          metricName="Risk"
          metricKey="risk"
          metricColor="#f59e0b"
          gradientId="analyticsRiskGradient"
          prs={prs || []}
          trendPoints={d.risk_trend || []}
        />
      </div>

      <div className="dashboard-grid dashboard-grid--bottom mt-6">
        <PolicyTrendChart data={d.policy_trend || []} />
        <TrendChart title="Changed-code coverage" series={[{ name: 'Coverage %', color: 'var(--cg-primary)', points: d.changed_coverage_trend || [] }]} />
      </div>

      <div className="dashboard-grid dashboard-grid--charts mt-6">
        <DistributionChart title="Quality grades" values={d.quality_grade_distribution || {}} />
        <DistributionChart title="Risk levels" values={d.risk_level_distribution || {}} colors={{ LOW: 'var(--cg-green)', MEDIUM: 'var(--cg-amber)', HIGH: 'var(--cg-red)', CRITICAL: 'var(--cg-red)' }} />
      </div>

      <section className="dashboard-panel">
        <div className="section-heading">
          <h2>Evidence summary</h2>
        </div>
        <div className="table-wrapper">
          <table className="cg-table">
            <thead>
              <tr>
                <th>Evidence</th>
                <th>Recorded value</th>
                <th>Context</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Analyses</td>
                <td className="font-bold text-[var(--cg-text)]">{d.analyses_completed} completed / {d.analyses_failed} failed</td>
                <td className="text-[var(--cg-muted)]">{d.analyses_total} total</td>
              </tr>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Test pass rate</td>
                <td className="font-bold text-emerald-600">{formatPercentage(d.test_pass_rate)}</td>
                <td className="text-[var(--cg-muted)]">{d.tests_passed_runs} passed / {d.tests_failed_runs} failed runs{d.tests_passed_runs === 0 && d.tests_failed_runs === 0 ? ' (no results recorded)' : ''}</td>
              </tr>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Line coverage</td>
                <td className="font-bold font-mono text-[var(--cg-text)]">{formatPercentage(d.average_line_coverage)}</td>
                <td className="text-[var(--cg-muted)]">Average recorded coverage</td>
              </tr>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Policy block rate</td>
                <td className="font-bold text-rose-600">{formatPercentage(d.policy_block_rate)}</td>
                <td className="text-[var(--cg-muted)]">{d.policy_block_count} blocked evaluations</td>
              </tr>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Findings</td>
                <td className="font-bold text-[var(--cg-text)]">{d.critical_findings} critical / {d.high_findings} high</td>
                <td className="text-[var(--cg-muted)]">{d.high_security_findings ?? 'N/A'} high security findings</td>
              </tr>
              <tr>
                <td className="font-semibold text-[var(--cg-text)]">Reviewer recommendations</td>
                <td className="font-bold text-[var(--cg-text)]">{d.reviewer_recommendations_generated ?? 'N/A'}</td>
                <td className="text-[var(--cg-muted)]">Generated recommendations</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
