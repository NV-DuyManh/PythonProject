import { Badge } from './ui/Badge';
import { AlertTriangle, AlertCircle, Shield } from 'lucide-react';

export function RiskBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return <span className="text-muted font-mono text-sm">-</span>;
  
  if (score >= 75) {
    return (
      <Badge variant="destructive" className="gap-1 px-2 py-0.5 font-mono">
        <AlertTriangle className="h-3 w-3" />
        HIGH
      </Badge>
    );
  }
  if (score >= 50) {
    return (
      <Badge variant="warning" className="gap-1 px-2 py-0.5 font-mono">
        <AlertCircle className="h-3 w-3" />
        MEDIUM
      </Badge>
    );
  }
  return (
    <Badge variant="success" className="gap-1 px-2 py-0.5 font-mono">
      <Shield className="h-3 w-3" />
      LOW
    </Badge>
  );
}
