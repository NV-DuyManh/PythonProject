import { useId } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend,
  BarChart, Bar } from 'recharts';
import { formatScore } from '../lib/utils';

type TrendPoint = { date: string; value?: number | null };
type Series = { name: string; color: string; points: TrendPoint[] };

export function mergeTrends(series: Series[]) {
  const dates = [...new Set(series.flatMap(item => item.points.map(point => point.date)))].sort();
  return dates.map(date => Object.fromEntries([
    ['date', date],
    ...series.map(item => [item.name, item.points.find(point => point.date === date)?.value ?? null]),
  ]));
}

export function TrendChart({ title, series }: { title: string; series: Series[] }) {
  const id = useId();
  const data = mergeTrends(series);
  return <section className="dashboard-panel" aria-labelledby={id}>
    <div className="section-heading"><h2 id={id}>{title}</h2><span className="muted">Daily averages</span></div>
    {data.length === 0 ? <div className="chart-empty">No historical data available</div> : <>
      <div className="chart-frame">
        <ResponsiveContainer width="100%" height="100%" minWidth={0}>
          <LineChart data={data} margin={{ top: 12, right: 16, left: -20, bottom: 0 }} accessibilityLayer>
            <CartesianGrid vertical={false} stroke="var(--cg-border-soft)" />
            <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} minTickGap={30} />
            <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: 'var(--cg-muted)' }} />
            <Tooltip contentStyle={{ borderRadius: 6, borderColor: 'var(--cg-border)', fontSize: 13 }} />
            <Legend iconType="plainline" wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
            {series.map(item => <Line key={item.name} type="linear" dataKey={item.name} stroke={item.color}
              strokeWidth={2} dot={{ r: 3 }} connectNulls={false} isAnimationActive={false} />)}
          </LineChart>
        </ResponsiveContainer>
      </div>
      {data.length === 1 && <p className="muted">One recorded day. More history is needed to show a trend.</p>}
      <details className="chart-data"><summary>View chart data</summary><div className="table-wrapper">
        <table className="cg-table"><thead><tr><th>Date</th>{series.map(item => <th key={item.name}>{item.name}</th>)}</tr></thead>
          <tbody>{data.map(row => <tr key={String(row.date)}><td>{row.date}</td>{series.map(item => <td key={item.name}>{formatScore(row[item.name] as number | null)}</td>)}</tr>)}</tbody>
        </table>
      </div></details>
    </>}
  </section>;
}

export function DistributionChart({ title, values, colors = {} }: {
  title: string; values: Record<string, number>; colors?: Record<string, string>;
}) {
  const id = useId();
  const total = Object.values(values).reduce((sum, value) => sum + value, 0);
  return <section className="dashboard-panel" aria-labelledby={id}>
    <div className="section-heading"><h2 id={id}>{title}</h2><span className="muted">{total} recorded</span></div>
    {total === 0 ? <div className="chart-empty">No recorded results</div> : <dl className="distribution">
      {Object.entries(values).map(([label, value]) => <div key={label} className="distribution__row">
        <dt>{label}</dt><dd><span className="distribution__track" aria-hidden="true"><span style={{ width: `${value / total * 100}%`, background: colors[label] || 'var(--cg-primary)' }} /></span><strong>{value}</strong></dd>
      </div>)}
    </dl>}
  </section>;
}

export function PolicyTrendChart({ data }: { data: { date: string; pass_count?: number | null; warning_count?: number | null; block_count?: number | null }[] }) {
  return <section className="dashboard-panel" aria-label="Policy history">
    <div className="section-heading"><h2>Policy history</h2><span className="muted">Daily evaluations</span></div>
    {!data.length ? <div className="chart-empty">No policy history available</div> : <>
      <div className="chart-frame"><ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <BarChart data={data} margin={{ top: 8, right: 12, left: -20, bottom: 0 }} accessibilityLayer>
          <CartesianGrid vertical={false} stroke="var(--cg-border-soft)" />
          <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ borderRadius: 6, borderColor: 'var(--cg-border)' }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar dataKey="pass_count" name="Pass" stackId="policy" fill="var(--cg-green)" maxBarSize={40} isAnimationActive={false} />
          <Bar dataKey="warning_count" name="Warning" stackId="policy" fill="var(--cg-amber)" isAnimationActive={false} />
          <Bar dataKey="block_count" name="Block" stackId="policy" fill="var(--cg-red)" isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer></div>
      <details className="chart-data"><summary>View chart data</summary><div className="table-wrapper"><table className="cg-table">
        <thead><tr><th>Date</th><th>Pass</th><th>Warning</th><th>Block</th></tr></thead>
        <tbody>{data.map(row => <tr key={row.date}><td>{row.date}</td><td>{row.pass_count ?? 'N/A'}</td><td>{row.warning_count ?? 'N/A'}</td><td>{row.block_count ?? 'N/A'}</td></tr>)}</tbody>
      </table></div></details>
    </>}
  </section>;
}
