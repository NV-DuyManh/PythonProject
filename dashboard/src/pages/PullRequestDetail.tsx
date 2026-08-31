import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { CodeGateAPI } from '../api/client';
import type { PullRequestDashboardDetail } from '../types';
import {
  ShieldCheck,
  ShieldAlert,
  ShieldX,
  CheckCircle,
  FileCheck,
  Bug,
  Users,
} from 'lucide-react';
import { ErrorState } from '../components/ui/ErrorState';
import { Badge } from '../components/ui/Badge';
import { formatPercentage, formatScore } from '../lib/utils';

export function PullRequestDetail() {
  const { pullRequestId } = useParams<{ pullRequestId: string }>();
  const [data, setData] = useState<PullRequestDashboardDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!pullRequestId) return;
    setLoading(true);
    setError(null);
    CodeGateAPI.getPullRequestDetail(parseInt(pullRequestId, 10))
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [pullRequestId]);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return (
      <div>
        <div className="skeleton skeleton--hero" />
        <div className="dashboard-grid dashboard-grid--5">
          {[...Array(5)].map((_, i) => <div key={i} className="skeleton skeleton--stat" />)}
        </div>
        <div className="skeleton skeleton--panel" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-8">
        <ErrorState 
          title="Unable to load pull request" 
          description={error || 'Pull request not found'} 
          onRetry={load} 
        />
      </div>
    );
  }

  const { pr, quality, risk, policy, tests, coverage, findings, reviewer_recommendation: reviewers } = data;
  const policyDecision = policy?.decision?.toUpperCase() || 'UNKNOWN';
  const decisionVariant = policyDecision === 'BLOCK' ? 'block' : policyDecision === 'WARNING' ? 'warning' : 'pass';

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">PULL REQUEST ANALYSIS</p>
          <h2 className="page-hero__title">#{pr.number} — {pr.title}</h2>
          <p className="page-hero__desc">
            {pr.repository} · {pr.author} · {pr.state}
            {pr.head_branch ? ` · ${pr.head_branch}` : ''}
            {pr.head_sha ? ` (${pr.head_sha.substring(0, 7)})` : ''}
          </p>
        </div>
      </div>

      {/* STATUS CARDS */}
      <div className="dashboard-grid dashboard-grid--5">
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon"><ShieldCheck size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Quality</div>
            <div className="stat-card__value">{formatScore(quality?.overall_score)}</div>
            <div className="stat-card__note">
              {quality?.grade ? (
                <Badge variant={quality.grade === 'A' || quality.grade === 'B' ? 'success' : quality.grade === 'C' ? 'warning' : 'danger'}>
                  Grade {quality.grade}
                </Badge>
              ) : 'N/A'}
            </div>
          </div>
        </div>
        <div className="stat-card stat-card--amber">
          <div className="stat-card__icon"><ShieldAlert size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Risk</div>
            <div className="stat-card__value">{formatScore(risk?.overall_score)}</div>
            <div className="stat-card__note">
              {risk?.level ? (
                <Badge variant={risk.level === 'LOW' ? 'success' : risk.level === 'MEDIUM' ? 'warning' : 'danger'}>
                  {risk.level} Risk
                </Badge>
              ) : 'N/A'}
            </div>
          </div>
        </div>
        <div className={`stat-card stat-card--${decisionVariant === 'block' ? 'red' : decisionVariant === 'warning' ? 'amber' : 'indigo'}`}>
          <div className="stat-card__icon">
            {policyDecision === 'BLOCK' ? <ShieldX size={26} strokeWidth={1.8} /> :
             policyDecision === 'WARNING' ? <ShieldAlert size={26} strokeWidth={1.8} /> :
             <ShieldCheck size={26} strokeWidth={1.8} />}
          </div>
          <div className="stat-card__body">
            <div className="stat-card__label">Policy</div>
            <div className="stat-card__value" style={{ fontSize: '24px' }}>{policyDecision}</div>
          </div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon"><CheckCircle size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Tests</div>
            <div className="stat-card__value" style={{ fontSize: '24px' }}>
              {tests ? `${tests.passed_tests ?? 0}/${tests.total_tests ?? 0}` : '—'}
            </div>
            <div className="stat-card__note">
              {tests?.failed_tests === 0 ? 'All passed' : tests ? `${tests.failed_tests} failed` : 'No tests'}
            </div>
          </div>
        </div>
        <div className="stat-card stat-card--indigo">
          <div className="stat-card__icon"><FileCheck size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Changed Coverage</div>
            <div className="stat-card__value" style={{ fontSize: '24px' }}>
              {formatPercentage(coverage?.changed_coverage)}
            </div>
          </div>
        </div>
      </div>

      {/* WHY THIS DECISION */}
      {policy && (
        <div className={`decision-panel decision-panel--${decisionVariant}`}>
          <div className="decision-panel__title">
            {policyDecision === 'BLOCK' ? <ShieldX size={20} /> :
             policyDecision === 'WARNING' ? <ShieldAlert size={20} /> :
             <ShieldCheck size={20} />}
            Why this decision?
          </div>
          <ul className="decision-panel__reasons">
            {policy.reasons?.map((reason: string, idx: number) => (
              <li key={idx} className="decision-panel__reason">
                <span className="decision-panel__dot" />
                {reason}
              </li>
            ))}
            {(!policy.reasons || policy.reasons.length === 0) && (
              <li className="decision-panel__reason">
                <span className="decision-panel__dot" />
                No specific reasons provided.
              </li>
            )}
          </ul>
        </div>
      )}

      {/* QUALITY & RISK BREAKDOWN */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Quality Breakdown</div>
          </div>
          <div className="dashboard-panel__body">
            {quality?.components?.map((comp: any) => (
              <div key={comp.category} className="breakdown-row">
                <div className="breakdown-row__label">{comp.category}</div>
                <div className="breakdown-row__score" style={{
                  color: comp.score >= 80 ? 'var(--cg-green)' : comp.score >= 60 ? 'var(--cg-amber)' : 'var(--cg-red)'
                }}>{comp.score}</div>
                <div className="breakdown-row__bar">
                  <div className="progress-bar">
                    <div
                      className={`progress-bar__fill ${comp.score >= 80 ? 'progress-bar__fill--green' : comp.score >= 60 ? 'progress-bar__fill--amber' : 'progress-bar__fill--red'}`}
                      style={{ width: `${Math.min(comp.score, 100)}%` }}
                    />
                  </div>
                </div>
                <div className="breakdown-row__weight">×{comp.weight?.toFixed(1) || '—'}</div>
              </div>
            ))}
            {(!quality?.components || quality.components.length === 0) && (
              <div style={{ textAlign: 'center', color: 'var(--cg-muted)', padding: '24px', fontSize: '13px' }}>
                No quality breakdown available.
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Risk Breakdown</div>
          </div>
          <div className="dashboard-panel__body">
            {risk?.components?.map((comp: any) => (
              <div key={comp.category} className="breakdown-row">
                <div className="breakdown-row__label">{comp.category}</div>
                <div className="breakdown-row__score" style={{
                  color: comp.score >= 75 ? 'var(--cg-red)' : comp.score >= 50 ? 'var(--cg-amber)' : 'var(--cg-green)'
                }}>{comp.score}</div>
                <div className="breakdown-row__bar">
                  <div className="progress-bar">
                    <div
                      className={`progress-bar__fill ${comp.score >= 75 ? 'progress-bar__fill--red' : comp.score >= 50 ? 'progress-bar__fill--amber' : 'progress-bar__fill--green'}`}
                      style={{ width: `${Math.min(comp.score, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
            {(!risk?.components || risk.components.length === 0) && (
              <div style={{ textAlign: 'center', color: 'var(--cg-muted)', padding: '24px', fontSize: '13px' }}>
                No risk components analyzed.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* TEST & COVERAGE */}
      <div className="dashboard-grid dashboard-grid--bottom">
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Test Results</div>
          </div>
          <div className="dashboard-panel__body">
            {tests ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <div className="metric-block"><div className="metric-block__label">Total</div><div className="metric-block__value">{tests.total_tests ?? 0}</div></div>
                <div className="metric-block metric-block--green"><div className="metric-block__label">Passed</div><div className="metric-block__value">{tests.passed_tests ?? 0}</div></div>
                <div className="metric-block metric-block--red"><div className="metric-block__label">Failed</div><div className="metric-block__value">{tests.failed_tests ?? 0}</div></div>
                <div className="metric-block"><div className="metric-block__label">Skipped</div><div className="metric-block__value">{tests.skipped_tests ?? 0}</div></div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--cg-muted)', padding: '24px', fontSize: '13px' }}>
                No test data available.
              </div>
            )}
          </div>
        </div>
        <div className="dashboard-panel">
          <div className="dashboard-panel__head">
            <div className="dashboard-panel__title">Coverage</div>
          </div>
          <div className="dashboard-panel__body">
            {coverage ? (
              <>
                <div className="metric-block metric-block--blue">
                  <div className="metric-block__label">Overall Coverage</div>
                  <div className="metric-block__value">
                    {formatPercentage(coverage.overall_coverage)}
                  </div>
                </div>
                <div className="metric-block metric-block--indigo">
                  <div className="metric-block__label">Changed-Code Coverage</div>
                  <div className="metric-block__value">
                    {formatPercentage(coverage.changed_coverage)}
                  </div>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--cg-muted)', padding: '24px', fontSize: '13px' }}>
                No coverage data available.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* FINDINGS */}
      <div className="dashboard-panel" style={{ marginBottom: '16px' }}>
        <div className="dashboard-panel__head">
          <div className="dashboard-panel__title">
            <Bug size={18} strokeWidth={1.8} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Findings
          </div>
          <div className="dashboard-panel__meta">{findings?.length || 0} issues</div>
        </div>
        <div className="dashboard-panel__body">
          {findings && findings.length > 0 ? (
            <div className="table-wrapper" style={{ boxShadow: 'none', border: '1px solid #f1f5f9' }}>
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>Severity</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>File</th>
                    <th>Line</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map((f: any, idx: number) => (
                    <tr key={idx}>
                      <td>
                        <Badge variant={f.severity === 'CRITICAL' || f.severity === 'HIGH' ? 'danger' : f.severity === 'MEDIUM' ? 'warning' : 'default'}>
                          {f.severity}
                        </Badge>
                      </td>
                      <td className="cell-primary font-medium">{f.title}</td>
                      <td><Badge variant="indigo">{f.category}</Badge></td>
                      <td className="cell-muted" style={{ fontFamily: 'monospace', fontSize: '12px' }}>{f.file_path}</td>
                      <td className="cell-muted">{f.line_number}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--cg-muted)', fontSize: '13px' }}>
              <ShieldCheck size={32} strokeWidth={1.2} style={{ margin: '0 auto 8px', opacity: 0.4 }} />
              <div>No issues found in this pull request.</div>
            </div>
          )}
        </div>
      </div>

      {/* REVIEWER RECOMMENDATIONS */}
      <div className="dashboard-panel">
        <div className="dashboard-panel__head">
          <div className="dashboard-panel__title">
            <Users size={18} strokeWidth={1.8} style={{ marginRight: '8px', verticalAlign: 'middle' }} />
            Suggested Reviewers
          </div>
        </div>
        <div className="dashboard-panel__body">
          {reviewers && (Array.isArray(reviewers) ? reviewers : [reviewers]).length > 0 ? (
            (Array.isArray(reviewers) ? reviewers : [reviewers]).map((r: any, idx: number) => (
              <div key={idx} className="reviewer-card">
                <div className="reviewer-card__avatar">
                  {r.reviewer_username?.charAt(0)?.toUpperCase() || '?'}
                </div>
                <div className="reviewer-card__info">
                  <div className="reviewer-card__name">@{r.reviewer_username}</div>
                  <div className="reviewer-card__reasons">
                    {r.reasons?.join(' · ') || 'No details'}
                  </div>
                </div>
                <div className="reviewer-card__score">
                  {formatScore(r.match_score)} match
                </div>
              </div>
            ))
          ) : (
            <div style={{ textAlign: 'center', padding: '32px', color: 'var(--cg-muted)', fontSize: '13px' }}>
              No reviewer recommendations available.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
