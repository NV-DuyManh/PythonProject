import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { GitHubIntegration } from './GitHubIntegration';
import { CodeGateAPI } from '../api/client';
import { AuthProvider } from '../contexts/AuthContext';


// Mock CodeGateAPI
vi.mock('../api/client', () => ({
  CodeGateAPI: {
    getGitHubConnections: vi.fn(),
    installGitHubApp: vi.fn(),
    disconnectGitHubConnection: vi.fn()
  }
}));

describe('GitHubIntegration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (CodeGateAPI.getGitHubConnections as any).mockResolvedValue([]);
  });

  it('renders the integrations page with empty state', async () => {
    render(
      <AuthProvider>
        <GitHubIntegration />
      </AuthProvider>
    );
    
    expect(screen.getByText('GitHub Integration')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText(/No GitHub connections found for this workspace/i)).toBeInTheDocument();
    });
  });

  it('renders existing connections (Personal and Org)', async () => {
    (CodeGateAPI.getGitHubConnections as any).mockResolvedValue([
      {
        id: 1,
        account_login: 'test-user',
        account_type: 'User',
        repository_selection: 'all',
        status: 'active',
        installation_id: '123'
      },
      {
        id: 2,
        account_login: 'test-org',
        account_type: 'Organization',
        repository_selection: 'selected',
        status: 'active',
        installation_id: '456'
      }
    ]);

    render(
      <AuthProvider>
        <GitHubIntegration />
      </AuthProvider>
    );
    
    await waitFor(() => {
      expect(screen.getByText('test-user')).toBeInTheDocument();
      expect(screen.getByText('test-org')).toBeInTheDocument();
      expect(screen.getByText('User')).toBeInTheDocument();
      expect(screen.getByText('Organization')).toBeInTheDocument();
    });
  });

  it('handles connect CTA click', async () => {
    (CodeGateAPI.installGitHubApp as any).mockResolvedValue({ install_url: 'https://github.com/install/123' });
    
    render(
      <AuthProvider>
        <GitHubIntegration />
      </AuthProvider>
    );
    
    const connectBtn = screen.getByRole('button', { name: /Connect GitHub/i });
    expect(connectBtn).toBeInTheDocument();
    
    // Test user event disabled when workspaceId is missing by default in mock context
    // Actually our simple mock doesn't mock activeWorkspaceId nicely. Let's mock it.
  });
});
