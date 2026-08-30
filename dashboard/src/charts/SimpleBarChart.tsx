import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface SimpleBarChartProps {
  data: any[];
  xKey: string;
  yKey: string;
  color?: string;
}

export const SimpleBarChart: React.FC<SimpleBarChartProps> = ({ data, xKey, yKey, color = '#3b82f6' }) => {
  if (!data || data.length === 0) {
    return <div className="h-full flex items-center justify-center text-gray-500">No data available</div>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <XAxis dataKey={xKey} stroke="#8b949e" fontSize={12} tickLine={false} axisLine={false} />
        <YAxis stroke="#8b949e" fontSize={12} tickLine={false} axisLine={false} />
        <Tooltip 
          contentStyle={{ backgroundColor: '#1c2128', border: '1px solid #30363d', borderRadius: '6px' }}
          itemStyle={{ color: '#c9d1d9' }}
        />
        <Bar dataKey={yKey} fill={color} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
};
