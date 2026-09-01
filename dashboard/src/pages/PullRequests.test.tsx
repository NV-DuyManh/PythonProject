import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { PullRequests } from './PullRequests';
import { CodeGateAPI } from '../api/client';
import { MemoryRouter } from 'react-router-dom';

vi.mock('../api/client', () => ({
  CodeGateAPI: {
    getPullRequests: vi.fn(),
  },
}));

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(() => ({ workspaceVersion: 0 })),
}));

describe('PullRequests Page', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders error state on API failure', async () => {
    vi.mocked(CodeGateAPI.getPullRequests).mockRejectedValue(new Error('Network error'));
    render(<MemoryRouter><PullRequests /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('renders empty state when no pull requests exist', async () => {
    vi.mocked(CodeGateAPI.getPullRequests).mockResolvedValue([]);
    render(<MemoryRouter><PullRequests /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('No pull requests yet')).toBeInTheDocument();
      expect(screen.getByText(/after CodeGate receives a GitHub webhook/)).toBeInTheDocument();
    });
  });

  it('renders table correctly with mock data', async () => {
    vi.mocked(CodeGateAPI.getPullRequests).mockResolvedValue([
      {
        pull_request_id: 'pr-1',
        repository: 'owner/repo1',
        number: 123,
        title: 'Fix bug',
        state: 'open',
        author: 'johndoe',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-02T00:00:00Z',
        quality_score: 85.5,
        quality_grade: 'A',
        risk_score: 20.0,
        risk_level: 'LOW',
        policy_decision: 'PASS',
        test_outcome: 'PASSED',
        changed_line_coverage: 75.4,
        critical_findings: 0,
        high_findings: 1,
      } as unknown as any
    ]);

    render(<MemoryRouter><PullRequests /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Fix bug')).toBeInTheDocument();
      expect(screen.getByText('owner/repo1')).toBeInTheDocument();
      expect(screen.getByText('johndoe')).toBeInTheDocument();
      expect(screen.getByText('A')).toBeInTheDocument();
      expect(screen.getByText('LOW')).toBeInTheDocument();
      expect(screen.getByText('PASS')).toBeInTheDocument();
      expect(screen.getByText('75.4%')).toBeInTheDocument();
      expect(screen.getByText('1')).toBeInTheDocument();
    });
  });
});
