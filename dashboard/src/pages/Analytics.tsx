import { useEffect, useState } from 'react';
import { CodeGateAPI } from '../api/client';
import type { DashboardOverviewResponse } from '../types';
import {
  RefreshCw,
  ShieldCheck,
  ShieldX,
  CheckCircle,
  FileCheck,
  Bug,
  Users,
} from 'lucide-react';
import { ErrorState } from '../components/ui/ErrorState';
import { formatPercentage, formatScore } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';

export function Analytics() {
  const { workspaceVersion } = useAuth();
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

  useEffect(() => { load(); }, [workspaceVersion]);

  if (loading) {
    return (
      <div>
        <div className="skeleton skeleton--hero" />
        <div className="dashboard-grid dashboard-grid--stats">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton skeleton--stat" />)}
        </div>
        <div className="dashboard-grid dashboard-grid--bottom">
          <div className="skeleton skeleton--panel" />
          <div className="skeleton skeleton--panel" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <ErrorState onRetry={load} description={error} title="Unable to load analytics" />
      </div>
    );
  }

  const d = data!;

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">INTELLIGENCE</p>
          <h2 className="page-hero__title">Engineering Analytics</h2>
          <p className="page-hero__desc">
            Understand quality, risk and review trends over time.
          </p>
        </div>
        <div className="page-hero__actions">
          <button className="btn-primary" onClick={load}>
            <RefreshCw size={15} strokeWidth={2} /> Refresh Data
          </button>
        </div>
      </div>

      {/* FILTER */}
      <div className="filter-card">
        <div className="filter-card__info">
          <div className="filter-card__label">ANALYTICS FILTER</div>
          <h3>All Time</h3>
          <div className="filter-card__desc">Aggregated metrics across all repositories and pull requests.</div>
        </div>
        <div className="filter-card__controls">
          <select defaultValue="all">
            <option value="all">All Repositories</option>
          </select>
          <select defaultValue="all">
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* KPI */}
      <div className="dashboard-grid dashboard-grid--stats">
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon"><ShieldCheck size={28} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Quality</div>
            <div className="stat-card__value">{formatScore(d.average_quality_score)}</div>
          </div>
        </div>
        <div className="stat-card stat-card--amber">
          <div className="stat-card__icon"><ShieldX size={28} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Risk</div>
            <div className="stat-card__value">{formatScore(d.average_risk_score)}</div>
          </div>
        </div>
        <div className="stat-card stat-card--indigo">
          <div className="stat-card__icon"><CheckCircle size={28} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Pass Rate</div>
            <div className="stat-card__value">{formatPercentage(d.policy_pass_rate)}</div>
          </div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon"><FileCheck size={28} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Changed Coverage</div>
            <div className="stat-card__value">{formatPercentage(d.average_changed_line_coverage)}</div>
          </div>
        </div>
      </div>

      {/* QUALITY SECTION */}
      <div className="dashboard-grid dashboard-grid--analytics">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Quality Overview</div>
          </div>
          <div className="dashboard-panel__body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div className="metric-block metric-block--green">
                <div className="metric-block__label">Avg Score</div>
                <div className="metric-block__value">{formatScore(d.average_quality_score)}</div>
              </div>
              <div className="metric-block metric-block--indigo">
                <div className="metric-block__label">Total Analyses</div>
                <div className="metric-block__value">{d.analyses_completed ?? 0}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Risk Overview</div>
          </div>
          <div className="dashboard-panel__body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div className="metric-block metric-block--amber">
                <div className="metric-block__label">Avg Risk</div>
                <div className="metric-block__value">{formatScore(d.average_risk_score)}</div>
              </div>
              <div className="metric-block metric-block--red">
                <div className="metric-block__label">Block Rate</div>
                <div className="metric-block__value">{formatPercentage(d.policy_block_rate)}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* POLICY */}
      <div className="dashboard-grid dashboard-grid--charts">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Policy Distribution</div>
          </div>
          <div className="dashboard-panel__body">
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
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Testing</div>
          </div>
          <div className="dashboard-panel__body">
            <div className="metric-block metric-block--green">
              <div className="metric-block__label">Test Pass Rate</div>
              <div className="metric-block__value">{formatPercentage(d.test_pass_rate)}</div>
            </div>
            <div className="metric-block metric-block--blue">
              <div className="metric-block__label">Changed Coverage</div>
              <div className="metric-block__value">{formatPercentage(d.average_changed_line_coverage)}</div>
            </div>
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Security</div>
          </div>
          <div className="dashboard-panel__body">
            <div className="alert-card alert-card--red">
              <div className="alert-card__icon alert-card__icon--red">
                <Bug size={18} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>Critical Findings</h4>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-red)' }}>{d.critical_findings ?? 0}</div>
            </div>
            <div className="alert-card alert-card--amber">
              <div className="alert-card__icon alert-card__icon--amber">
                <ShieldX size={18} strokeWidth={1.8} />
              </div>
              <div className="alert-card__body">
                <h4>High Findings</h4>
              </div>
              <div className="alert-card__value" style={{ color: 'var(--cg-amber)' }}>{d.high_findings ?? 0}</div>
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">
              <Users size={18} strokeWidth={1.8} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
              Reviewer Recommendations
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="metric-block metric-block--indigo">
              <div className="metric-block__label">Generated Recommendations</div>
              <div className="metric-block__value">{d.reviewer_recommendations_generated ?? 0}</div>
              <div className="metric-block__note">AI-powered reviewer matches</div>
            </div>
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">
              <ShieldX size={18} strokeWidth={1.8} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
              Risk Summary
            </div>
          </div>
          <div className="dashboard-panel__body">
            <div className="metric-block metric-block--red">
              <div className="metric-block__label">Blocked PRs</div>
              <div className="metric-block__value">{d.policy_block_count ?? 0}</div>
            </div>
            <div className="metric-block metric-block--green">
              <div className="metric-block__label">Healthy PRs</div>
              <div className="metric-block__value">{d.policy_pass_count ?? 0}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
