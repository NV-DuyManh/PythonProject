import { render, screen, fireEvent } from '@testing-library/react';
import { EmptyState } from './EmptyState';
import { ErrorState } from './ErrorState';
import { Skeleton } from './Skeleton';
import { Activity } from 'lucide-react';
import { describe, it, expect, vi } from 'vitest';

describe('UI State Components', () => {
  describe('EmptyState', () => {
    it('renders title and description', () => {
      render(
        <EmptyState 
          icon={Activity} 
          title="No Data Found" 
          description="Please add some data." 
        />
      );
      
      expect(screen.getByText('No Data Found')).toBeInTheDocument();
      expect(screen.getByText('Please add some data.')).toBeInTheDocument();
    });

    it('renders children if provided', () => {
      render(
        <EmptyState icon={Activity} title="Title" description="Description">
          <button>Action Button</button>
        </EmptyState>
      );
      
      expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument();
    });
  });

  describe('ErrorState', () => {
    it('renders error message', () => {
      render(
        <ErrorState 
          title="An error occurred" 
          description="Failed to load." 
        />
      );
      
      expect(screen.getByText('An error occurred')).toBeInTheDocument();
      expect(screen.getByText('Failed to load.')).toBeInTheDocument();
    });

    it('renders retry button and handles click', () => {
      const handleRetry = vi.fn();
      render(
        <ErrorState 
          onRetry={handleRetry}
        />
      );
      
      const retryBtn = screen.getByRole('button', { name: 'Retry' });
      expect(retryBtn).toBeInTheDocument();
      
      fireEvent.click(retryBtn);
      expect(handleRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Skeleton', () => {
    it('renders with default classes', () => {
      const { container } = render(<Skeleton />);
      const skeletonEl = container.firstChild as HTMLElement;
      expect(skeletonEl).toHaveClass('animate-pulse', 'bg-slate-200');
    });

    it('applies custom className', () => {
      const { container } = render(<Skeleton className="w-10 h-10" />);
      const skeletonEl = container.firstChild as HTMLElement;
      expect(skeletonEl).toHaveClass('w-10', 'h-10');
    });
  });
});
