import { useEffect, useState } from 'react';
import { CodeGateAPI } from '../api/client';
import type { DashboardOverviewResponse } from '../types';
import {
  ShieldCheck,
  AlertTriangle,
  GitPullRequest,
  FileCheck,
  ShieldX,
  CheckCircle,
  RefreshCw,
  LayoutDashboard
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Cell, Legend
} from 'recharts';
import { formatPercentage, formatScore } from '../lib/utils';
import { ErrorState } from '../components/ui/ErrorState';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useAuth } from '../contexts/AuthContext';

export function Overview() {
  const { workspaceVersion } = useAuth();
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getOverview()
      .then((overview) => {
        setData(overview);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [workspaceVersion]);

  if (loading) {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="w-full h-[200px] rounded-[22px]" />
        <div className="dashboard-grid dashboard-grid--stats">
          <Skeleton className="w-full h-[120px] rounded-[22px]" />
          <Skeleton className="w-full h-[120px] rounded-[22px]" />
          <Skeleton className="w-full h-[120px] rounded-[22px]" />
          <Skeleton className="w-full h-[120px] rounded-[22px]" />
        </div>
        <div className="dashboard-grid dashboard-grid--charts">
          <Skeleton className="w-full h-[300px] rounded-[22px]" />
          <Skeleton className="w-full h-[300px] rounded-[22px]" />
          <Skeleton className="w-full h-[300px] rounded-[22px]" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 min-h-[500px]">
        <ErrorState onRetry={load} description={error} />
      </div>
    );
  }

  if (!data || data.analyses_total === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 min-h-[500px]">
        <EmptyState 
          icon={LayoutDashboard} 
          title="No analysis data yet" 
          description="Connect a repository or analyze a Pull Request to populate the dashboard." 
        />
      </div>
    );
  }

  const d = data;

  return (
    <div className="flex flex-col gap-6">
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <p className="page-hero__kicker">CODEGATE ANALYTICS</p>
          </div>
          <h2 className="page-hero__title">Engineering Health Overview</h2>
          <p className="page-hero__desc">
            Monitor pull request quality, risk, testing, security and merge readiness across connected repositories.
          </p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-primary" onClick={load}>
            <RefreshCw size={15} strokeWidth={2} /> Refresh Data
          </button>
        </div>
      </div>

      {/* FILTER CARD */}
      <div className="filter-card">
        <div className="filter-card__info">
          <div className="filter-card__label">ANALYTICS FILTER</div>
          <h3>All Time Overview</h3>
          <div className="filter-card__desc">
            Showing aggregated data from all analyzed pull requests.
          </div>
        </div>
        <div className="filter-card__controls">
          <select defaultValue="all">
            <option value="all">All Repositories</option>
          </select>
          <select defaultValue="all">
            <option value="all">All Time</option>
            <option value="month">This Month</option>
            <option value="week">This Week</option>
          </select>
        </div>
      </div>

      {/* KPI GRID — ROW 1 */}
      <div className="dashboard-grid dashboard-grid--stats">
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon">
            <ShieldCheck size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Average Quality</div>
            <div className="stat-card__value">
              {formatScore(d.average_quality_score)}
            </div>
            <div className="stat-card__note">out of 100</div>
          </div>
        </div>

        <div className="stat-card stat-card--amber">
          <div className="stat-card__icon">
            <AlertTriangle size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Average Risk</div>
            <div className="stat-card__value">
              {formatScore(d.average_risk_score)}
            </div>
            <div className="stat-card__note">lower is better</div>
          </div>
        </div>

        <div className="stat-card stat-card--indigo">
          <div className="stat-card__icon">
            <GitPullRequest size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Open Pull Requests</div>
            <div className="stat-card__value">{d.open_pull_requests ?? 0}</div>
            <div className="stat-card__note">{d.pull_requests_total ?? 0} total analyzed</div>
          </div>
        </div>

        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon">
            <FileCheck size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Changed Coverage</div>
            <div className="stat-card__value">
              {formatPercentage(d.average_changed_line_coverage)}
            </div>
            <div className="stat-card__note">across PRs</div>
          </div>
        </div>
      </div>

      {/* KPI GRID — ROW 2 */}
      <div className="dashboard-grid dashboard-grid--stats-2">
        <div className="stat-card stat-card--red">
          <div className="stat-card__icon">
            <ShieldX size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Policy Block Rate</div>
            <div className="stat-card__value">
              {formatPercentage(d.policy_block_rate)}
            </div>
            <div className="stat-card__note">{d.policy_block_count ?? 0} blocked PRs</div>
          </div>
        </div>

        <div className="stat-card stat-card--green">
          <div className="stat-card__icon">
            <CheckCircle size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Test Pass Rate</div>
            <div className="stat-card__value">
              {formatPercentage(d.test_pass_rate)}
            </div>
            <div className="stat-card__note">{(d.tests_passed_runs || 0) + (d.tests_failed_runs || 0)} test runs</div>
          </div>
        </div>

        <div className="stat-card stat-card--indigo">
          <div className="stat-card__icon">
            <ShieldCheck size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Policy Pass Rate</div>
            <div className="stat-card__value">
              {formatPercentage(d.policy_pass_rate)}
            </div>
            <div className="stat-card__note">{d.policy_pass_count ?? 0} passed</div>
          </div>
        </div>
      </div>

      {/* CHART ROW: 1.2fr 1.2fr 1fr */}
      <div className="dashboard-grid dashboard-grid--charts">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Quality Grade Distribution</div>
          </div>
          <div className="dashboard-panel__body" style={{ height: '220px', width: '100%' }}>
            {(!d.quality_grade_distribution || Object.keys(d.quality_grade_distribution).length === 0) ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--cg-muted)' }}>No distribution data</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={Object.entries(d.quality_grade_distribution).map(([k, v]) => ({ name: k, count: v }))} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--cg-border)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <Tooltip cursor={{ fill: 'var(--cg-bg-hover)' }} contentStyle={{ backgroundColor: 'var(--cg-bg-elevated)', borderColor: 'var(--cg-border)', borderRadius: '6px' }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {Object.entries(d.quality_grade_distribution).map(([k]) => (
                      <Cell key={k} fill={k === 'A' ? 'var(--cg-green)' : k === 'B' ? 'var(--cg-green-muted)' : k === 'C' ? 'var(--cg-amber)' : 'var(--cg-red)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Risk Level Distribution</div>
          </div>
          <div className="dashboard-panel__body" style={{ height: '220px', width: '100%' }}>
            {(!d.risk_level_distribution || Object.keys(d.risk_level_distribution).length === 0) ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--cg-muted)' }}>No distribution data</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={Object.entries(d.risk_level_distribution).map(([k, v]) => ({ name: k, count: v }))} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--cg-border)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <Tooltip cursor={{ fill: 'var(--cg-bg-hover)' }} contentStyle={{ backgroundColor: 'var(--cg-bg-elevated)', borderColor: 'var(--cg-border)', borderRadius: '6px' }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {Object.entries(d.risk_level_distribution).map(([k]) => (
                      <Cell key={k} fill={k === 'LOW' ? 'var(--cg-green)' : k === 'MEDIUM' ? 'var(--cg-amber)' : 'var(--cg-red)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Policy Decisions</div>
          </div>
          <div className="dashboard-panel__body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div className="metric-block metric-block--green">
                <div className="metric-block__label">PASS</div>
                <div className="metric-block__value">{d.policy_pass_count ?? 0}</div>
              </div>
              <div className="metric-block metric-block--amber">
                <div className="metric-block__label">WARNING</div>
                <div className="metric-block__value">{d.policy_warning_count ?? 0}</div>
              </div>
              <div className="metric-block metric-block--red">
                <div className="metric-block__label">BLOCK</div>
                <div className="metric-block__value">{d.policy_block_count ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ANALYTICS ROW: 2fr 1fr */}
      <div className="dashboard-grid dashboard-grid--analytics">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Quality & Risk Trend</div>
            <div className="dashboard-panel__meta">Recent PRs</div>
          </div>
          <div className="dashboard-panel__body" style={{ height: '220px', width: '100%' }}>
            {(!d.quality_trend || d.quality_trend.length === 0) ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--cg-muted)' }}>No trend data available</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={d.quality_trend.map((q, i) => ({ pr: q.date, quality: q.value, risk: d.risk_trend?.[i]?.value }))} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--cg-border)" />
                  <XAxis dataKey="pr" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--cg-bg-elevated)', borderColor: 'var(--cg-border)', borderRadius: '6px' }} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                  <Line type="monotone" dataKey="quality" stroke="var(--cg-green)" strokeWidth={2} dot={false} activeDot={{ r: 6 }} name="Quality Score" />
                  <Line type="monotone" dataKey="risk" stroke="var(--cg-amber)" strokeWidth={2} dot={false} activeDot={{ r: 6 }} name="Risk Score" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Testing Summary</div>
          </div>
          <div className="dashboard-panel__body">
            <div className="metric-block metric-block--green">
              <div className="metric-block__label">Test Pass Rate</div>
              <div className="metric-block__value">
                {formatPercentage(d.test_pass_rate)}
              </div>
            </div>
            <div className="metric-block metric-block--blue">
              <div className="metric-block__label">Avg Changed Coverage</div>
              <div className="metric-block__value">
                {formatPercentage(d.average_changed_line_coverage)}
              </div>
            </div>
            <div className="metric-block metric-block--red">
              <div className="metric-block__label">Failed Test Runs</div>
              <div className="metric-block__value">{d.tests_failed_runs ?? 0}</div>
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM ROW: 1fr 1fr */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Coverage Trend</div>
            <div className="dashboard-panel__meta">Changed-code coverage</div>
          </div>
          <div className="dashboard-panel__body" style={{ height: '140px', width: '100%' }}>
            {(!d.changed_coverage_trend || d.changed_coverage_trend.length === 0) ? (
               <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--cg-muted)', fontSize: '13px' }}>
                 No coverage data yet
               </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={d.changed_coverage_trend} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--cg-border)" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)' }} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--cg-bg-elevated)', borderColor: 'var(--cg-border)', borderRadius: '6px' }} />
                  <Line type="monotone" dataKey="value" stroke="var(--cg-blue)" strokeWidth={2} dot={false} activeDot={{ r: 6 }} name="Coverage %" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Security & Merge Alerts</div>
          </div>
          <div className="dashboard-panel__body">
            <div className="alert-card alert-card--red">
              <div className="alert-card__icon alert-card__icon--red">
                <ShieldX size={20} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Critical Security Findings</h4>
                <p>High-severity issues detected</p>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-red)' }}>{d.critical_findings ?? 0}</div>
            </div>
            <div className="alert-card alert-card--amber">
              <div className="alert-card__icon alert-card__icon--amber">
                <AlertTriangle size={20} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Blocked Pull Requests</h4>
                <p>Require attention before merge</p>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-amber)' }}>{d.policy_block_count ?? 0}</div>
            </div>
            <div className="alert-card alert-card--green">
              <div className="alert-card__icon alert-card__icon--green">
                <CheckCircle size={20} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Healthy PRs</h4>
                <p>Passed policy evaluation</p>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-green)' }}>{d.policy_pass_count ?? 0}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
