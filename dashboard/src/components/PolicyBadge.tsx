import { Badge } from './ui/Badge';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

export function PolicyBadge({ decision }: { decision: string }) {
  if (decision === 'PASS') {
    return (
      <Badge variant="success" className="gap-1 px-2 py-0.5 font-mono">
        <ShieldCheck className="h-3 w-3" />
        PASS
      </Badge>
    );
  }
  if (decision === 'WARNING') {
    return (
      <Badge variant="warning" className="gap-1 px-2 py-0.5 font-mono">
        <ShieldAlert className="h-3 w-3" />
        WARNING
      </Badge>
    );
  }
  return (
    <Badge variant="destructive" className="gap-1 px-2 py-0.5 font-mono">
      <ShieldX className="h-3 w-3" />
      BLOCK
    </Badge>
  );
}
