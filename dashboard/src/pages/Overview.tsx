import { useEffect, useState } from 'react';
import type { DashboardOverviewResponse } from '../types';
import { CodeGateAPI } from '../api/client';
import {
  ShieldCheck,
  AlertTriangle,
  GitPullRequest,
  FileCheck,
  ShieldX,
  CheckCircle,
  RefreshCw,
  LayoutDashboard,
  Award,
  ShieldAlert,
  TrendingUp,
  Activity,
  Sparkles
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  AreaChart, Area, LineChart, Line, CartesianGrid, Cell, Legend
} from 'recharts';
import { formatPercentage, formatScore } from '../lib/utils';
import { ErrorState } from '../components/ui/ErrorState';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useAuth } from '../contexts/AuthContext';

interface TooltipPayloadItem {
  name?: string;
  value?: number | string;
  payload?: any;
  dataKey?: string;
}

const CustomGradeTooltip = ({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.94)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '12px',
          padding: '10px 14px',
          boxShadow: '0 14px 30px rgba(0, 0, 0, 0.28)',
          color: '#fff',
          fontSize: '12px',
          minWidth: '150px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '6px' }}>
          <span style={{ fontWeight: 700, fontSize: '13px', color: item.color }}>{item.label}</span>
          <span style={{ fontSize: '10px', fontWeight: 600, padding: '1px 6px', borderRadius: '999px', background: 'rgba(255, 255, 255, 0.1)', color: '#94a3b8' }}>
            {item.range}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '4px' }}>
          <span style={{ fontSize: '20px', fontWeight: 800, color: '#f8fafc', lineHeight: 1 }}>{item.count}</span>
          <span style={{ color: '#94a3b8', fontSize: '11px' }}>PR ({item.pct}%)</span>
        </div>
        <div style={{ color: '#cbd5e1', fontSize: '11px' }}>{item.desc}</div>
      </div>
    );
  }
  return null;
};

const CustomRiskTooltip = ({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) => {
  if (active && payload && payload.length) {
    const item = payload[0].payload;
    return (
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.94)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '12px',
          padding: '10px 14px',
          boxShadow: '0 14px 30px rgba(0, 0, 0, 0.28)',
          color: '#fff',
          fontSize: '12px',
          minWidth: '150px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '6px' }}>
          <span style={{ fontWeight: 700, fontSize: '13px', color: item.color }}>Mức: {item.label}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px', marginBottom: '4px' }}>
          <span style={{ fontSize: '20px', fontWeight: 800, color: '#f8fafc', lineHeight: 1 }}>{item.count}</span>
          <span style={{ color: '#94a3b8', fontSize: '11px' }}>PR ({item.pct}%)</span>
        </div>
        <div style={{ color: '#cbd5e1', fontSize: '11px' }}>{item.desc}</div>
      </div>
    );
  }
  return null;
};

const CustomTrendTooltip = ({ active, payload, label }: { active?: boolean; payload?: TooltipPayloadItem[]; label?: string }) => {
  if (active && payload && payload.length) {
    const qItem = payload.find((p) => p.dataKey === 'quality');
    const rItem = payload.find((p) => p.dataKey === 'risk');
    return (
      <div
        style={{
          background: 'rgba(15, 23, 42, 0.94)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '12px',
          padding: '12px 14px',
          boxShadow: '0 14px 30px rgba(0, 0, 0, 0.28)',
          color: '#fff',
          fontSize: '12px',
          minWidth: '170px',
        }}
      >
        <div style={{ color: '#94a3b8', fontSize: '11px', marginBottom: '8px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Activity size={12} /> {label}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '6px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#6ee7b7' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px rgba(16, 185, 129, 0.6)' }} />
            Quality Score
          </span>
          <span style={{ fontWeight: 800, color: '#fff', fontSize: '13px' }}>
            {qItem?.value !== undefined ? Number(qItem.value).toFixed(1) : 'N/A'}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fcd34d' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 6px rgba(245, 158, 11, 0.6)' }} />
            Risk Score
          </span>
          <span style={{ fontWeight: 800, color: '#fff', fontSize: '13px' }}>
            {rItem?.value !== undefined ? Number(rItem.value).toFixed(2) : 'N/A'}
          </span>
        </div>
      </div>
    );
  }
  return null;
};

export function Overview() {
  const { workspaceVersion, activeWorkspace, loading: authLoading } = useAuth();
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (authLoading || !activeWorkspace) return;

    let cancelled = false;

    const fetchOverview = async (retries = 3, delay = import.meta.env.MODE === 'test' ? 0 : 800) => {
      setLoading(true);
      setError(null);
      for (let attempt = 0; attempt < retries; attempt++) {
        try {
          const overview = await CodeGateAPI.getOverview();
          if (!cancelled) {
            setData(overview);
            setError(null);
            setLoading(false);
          }
          return;
        } catch (err: unknown) {
          if (attempt === retries - 1 && !cancelled) {
            setError(err instanceof Error ? err.message : 'Failed to fetch overview');
            setLoading(false);
          } else {
            await new Promise(r => setTimeout(r, delay));
          }
        }
      }
    };

    fetchOverview();

    return () => { cancelled = true; };
  }, [workspaceVersion, authLoading, activeWorkspace?.id]);

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
        <ErrorState onRetry={() => window.location.reload()} description={error} />
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
          <button className="btn-primary" onClick={() => window.location.reload()}>
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
      {(() => {
        const rawGrades = d.quality_grade_distribution || {};
        const totalGradedPRs = Object.values(rawGrades).reduce((acc, v) => acc + (Number(v) || 0), 0);
        const gradeConfigs = [
          { key: 'A', label: 'Grade A', range: '90-100', desc: 'Xuất sắc (90-100)', color: '#10b981', fill: 'url(#gradeGradA)', border: '#059669', bgBadge: 'rgba(16, 185, 129, 0.12)' },
          { key: 'B', label: 'Grade B', range: '80-89', desc: 'Tốt (80-89)', color: '#3b82f6', fill: 'url(#gradeGradB)', border: '#2563eb', bgBadge: 'rgba(59, 130, 246, 0.12)' },
          { key: 'C', label: 'Grade C', range: '70-79', desc: 'Trung bình (70-79)', color: '#f59e0b', fill: 'url(#gradeGradC)', border: '#d97706', bgBadge: 'rgba(245, 158, 11, 0.12)' },
          { key: 'D', label: 'Grade D', range: '60-69', desc: 'Cần cải thiện (60-69)', color: '#f97316', fill: 'url(#gradeGradD)', border: '#ea580c', bgBadge: 'rgba(249, 115, 22, 0.12)' },
          { key: 'F', label: 'Grade F', range: '<60', desc: 'Không đạt (<60)', color: '#ef4444', fill: 'url(#gradeGradF)', border: '#dc2626', bgBadge: 'rgba(239, 68, 68, 0.12)' },
        ];
        const gradeChartData = gradeConfigs.map(c => {
          const count = Number(rawGrades[c.key]) || 0;
          const pct = totalGradedPRs > 0 ? Math.round((count / totalGradedPRs) * 100) : 0;
          return { ...c, count, pct };
        });

        const rawRisks = d.risk_level_distribution || {};
        const totalRiskPRs = Object.values(rawRisks).reduce((acc, v) => acc + (Number(v) || 0), 0);
        const riskConfigs = [
          { key: 'LOW', label: 'Low', desc: 'An toàn để merge', color: '#10b981', fill: 'url(#riskGradLow)', border: '#059669', bgBadge: 'rgba(16, 185, 129, 0.12)' },
          { key: 'MEDIUM', label: 'Medium', desc: 'Cần chú ý review', color: '#f59e0b', fill: 'url(#riskGradMed)', border: '#d97706', bgBadge: 'rgba(245, 158, 11, 0.12)' },
          { key: 'HIGH', label: 'High', desc: 'Cảnh báo rủi ro cao', color: '#f97316', fill: 'url(#riskGradHigh)', border: '#ea580c', bgBadge: 'rgba(249, 115, 22, 0.12)' },
          { key: 'CRITICAL', label: 'Critical', desc: 'Nguy hiểm, chặn merge', color: '#ef4444', fill: 'url(#riskGradCrit)', border: '#dc2626', bgBadge: 'rgba(239, 68, 68, 0.12)' },
        ];
        const riskChartData = riskConfigs.map(c => {
          const count = Number(rawRisks[c.key]) || 0;
          const pct = totalRiskPRs > 0 ? Math.round((count / totalRiskPRs) * 100) : 0;
          return { ...c, count, pct };
        });

        const rawQualityTrend = d.quality_trend || [];
        const rawRiskTrend = d.risk_trend || [];
        const trendData = rawQualityTrend.map((q, i) => ({
          date: q.date,
          quality: typeof q.value === 'number' ? Number(q.value.toFixed(1)) : 0,
          risk: typeof rawRiskTrend[i]?.value === 'number' ? Number(rawRiskTrend[i].value.toFixed(2)) : 0,
        }));
        const latestQuality = trendData.length > 0 ? trendData[trendData.length - 1].quality : (d.average_quality_score ?? 0);
        const latestRisk = trendData.length > 0 ? trendData[trendData.length - 1].risk : (d.average_risk_score ?? 0);

        return (
          <>
            <div className="dashboard-grid dashboard-grid--charts">
              {/* PANEL 1: QUALITY GRADE DISTRIBUTION */}
              <div className="dashboard-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="dashboard-panel__head">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '34px', height: '34px', borderRadius: '10px',
                      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.1))',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#059669', border: '1px solid rgba(16, 185, 129, 0.25)',
                      boxShadow: '0 2px 6px rgba(16, 185, 129, 0.15)'
                    }}>
                      <Award size={18} strokeWidth={2.2} />
                    </div>
                    <div>
                      <div className="dashboard-panel__title" style={{ fontSize: '15px' }}>Quality Grade Distribution</div>
                      <div style={{ fontSize: '11px', color: 'var(--cg-muted)' }}>Phân bổ chất lượng code PRs</div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '11px', fontWeight: 700, padding: '3px 10px',
                    borderRadius: '999px', background: 'rgba(16, 185, 129, 0.1)',
                    color: '#059669', border: '1px solid rgba(16, 185, 129, 0.25)',
                    letterSpacing: '0.3px'
                  }}>
                    {totalGradedPRs} PRs
                  </span>
                </div>

                <div className="dashboard-panel__body" style={{ height: '210px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={gradeChartData} margin={{ top: 15, right: 10, left: -20, bottom: 5 }}>
                      <defs>
                        <linearGradient id="gradeGradA" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#34d399" stopOpacity={1} />
                          <stop offset="100%" stopColor="#059669" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="gradeGradB" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#60a5fa" stopOpacity={1} />
                          <stop offset="100%" stopColor="#2563eb" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="gradeGradC" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#fbbf24" stopOpacity={1} />
                          <stop offset="100%" stopColor="#d97706" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="gradeGradD" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#fb923c" stopOpacity={1} />
                          <stop offset="100%" stopColor="#ea580c" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="gradeGradF" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f87171" stopOpacity={1} />
                          <stop offset="100%" stopColor="#dc2626" stopOpacity={0.85} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.18)" />
                      <XAxis
                        dataKey="key"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)', fontWeight: 700 }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        allowDecimals={false}
                        tick={{ fontSize: 11, fill: 'var(--cg-muted)' }}
                      />
                      <Tooltip cursor={{ fill: 'rgba(99, 102, 241, 0.04)', radius: 8 }} content={<CustomGradeTooltip />} />
                      <Bar dataKey="count" maxBarSize={36} radius={[8, 8, 2, 2]}>
                        {gradeChartData.map((entry) => (
                          <Cell key={entry.key} fill={entry.fill} stroke={entry.border} strokeWidth={1} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Grade Mini Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '4px', paddingTop: '10px', borderTop: '1px solid var(--cg-border-soft)' }}>
                  {gradeChartData.map(g => (
                    <div key={g.key} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: g.color }} />
                      <span style={{ fontWeight: 600, color: 'var(--cg-text-secondary)' }}>{g.key}:</span>
                      <span style={{ fontWeight: 700, color: g.count > 0 ? g.color : 'var(--cg-muted)' }}>{g.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* PANEL 2: RISK LEVEL DISTRIBUTION */}
              <div className="dashboard-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="dashboard-panel__head">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '34px', height: '34px', borderRadius: '10px',
                      background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1))',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#d97706', border: '1px solid rgba(245, 158, 11, 0.25)',
                      boxShadow: '0 2px 6px rgba(245, 158, 11, 0.15)'
                    }}>
                      <ShieldAlert size={18} strokeWidth={2.2} />
                    </div>
                    <div>
                      <div className="dashboard-panel__title" style={{ fontSize: '15px' }}>Risk Level Distribution</div>
                      <div style={{ fontSize: '11px', color: 'var(--cg-muted)' }}>Mức độ rủi ro rà soát</div>
                    </div>
                  </div>
                  <span style={{
                    fontSize: '11px', fontWeight: 700, padding: '3px 10px',
                    borderRadius: '999px', background: 'rgba(245, 158, 11, 0.1)',
                    color: '#d97706', border: '1px solid rgba(245, 158, 11, 0.25)',
                    letterSpacing: '0.3px'
                  }}>
                    {totalRiskPRs} Đã phân tích
                  </span>
                </div>

                <div className="dashboard-panel__body" style={{ height: '210px', width: '100%' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={riskChartData} margin={{ top: 15, right: 10, left: -20, bottom: 5 }}>
                      <defs>
                        <linearGradient id="riskGradLow" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#34d399" stopOpacity={1} />
                          <stop offset="100%" stopColor="#059669" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="riskGradMed" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#fbbf24" stopOpacity={1} />
                          <stop offset="100%" stopColor="#d97706" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="riskGradHigh" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#fb923c" stopOpacity={1} />
                          <stop offset="100%" stopColor="#ea580c" stopOpacity={0.85} />
                        </linearGradient>
                        <linearGradient id="riskGradCrit" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#f87171" stopOpacity={1} />
                          <stop offset="100%" stopColor="#dc2626" stopOpacity={0.85} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.18)" />
                      <XAxis
                        dataKey="label"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12, fill: 'var(--cg-text-secondary)', fontWeight: 700 }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        allowDecimals={false}
                        tick={{ fontSize: 11, fill: 'var(--cg-muted)' }}
                      />
                      <Tooltip cursor={{ fill: 'rgba(99, 102, 241, 0.04)', radius: 8 }} content={<CustomRiskTooltip />} />
                      <Bar dataKey="count" maxBarSize={36} radius={[8, 8, 2, 2]}>
                        {riskChartData.map((entry) => (
                          <Cell key={entry.key} fill={entry.fill} stroke={entry.border} strokeWidth={1} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Risk Mini Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '4px', paddingTop: '10px', borderTop: '1px solid var(--cg-border-soft)' }}>
                  {riskChartData.map(r => (
                    <div key={r.key} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: r.color }} />
                      <span style={{ fontWeight: 600, color: 'var(--cg-text-secondary)' }}>{r.label}:</span>
                      <span style={{ fontWeight: 700, color: r.count > 0 ? r.color : 'var(--cg-muted)' }}>{r.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* PANEL 3: POLICY DECISIONS */}
              <div className="dashboard-panel">
                <div className="dashboard-panel__head">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '34px', height: '34px', borderRadius: '10px',
                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(79, 70, 229, 0.1))',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#4f46e5', border: '1px solid rgba(99, 102, 241, 0.25)',
                      boxShadow: '0 2px 6px rgba(99, 102, 241, 0.15)'
                    }}>
                      <ShieldCheck size={18} strokeWidth={2.2} />
                    </div>
                    <div>
                      <div className="dashboard-panel__title" style={{ fontSize: '15px' }}>Policy Decisions</div>
                      <div style={{ fontSize: '11px', color: 'var(--cg-muted)' }}>Kết quả thực thi quy tắc</div>
                    </div>
                  </div>
                </div>
                <div className="dashboard-panel__body">
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div className="metric-block metric-block--green">
                      <div className="metric-block__label">PASS (HỢP LỆ)</div>
                      <div className="metric-block__value">{d.policy_pass_count ?? 0}</div>
                    </div>
                    <div className="metric-block metric-block--amber">
                      <div className="metric-block__label">WARNING (CẢNH BÁO)</div>
                      <div className="metric-block__value">{d.policy_warning_count ?? 0}</div>
                    </div>
                    <div className="metric-block metric-block--red">
                      <div className="metric-block__label">BLOCK (CHẶN)</div>
                      <div className="metric-block__value">{d.policy_block_count ?? 0}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ANALYTICS ROW: 2fr 1fr */}
            <div className="dashboard-grid dashboard-grid--analytics">
              {/* QUALITY & RISK TREND */}
              <div className="dashboard-panel" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="dashboard-panel__head">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                      width: '34px', height: '34px', borderRadius: '10px',
                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(124, 58, 237, 0.1))',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      color: '#6366f1', border: '1px solid rgba(99, 102, 241, 0.25)',
                      boxShadow: '0 2px 6px rgba(99, 102, 241, 0.15)'
                    }}>
                      <TrendingUp size={18} strokeWidth={2.2} />
                    </div>
                    <div>
                      <div className="dashboard-panel__title" style={{ fontSize: '15px' }}>Quality & Risk Trend</div>
                      <div style={{ fontSize: '11px', color: 'var(--cg-muted)' }}>Xu hướng chất lượng & rủi ro gần đây</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: '5px',
                      fontSize: '11px', fontWeight: 700, padding: '3px 10px',
                      borderRadius: '999px', background: 'rgba(16, 185, 129, 0.1)',
                      color: '#059669', border: '1px solid rgba(16, 185, 129, 0.25)'
                    }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 5px rgba(16, 185, 129, 0.8)' }} />
                      Quality: {latestQuality.toFixed(1)}
                    </span>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: '5px',
                      fontSize: '11px', fontWeight: 700, padding: '3px 10px',
                      borderRadius: '999px', background: 'rgba(245, 158, 11, 0.1)',
                      color: '#d97706', border: '1px solid rgba(245, 158, 11, 0.25)'
                    }}>
                      <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#f59e0b', boxShadow: '0 0 5px rgba(245, 158, 11, 0.8)' }} />
                      Risk: {latestRisk.toFixed(2)}
                    </span>
                  </div>
                </div>

                <div className="dashboard-panel__body" style={{ height: '230px', width: '100%' }}>
                  {trendData.length === 0 ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--cg-muted)' }}>
                      No trend data available
                    </div>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={trendData} margin={{ top: 15, right: 15, left: -20, bottom: 5 }}>
                        <defs>
                          <linearGradient id="qualityAreaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.32} />
                            <stop offset="100%" stopColor="#10b981" stopOpacity={0.02} />
                          </linearGradient>
                          <linearGradient id="riskAreaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.28} />
                            <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.02} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.18)" />
                        <XAxis
                          dataKey="date"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 11, fill: 'var(--cg-text-secondary)', fontWeight: 600 }}
                        />
                        <YAxis
                          domain={[0, 100]}
                          ticks={[0, 25, 50, 75, 100]}
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 11, fill: 'var(--cg-muted)' }}
                        />
                        <Tooltip content={<CustomTrendTooltip />} />
                        <Legend
                          iconType="circle"
                          wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }}
                        />
                        <Area
                          type="monotone"
                          dataKey="quality"
                          name="Quality Score"
                          stroke="#10b981"
                          strokeWidth={2.5}
                          fill="url(#qualityAreaGrad)"
                          dot={{ r: 5, fill: '#10b981', stroke: '#ffffff', strokeWidth: 2 }}
                          activeDot={{ r: 7, fill: '#10b981', stroke: '#ffffff', strokeWidth: 3 }}
                        />
                        <Area
                          type="monotone"
                          dataKey="risk"
                          name="Risk Score"
                          stroke="#f59e0b"
                          strokeWidth={2.5}
                          fill="url(#riskAreaGrad)"
                          dot={{ r: 5, fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 2 }}
                          activeDot={{ r: 7, fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 3 }}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>

                {trendData.length === 1 && (
                  <div style={{
                    marginTop: '8px', padding: '6px 12px', borderRadius: '8px',
                    background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.12)',
                    fontSize: '11px', color: 'var(--cg-muted)', display: 'flex', alignItems: 'center', gap: '6px'
                  }}>
                    <Sparkles size={13} className="text-indigo-500" />
                    <span>Đang hiển thị bản ghi PR đầu tiên. Biểu đồ sẽ tự động vẽ đồ thị liên tục khi có thêm các PR tiếp theo.</span>
                  </div>
                )}
              </div>

              {/* TESTING SUMMARY */}
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
          </>
        );
      })()}

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
