import * as React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'destructive' | 'danger' | 'outline' | 'secondary' | 'indigo';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'bg-primary/20 text-primary-foreground border-transparent',
    success: 'bg-success/20 text-success border-success/30',
    warning: 'bg-warning/20 text-warning border-warning/30',
    destructive: 'bg-danger/20 text-danger border-danger/30',
    danger: 'bg-danger/20 text-danger border-danger/30',
    indigo: 'bg-[var(--cg-indigo-10)] text-[var(--cg-indigo)] border-[var(--cg-indigo-30)]',
    outline: 'text-foreground border-border',
    secondary: 'bg-surface-hover text-muted border-border',
  };

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
