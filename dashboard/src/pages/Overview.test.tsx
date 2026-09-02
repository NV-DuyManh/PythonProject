import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { Overview } from './Overview';
import { CodeGateAPI } from '../api/client';
import type { DashboardOverviewResponse } from '../types';

vi.mock('../api/client', () => ({
  CodeGateAPI: {
    getOverview: vi.fn(),
    getSystemStatus: vi.fn(),
  },
}));

vi.mock('../contexts/AuthContext', () => ({
  useAuth: vi.fn(() => ({ 
    workspaceVersion: 0,
    activeWorkspace: { id: 1, name: 'Test' },
    authLoading: false
  })),
}));

describe('Overview Dashboard Page', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders loading skeletons initially', () => {
    vi.mocked(CodeGateAPI.getOverview).mockReturnValue(new Promise(() => {}));
    const { container } = render(<Overview />);
    expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  it('renders error state on API failure', async () => {
    vi.mocked(CodeGateAPI.getOverview).mockRejectedValue(new Error('Network error'));
    render(<Overview />);
    await waitFor(() => {
      expect(screen.getByText('Unable to load data')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('renders empty state when no data exists', async () => {
    vi.mocked(CodeGateAPI.getOverview).mockResolvedValue({
      analyses_total: 0,
      open_pull_requests: 0,
      pull_requests_total: 0,
      average_quality_score: null,
      average_risk_score: null,
      average_changed_line_coverage: null,
      policy_block_count: 0,
      policy_block_rate: null,
      test_pass_rate: null,
      tests_passed_runs: 0,
      tests_failed_runs: 0,
      policy_pass_count: 0,
      policy_pass_rate: null,
      policy_warning_count: 0,
      quality_grade_distribution: {},
      risk_level_distribution: {},
      quality_trend: [],
      risk_trend: [],
      changed_coverage_trend: [],
      reviewer_recommendations_generated: 12,
      critical_findings: 0,
    } as unknown as DashboardOverviewResponse);

    render(<Overview />);
    await waitFor(() => {
      expect(screen.getByText('No analysis data yet')).toBeInTheDocument();
      expect(screen.getByText('Connect a repository or analyze a Pull Request to populate the dashboard.')).toBeInTheDocument();
    });
  });

  it('renders dashboard correctly with mock data', async () => {
    vi.mocked(CodeGateAPI.getOverview).mockResolvedValue({
      analyses_total: 10,
      open_pull_requests: 5,
      pull_requests_total: 10,
      average_quality_score: 84.9,
      average_risk_score: 42.2,
      average_changed_line_coverage: 44.4,
      policy_block_count: 2,
      policy_block_rate: 20.0,
      test_pass_rate: 80.0,
      tests_passed_runs: 8,
      tests_failed_runs: 2,
      policy_pass_count: 6,
      policy_pass_rate: 60.0,
      policy_warning_count: 2,
      quality_grade_distribution: { A: 4, B: 3, C: 2, D: 1 },
      risk_level_distribution: { LOW: 6, MEDIUM: 2, HIGH: 2 },
      quality_trend: [],
      risk_trend: [],
      changed_coverage_trend: [],
      critical_findings: 1,
    } as unknown as DashboardOverviewResponse);

    render(<Overview />);
    await waitFor(() => {
      expect(screen.getAllByText('84.9').length).toBeGreaterThan(0);
      expect(screen.getAllByText('42.2').length).toBeGreaterThan(0);
      expect(screen.getAllByText('44.4%').length).toBeGreaterThan(0);
      expect(screen.getAllByText('20.0%').length).toBeGreaterThan(0);
    });
  });
});
