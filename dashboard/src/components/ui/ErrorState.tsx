import { AlertTriangle, RefreshCcw } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from './Button';

export interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export function ErrorState({ 
  title = "Unable to load data", 
  description = "There was a problem communicating with the CodeGate API.", 
  onRetry,
  className, 
  ...props 
}: ErrorStateProps) {
  return (
    <div
      className={cn('error-state', className)}
      {...props}
    >
      <AlertTriangle className="error-state__icon" />
      <h3 className="error-state__title">{title}</h3>
      <p className="error-state__desc">{description}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="flex items-center gap-2">
          <RefreshCcw className="h-4 w-4" />
          Retry
        </Button>
      )}
    </div>
  );
}
