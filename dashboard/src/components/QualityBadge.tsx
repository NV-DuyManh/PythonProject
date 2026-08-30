import { Badge } from './ui/Badge';
import { Sparkles } from 'lucide-react';

export function QualityBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return <span className="text-muted font-mono text-sm">-</span>;
  
  if (score >= 90) {
    return (
      <Badge variant="success" className="gap-1 px-2 py-0.5 font-mono">
        <Sparkles className="h-3 w-3" />
        A
      </Badge>
    );
  }
  if (score >= 80) {
    return (
      <Badge variant="success" className="gap-1 px-2 py-0.5 font-mono opacity-90">
        B
      </Badge>
    );
  }
  if (score >= 70) {
    return (
      <Badge variant="warning" className="gap-1 px-2 py-0.5 font-mono">
        C
      </Badge>
    );
  }
  if (score >= 60) {
    return (
      <Badge variant="warning" className="gap-1 px-2 py-0.5 font-mono opacity-80">
        D
      </Badge>
    );
  }
  return (
    <Badge variant="destructive" className="gap-1 px-2 py-0.5 font-mono">
      F
    </Badge>
  );
}
