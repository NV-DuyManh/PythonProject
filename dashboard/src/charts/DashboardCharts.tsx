import { useId, useState } from 'react';
import {
  CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend,
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area
} from 'recharts';
import { formatScore } from '../lib/utils';
import { CheckCircle2, AlertTriangle, ShieldX } from 'lucide-react';

export type TrendPoint = { date: string; value?: number | null };
export type Series = { name: string; color: string; points: TrendPoint[] };

export function mergeTrends(series: Series[]) {
  const dates = [...new Set(series.flatMap(item => item.points.map(point => point.date)))].sort();
  return dates.map(date => Object.fromEntries([
    ['date', date],
    ...series.map(item => [item.name, item.points.find(point => point.date === date)?.value ?? null]),
  ]));
}

// -------------------------------------------------------------
// 1. POLICY DONUT CHART (Interactive Circular Chart)
// -------------------------------------------------------------
export function PolicyDonutChart({
  title = 'Policy decisions',
  values,
  colors = {
    PASS: '#10b981',
    WARNING: '#f59e0b',
    BLOCK: '#ef4444',
  }
}: {
  title?: string;
  values: Record<string, number>;
  colors?: Record<string, string>;
}) {
  const id = useId();
  const pass = values.PASS || 0;
  const warning = values.WARNING || 0;
  const block = values.BLOCK || 0;
  const total = pass + warning + block;
  const passRate = total > 0 ? Math.round((pass / total) * 100) : 0;

  const chartData = [
    { name: 'PASS', label: 'Pass', value: pass, color: colors.PASS || '#10b981' },
    { name: 'WARNING', label: 'Warning', value: warning, color: colors.WARNING || '#f59e0b' },
    { name: 'BLOCK', label: 'Block', value: block, color: colors.BLOCK || '#ef4444' },
  ].filter(item => item.value > 0);

  return (
    <section className="dashboard-panel policy-donut-card" aria-labelledby={id}>
      <div className="section-heading">
        <h2 id={id}>{title}</h2>
        <span className="muted">{total} recorded</span>
      </div>

      {total === 0 ? (
        <div className="chart-empty">No policy evaluations recorded</div>
      ) : (
        <div className="policy-donut-layout">
          {/* Donut Container with centered metric */}
          <div className="relative w-44 h-44 flex items-center justify-center shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const percent = total > 0 ? Math.round((data.value / total) * 100) : 0;
                      return (
                        <div className="chart-tooltip">
                          <div className="chart-tooltip__title" style={{ display: 'flex', alignItems: 'center', gap: 6, color: data.color }}>
                            <span style={{ width: 8, height: 8, borderRadius: '50%', background: data.color }} />
                            {data.label}
                          </div>
                          <div className="chart-tooltip__item">
                            <span style={{ color: '#cbd5e1' }}>Evaluations:</span>
                            <strong style={{ color: '#ffffff' }}>{data.value} ({percent}%)</strong>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={52}
                  outerRadius={74}
                  paddingAngle={chartData.length > 1 ? 4 : 0}
                  cornerRadius={chartData.length > 1 ? 5 : 0}
                  dataKey="value"
                  stroke="transparent"
                  isAnimationActive={true}
                >
                  {chartData.map((entry) => (
                    <Cell key={`cell-${entry.name}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>

            {/* Inner Center Hole Metrics */}
            <div className="policy-donut-center">
              <span className="policy-donut-value">
                {passRate}%
              </span>
              <span className="policy-donut-label">
                Pass rate
              </span>
            </div>
          </div>

          {/* Breakdown List */}
          <div className="policy-donut-list">
            {[
              { key: 'PASS', label: 'Pass', count: pass, color: colors.PASS || '#10b981', icon: CheckCircle2, badgeClass: 'policy-badge--pass' },
              { key: 'WARNING', label: 'Warning', count: warning, color: colors.WARNING || '#f59e0b', icon: AlertTriangle, badgeClass: 'policy-badge--warning' },
              { key: 'BLOCK', label: 'Block', count: block, color: colors.BLOCK || '#ef4444', icon: ShieldX, badgeClass: 'policy-badge--block' },
            ].map(({ key, label, count, color, icon: Icon, badgeClass }) => {
              const pct = total > 0 ? Math.round((count / total) * 100) : 0;
              return (
                <div key={key} className="policy-donut-row">
                  <div className="policy-donut-item-left">
                    <Icon style={{ width: 14, height: 14, color, flexShrink: 0 }} />
                    <span className="policy-donut-name">{label}</span>
                  </div>
                  <div className="policy-donut-item-right">
                    <span className={`policy-donut-pct ${badgeClass}`}>
                      {pct}%
                    </span>
                    <span className="policy-donut-count">
                      {count}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}

// -------------------------------------------------------------
// 2. ENHANCED QUALITY & RISK TREND CHART
// -------------------------------------------------------------
export interface QualityRiskTrendChartProps {
  title?: string;
  prs?: any[];
  qualityTrend?: TrendPoint[];
  riskTrend?: TrendPoint[];
}

export function QualityRiskTrendChart({
  title = 'Quality & risk',
  prs = [],
  qualityTrend = [],
  riskTrend = [],
}: QualityRiskTrendChartProps) {
  const id = useId();

  // Extract PR data points with scores
  const prPoints = (prs || [])
    .filter(pr => pr.quality_score != null || pr.risk_score != null)
    .map(pr => ({
      name: `#${pr.number}`,
      label: `PR #${pr.number}`,
      title: pr.title || `Pull Request #${pr.number}`,
      author: pr.author || 'unknown',
      quality: pr.quality_score != null ? Math.round(pr.quality_score * 10) / 10 : null,
      risk: pr.risk_score != null ? Math.round(pr.risk_score * 10) / 10 : null,
      date: pr.created_at ? pr.created_at.slice(0, 10) : '',
    }))
    .reverse(); // Chronological order

  // Daily trend points
  const dailyData = mergeTrends([
    { name: 'Quality', color: '#6366f1', points: qualityTrend },
    { name: 'Risk', color: '#f59e0b', points: riskTrend },
  ]);

  const hasPrData = prPoints.length > 0;
  const [viewMode, setViewMode] = useState<'pr' | 'daily'>(hasPrData ? 'pr' : 'daily');

  const chartData = viewMode === 'pr' && hasPrData ? prPoints : dailyData;
  const xKey = viewMode === 'pr' && hasPrData ? 'name' : 'date';
  const qualityKey = viewMode === 'pr' && hasPrData ? 'quality' : 'Quality';
  const riskKey = viewMode === 'pr' && hasPrData ? 'risk' : 'Risk';

  return (
    <section className="dashboard-panel" aria-labelledby={id}>
      <div className="section-heading flex items-center justify-between">
        <div>
          <h2 id={id}>{title}</h2>
          <span className="muted">
            {viewMode === 'pr' ? `${prPoints.length} pull requests timeline` : 'Daily averages'}
          </span>
        </div>

        {/* View Mode Toggle Switch */}
        {hasPrData && (
          <div className="chart-view-toggle">
            <button
              type="button"
              onClick={() => setViewMode('pr')}
              className={`chart-view-btn ${viewMode === 'pr' ? 'chart-view-btn--active' : ''}`}
            >
              By PR
            </button>
            <button
              type="button"
              onClick={() => setViewMode('daily')}
              className={`chart-view-btn ${viewMode === 'daily' ? 'chart-view-btn--active' : ''}`}
            >
              Daily
            </button>
          </div>
        )}
      </div>

      {chartData.length === 0 ? (
        <div className="chart-empty">No historical data available</div>
      ) : (
        <>
          <div className="chart-frame" style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <AreaChart data={chartData} margin={{ top: 14, right: 16, left: -20, bottom: 4 }}>
                <defs>
                  <linearGradient id="qualityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.22} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.16} />
                    <stop offset="100%" stopColor="#f59e0b" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="var(--cg-border-soft)" strokeDasharray="3 3" />
                <XAxis
                  dataKey={xKey}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'var(--cg-muted)' }}
                  minTickGap={20}
                />
                <YAxis
                  domain={[0, 100]}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'var(--cg-muted)' }}
                />
                <Tooltip
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="chart-tooltip">
                          <div className="chart-tooltip__title">
                            {viewMode === 'pr' && item.title ? (
                              <div>
                                <span style={{ color: '#818cf8', fontWeight: 700 }}>{item.label}</span>
                                <p style={{ color: '#cbd5e1', fontWeight: 400, margin: '2px 0 0 0', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 220 }}>
                                  {item.title}
                                </p>
                              </div>
                            ) : (
                              <span>{label}</span>
                            )}
                          </div>
                          <div className="chart-tooltip__item">
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#818cf8' }}>
                              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#6366f1' }} />
                              Quality:
                            </span>
                            <strong style={{ color: '#ffffff' }}>{item[qualityKey] ?? 'N/A'}</strong>
                          </div>
                          <div className="chart-tooltip__item">
                            <span style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#fbbf24' }}>
                              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }} />
                              Risk:
                            </span>
                            <strong style={{ color: '#ffffff' }}>{item[riskKey] ?? 'N/A'}</strong>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                <Area
                  type="monotone"
                  dataKey={qualityKey}
                  name="Quality"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  fill="url(#qualityGradient)"
                  dot={{ r: 3.5, fill: '#6366f1', strokeWidth: 1.5, stroke: '#ffffff' }}
                  activeDot={{ r: 6, fill: '#6366f1', stroke: '#ffffff', strokeWidth: 2 }}
                  connectNulls={true}
                  isAnimationActive={true}
                />
                <Area
                  type="monotone"
                  dataKey={riskKey}
                  name="Risk"
                  stroke="#f59e0b"
                  strokeWidth={2.5}
                  fill="url(#riskGradient)"
                  dot={{ r: 3.5, fill: '#f59e0b', strokeWidth: 1.5, stroke: '#ffffff' }}
                  activeDot={{ r: 6, fill: '#f59e0b', stroke: '#ffffff', strokeWidth: 2 }}
                  connectNulls={true}
                  isAnimationActive={true}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {chartData.length === 1 && (
            <p className="muted text-xs mt-2">
              One recorded entry. Additional pull requests will build a historical trajectory.
            </p>
          )}

          <details className="chart-data mt-2">
            <summary className="text-xs cursor-pointer text-slate-500 hover:text-slate-800 dark:hover:text-slate-200">
              View chart data
            </summary>
            <div className="table-wrapper mt-2">
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>{viewMode === 'pr' ? 'Pull Request' : 'Date'}</th>
                    <th>Quality</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {chartData.map((row, i) => (
                    <tr key={i}>
                      <td>{String(row[xKey])}</td>
                      <td>{formatScore(row[qualityKey] as number | null)}</td>
                      <td>{formatScore(row[riskKey] as number | null)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </section>
  );
}

// -------------------------------------------------------------
// 3. LEGACY COMPATIBLE TREND CHART (Standardized)
// -------------------------------------------------------------
export function TrendChart({ title, series }: { title: string; series: Series[] }) {
  const id = useId();
  const data = mergeTrends(series);
  return (
    <section className="dashboard-panel" aria-labelledby={id}>
      <div className="section-heading">
        <h2 id={id}>{title}</h2>
        <span className="muted">Daily averages</span>
      </div>
      {data.length === 0 ? (
        <div className="chart-empty">No historical data available</div>
      ) : (
        <>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <LineChart data={data} margin={{ top: 12, right: 16, left: -20, bottom: 0 }} accessibilityLayer>
                <CartesianGrid vertical={false} stroke="var(--cg-border-soft)" strokeDasharray="3 3" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} minTickGap={30} />
                <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} />
                <Tooltip contentStyle={{ borderRadius: 8, borderColor: 'var(--cg-border)', fontSize: 13, background: 'var(--cg-surface)', color: 'var(--cg-text)' }} />
                <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
                {series.map(item => (
                  <Line
                    key={item.name}
                    type="monotone"
                    dataKey={item.name}
                    stroke={item.color}
                    strokeWidth={2.5}
                    dot={{ r: 3.5 }}
                    activeDot={{ r: 5 }}
                    connectNulls={true}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          {data.length === 1 && <p className="muted">One recorded day. More history is needed to show a trend.</p>}
          <details className="chart-data">
            <summary>View chart data</summary>
            <div className="table-wrapper">
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    {series.map(item => <th key={item.name}>{item.name}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {data.map(row => (
                    <tr key={String(row.date)}>
                      <td>{row.date}</td>
                      {series.map(item => (
                        <td key={item.name}>{formatScore(row[item.name] as number | null)}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </section>
  );
}

// -------------------------------------------------------------
// 4. DISTRIBUTION CHART (Preserved & Enhanced)
// -------------------------------------------------------------
export function DistributionChart({ title, values, colors = {} }: {
  title: string; values: Record<string, number>; colors?: Record<string, string>;
}) {
  const id = useId();
  const total = Object.values(values).reduce((sum, value) => sum + value, 0);
  return (
    <section className="dashboard-panel" aria-labelledby={id}>
      <div className="section-heading">
        <h2 id={id}>{title}</h2>
        <span className="muted">{total} recorded</span>
      </div>
      {total === 0 ? (
        <div className="chart-empty">No recorded results</div>
      ) : (
        <dl className="distribution">
          {Object.entries(values).map(([label, value]) => (
            <div key={label} className="distribution__row">
              <dt className="text-slate-700 dark:text-slate-200">{label}</dt>
              <dd>
                <span className="distribution__track" aria-hidden="true">
                  <span style={{ width: `${(value / total) * 100}%`, background: colors[label] || 'var(--cg-primary)' }} />
                </span>
                <strong className="text-slate-900 dark:text-slate-100">{value}</strong>
              </dd>
            </div>
          ))}
        </dl>
      )}
    </section>
  );
}

// -------------------------------------------------------------
// 5. POLICY TREND CHART (Stacked Bar for History)
// -------------------------------------------------------------
export function PolicyTrendChart({ data }: { data: { date: string; pass_count?: number | null; warning_count?: number | null; block_count?: number | null }[] }) {
  return (
    <section className="dashboard-panel" aria-label="Policy history">
      <div className="section-heading">
        <h2>Policy history</h2>
        <span className="muted">Daily evaluations</span>
      </div>
      {!data.length ? (
        <div className="chart-empty">No policy history available</div>
      ) : (
        <>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height="100%" minWidth={0}>
              <BarChart data={data} margin={{ top: 8, right: 12, left: -20, bottom: 0 }} accessibilityLayer>
                <CartesianGrid vertical={false} stroke="var(--cg-border-soft)" strokeDasharray="3 3" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} />
                <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} />
                <Tooltip contentStyle={{ borderRadius: 8, borderColor: 'var(--cg-border)', background: 'var(--cg-surface)', color: 'var(--cg-text)' }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="pass_count" name="Pass" stackId="policy" fill="var(--cg-green, #10b981)" radius={[0, 0, 0, 0]} maxBarSize={36} isAnimationActive={false} />
                <Bar dataKey="warning_count" name="Warning" stackId="policy" fill="var(--cg-amber, #f59e0b)" radius={[0, 0, 0, 0]} maxBarSize={36} isAnimationActive={false} />
                <Bar dataKey="block_count" name="Block" stackId="policy" fill="var(--cg-red, #ef4444)" radius={[4, 4, 0, 0]} maxBarSize={36} isAnimationActive={false} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <details className="chart-data">
            <summary>View chart data</summary>
            <div className="table-wrapper">
              <table className="cg-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Pass</th>
                    <th>Warning</th>
                    <th>Block</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map(row => (
                    <tr key={row.date}>
                      <td>{row.date}</td>
                      <td>{row.pass_count ?? 'N/A'}</td>
                      <td>{row.warning_count ?? 'N/A'}</td>
                      <td>{row.block_count ?? 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </section>
  );
}
