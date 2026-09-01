import type { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon: LucideIcon;
  title: string;
  description: string;
  children?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, children, className, ...props }: EmptyStateProps) {
  return (
    <div
      className={cn('empty-state', className)}
      {...props}
    >
      <Icon className="empty-state__icon" />
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__desc">{description}</p>
      {children}
    </div>
  );
}
