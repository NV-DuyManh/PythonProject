import type { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon: LucideIcon;
  title: string;
  description: string;
  children?: React.ReactNode;
  image?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  children,
  className,
  image,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn('empty-state', className)}
      {...props}
    >
      {image ? (
        <img src={image} alt="" className="mascot-state" />
      ) : (
        <div className="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 mb-2">
          <Icon className="empty-state__icon text-indigo-600" />
        </div>
      )}
      <h3 className="empty-state__title">{title}</h3>
      <p className="empty-state__desc">{description}</p>
      {children}
    </div>
  );
}
