import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { AuthProvider } from './contexts/AuthContext';
import { PullRequestDetail } from './pages/PullRequestDetail';
import { RepositoryDetail } from './pages/RepositoryDetail';
import { Integrations } from './pages/Integrations';
import { CodeGateAPI } from './api/client';
import type { PullRequestDashboardDetail } from './types';


// CodeGateAPI is mocked below

vi.mock('./api/client', () => ({
  CodeGateAPI: {
    getPullRequestDetail: vi.fn(),
    getSystemStatus: vi.fn(),
    getRepositoryDetail: vi.fn(),
  },
}));

vi.mock('./contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, username: 'testuser', display_name: 'Test User' },
    activeWorkspace: { id: 1, name: 'Test Workspace' },
    workspaces: [{ id: 1, name: 'Test Workspace' }],
    authenticated: true,
    loading: false,
    logout: vi.fn(),
    handleSetActiveWorkspace: vi.fn(),
  }),
  AuthProvider: ({ children }: any) => <>{children}</>
}));

describe('Phase 3 Final Acceptance Tests', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  describe('System Status Offline Semantics (AppLayout)', () => {
    it('infers downstream UNKNOWN if API is OFFLINE', async () => {
      // Mock API offline via CodeGateAPI
      vi.mocked(CodeGateAPI.getSystemStatus).mockRejectedValueOnce(new Error('Network offline'));
      
      render(
        <MemoryRouter>
          <AuthProvider>
            <AppLayout />
          </AuthProvider>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText(/API\s+offline/i)).toBeInTheDocument();
        expect(screen.getByText(/DB\s+unknown/i)).toBeInTheDocument();
        expect(screen.getByText(/GitHub\s+unknown/i)).toBeInTheDocument();
      });
    });

    it('shows LIVE GITHUB if API is connected and data_mode is not DEMO', async () => {
      vi.mocked(CodeGateAPI.getSystemStatus).mockResolvedValueOnce({
        status: 'healthy',
        data_mode: 'LIVE',
        database: { status: 'connected' },
        github: { status: 'CONNECTED' },
      } as any);
      
      render(
        <MemoryRouter>
          <AuthProvider>
            <AppLayout />
          </AuthProvider>
        </MemoryRouter>
      );
      
      await waitFor(() => {
        expect(screen.getByText(/API\s+ready/i)).toBeInTheDocument();
        expect(screen.getByText(/DB\s+connected/i)).toBeInTheDocument();
        expect(screen.getByText(/GitHub\s+connected/i)).toBeInTheDocument();
        expect(screen.getByText(/LIVE GITHUB/i)).toBeInTheDocument();
      });
    });
  });

  describe('Null Coverage Formatting (PullRequestDetail)', () => {
    it('renders "—" when coverage is null', async () => {
      vi.mocked(CodeGateAPI.getPullRequestDetail).mockResolvedValue({
        pr: {
          pull_request_id: '123',
          repository: 'owner/repo',
          number: 1,
          title: 'Title',
          state: 'open',
          author: 'user',
        },
        coverage: { changed_coverage: null }, // Critical test point
      } as unknown as PullRequestDashboardDetail);

      render(
        <MemoryRouter initialEntries={['/pr/123']}>
          <AuthProvider>
            <Routes>
              <Route path="/pr/:pullRequestId" element={<PullRequestDetail />} />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      await waitFor(() => {
        // Since coverage is null, formatPercentage(null) should output "—"
        expect(screen.getByText('—')).toBeInTheDocument();
      });
    });
  });

  describe('Integrations Secret-Safe Rendering', () => {
    it('renders Integrations page without leaking secrets', async () => {
      vi.mocked(CodeGateAPI.getSystemStatus).mockResolvedValue({
        github: { status: 'CONNECTED', secret_token: 'SUPER_SECRET_TOKEN_123' },
      } as any);

      render(<MemoryRouter><Integrations /></MemoryRouter>);

      await waitFor(() => {
        // The word Configured should be present
        expect(screen.getByText('Configured')).toBeInTheDocument();
        // The token must not be in the document
        expect(screen.queryByText('SUPER_SECRET_TOKEN_123')).not.toBeInTheDocument();
      });
    });
  });

  describe('Repository Detail', () => {
    it('renders real repository detail with empty PR state', async () => {
      // Mock CodeGateAPI.getRepositoryDetail
      vi.spyOn(CodeGateAPI, 'getRepositoryDetail').mockResolvedValueOnce({
        repository: { name: 'codegate-demo', active: true, provider: 'GITHUB' },
        health: { average_quality: 98, last_analysis_at: '2026-08-31T00:00:00Z' },
        recent_prs: [],
      });

      render(
        <MemoryRouter initialEntries={['/repositories/456']}>
          <Routes>
            <Route path="/repositories/:repositoryId" element={<RepositoryDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('codegate-demo')).toBeInTheDocument();
        // Uses the real EmptyState component
        expect(screen.getByText('No pull requests')).toBeInTheDocument();
      });
    });

    it('renders error state on API failure', async () => {
      vi.spyOn(CodeGateAPI, 'getRepositoryDetail').mockRejectedValueOnce(new Error('Repository not found'));

      render(
        <MemoryRouter initialEntries={['/repositories/456']}>
          <Routes>
            <Route path="/repositories/:repositoryId" element={<RepositoryDetail />} />
          </Routes>
        </MemoryRouter>
      );

      await waitFor(() => {
        expect(screen.getByText('Unable to load repository')).toBeInTheDocument();
        expect(screen.getByText('Repository not found')).toBeInTheDocument();
      });
    });
  });
});
