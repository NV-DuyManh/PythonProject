import React from 'react';

interface ScoreCardProps {
  title: string;
  score: number | null;
  label: string | null;
  isRisk?: boolean;
}

export const ScoreCard: React.FC<ScoreCardProps> = ({ title, score, label, isRisk = false }) => {
  if (score === null || score === undefined) {
    return (
      <div className="p-4 rounded-lg bg-[#1a1b1e] border border-gray-800 text-gray-400">
        <h3 className="text-sm font-medium mb-2 uppercase">{title}</h3>
        <p className="text-lg">N/A</p>
      </div>
    );
  }

  const getScoreColor = () => {
    if (isRisk) {
      if (score >= 70) return 'text-red-500';
      if (score >= 40) return 'text-yellow-500';
      return 'text-green-500';
    } else {
      if (score >= 80) return 'text-green-500';
      if (score >= 60) return 'text-yellow-500';
      return 'text-red-500';
    }
  };

  return (
    <div className="p-4 rounded-lg bg-[#1a1b1e] border border-gray-800 flex flex-col justify-between">
      <h3 className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">{title}</h3>
      <div className="flex items-baseline gap-2">
        <span className={`text-3xl font-bold ${getScoreColor()}`}>
          {score.toFixed(0)}
        </span>
        {label && (
          <span className="text-sm px-2 py-0.5 rounded-full bg-gray-800 text-gray-200">
            {label}
          </span>
        )}
      </div>
    </div>
  );
};
