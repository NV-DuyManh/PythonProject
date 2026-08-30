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
} from 'lucide-react';

export function Overview() {
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setLoading(true);
    setError(null);
    CodeGateAPI.getOverview()
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="skeleton skeleton--hero" />
        <div className="dashboard-grid dashboard-grid--stats">
          <div className="skeleton skeleton--stat" />
          <div className="skeleton skeleton--stat" />
          <div className="skeleton skeleton--stat" />
          <div className="skeleton skeleton--stat" />
        </div>
        <div className="dashboard-grid dashboard-grid--charts">
          <div className="skeleton skeleton--panel" />
          <div className="skeleton skeleton--panel" />
          <div className="skeleton skeleton--panel" />
        </div>
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

  const d = data!;

  return (
    <div className="dashboard-page">
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">CODEGATE ANALYTICS</p>
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
              {d.average_quality_score !== null ? d.average_quality_score.toFixed(1) : '—'}
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
              {d.average_risk_score !== null ? d.average_risk_score.toFixed(1) : '—'}
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
            <div className="stat-card__value">{d.open_pull_requests}</div>
            <div className="stat-card__note">{d.pull_requests_total} total analyzed</div>
          </div>
        </div>

        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon">
            <FileCheck size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Changed Coverage</div>
            <div className="stat-card__value">
              {d.average_changed_line_coverage !== null
                ? `${d.average_changed_line_coverage.toFixed(1)}%`
                : '—'}
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
              {d.policy_block_rate !== null ? `${d.policy_block_rate.toFixed(1)}%` : '—'}
            </div>
            <div className="stat-card__note">{d.policy_block_count} blocked PRs</div>
          </div>
        </div>

        <div className="stat-card stat-card--green">
          <div className="stat-card__icon">
            <CheckCircle size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Test Pass Rate</div>
            <div className="stat-card__value">
              {d.test_pass_rate !== null ? `${d.test_pass_rate.toFixed(1)}%` : '—'}
            </div>
            <div className="stat-card__note">{d.tests_passed_runs + d.tests_failed_runs} test runs</div>
          </div>
        </div>

        <div className="stat-card stat-card--indigo">
          <div className="stat-card__icon">
            <ShieldCheck size={28} strokeWidth={1.8} />
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Policy Pass Rate</div>
            <div className="stat-card__value">
              {d.policy_pass_rate !== null ? `${d.policy_pass_rate.toFixed(1)}%` : '—'}
            </div>
            <div className="stat-card__note">{d.policy_pass_count} passed</div>
          </div>
        </div>
      </div>

      {/* CHART ROW: 1.2fr 1.2fr 1fr */}
      <div className="dashboard-grid dashboard-grid--charts">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Quality Grade Distribution</div>
          </div>
          <div className="dashboard-panel__body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cg-muted)', fontSize: '13px' }}>
            {d.analyses_total === 0 ? 'No analysis data yet' : 'Quality grades chart'}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Risk Level Distribution</div>
          </div>
          <div className="dashboard-panel__body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cg-muted)', fontSize: '13px' }}>
            {d.analyses_total === 0 ? 'No analysis data yet' : 'Risk levels chart'}
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
                <div className="metric-block__value">{d.policy_pass_count}</div>
              </div>
              <div className="metric-block metric-block--amber">
                <div className="metric-block__label">WARNING</div>
                <div className="metric-block__value">{d.policy_warning_count}</div>
              </div>
              <div className="metric-block metric-block--red">
                <div className="metric-block__label">BLOCK</div>
                <div className="metric-block__value">{d.policy_block_count}</div>
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
          <div className="dashboard-panel__body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cg-muted)', fontSize: '13px', minHeight: '180px' }}>
            {d.quality_trend.length === 0 ? 'No trend data available' : 'Quality/Risk trend chart'}
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
                {d.test_pass_rate !== null ? `${d.test_pass_rate.toFixed(1)}%` : '—'}
              </div>
            </div>
            <div className="metric-block metric-block--blue">
              <div className="metric-block__label">Avg Changed Coverage</div>
              <div className="metric-block__value">
                {d.average_changed_line_coverage !== null
                  ? `${d.average_changed_line_coverage.toFixed(1)}%`
                  : '—'}
              </div>
            </div>
            <div className="metric-block metric-block--red">
              <div className="metric-block__label">Failed Test Runs</div>
              <div className="metric-block__value">{d.tests_failed_runs}</div>
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
          <div className="dashboard-panel__body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--cg-muted)', fontSize: '13px', minHeight: '140px' }}>
            {d.changed_coverage_trend.length === 0 ? 'No coverage data yet' : 'Coverage trend chart'}
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
              <div className="alert-card__value" style={{ color: 'var(--cg-red)' }}>{d.critical_findings}</div>
            </div>
            <div className="alert-card alert-card--amber">
              <div className="alert-card__icon alert-card__icon--amber">
                <AlertTriangle size={20} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Blocked Pull Requests</h4>
                <p>Require attention before merge</p>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-amber)' }}>{d.policy_block_count}</div>
            </div>
            <div className="alert-card alert-card--green">
              <div className="alert-card__icon alert-card__icon--green">
                <CheckCircle size={20} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Healthy PRs</h4>
                <p>Passed policy evaluation</p>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-green)' }}>{d.policy_pass_count}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
