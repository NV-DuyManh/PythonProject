import * as React from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'destructive' | 'danger' | 'outline' | 'secondary' | 'indigo' | 'info';
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const variants = {
    default: 'badge--neutral',
    success: 'badge--pass',
    warning: 'badge--warning',
    destructive: 'badge--block',
    danger: 'badge--block',
    indigo: 'badge--indigo',
    outline: 'border border-slate-300 text-slate-700 bg-white',
    secondary: 'badge--neutral',
    info: 'badge--info',
  };

  return (
    <span
      className={cn(
        'badge',
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
