import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { AuthProvider, useAuth } from './contexts/AuthContext';

// Helper component to expose context
function WorkspaceSwitchTestHarness() {
  const { activeWorkspace, workspaces, setActiveWorkspace, workspaceVersion, authenticated } = useAuth();
  return (
    <div>
      <div data-testid="auth-status">{authenticated ? 'authenticated' : 'unauthenticated'}</div>
      <div data-testid="active-workspace">{activeWorkspace?.name || 'none'}</div>
      <div data-testid="workspace-version">{workspaceVersion}</div>
      <div data-testid="workspace-count">{workspaces.length}</div>
      {workspaces.map(w => (
        <button key={w.id} data-testid={`switch-${w.id}`} onClick={() => setActiveWorkspace(w.id)}>
          Switch to {w.name}
        </button>
      ))}
    </div>
  );
}

const mockWorkspaces = [
  { id: 1, name: 'Workspace Alpha', slug: 'alpha', role: 'owner' },
  { id: 2, name: 'Workspace Beta', slug: 'beta', role: 'member' },
];

const mockUser = (activeWsId: number | null = 1) => ({
  id: 100,
  username: 'testuser',
  display_name: 'Test User',
  avatar_url: null,
  active_workspace_id: activeWsId,
});

describe('WorkspaceSwitch', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders active workspace after auth init', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (url: any) => {
      if (url.toString().includes('/auth/me')) {
        return new Response(JSON.stringify(mockUser(1)), { status: 200 });
      }
      if (url.toString().includes('/workspaces')) {
        return new Response(JSON.stringify(mockWorkspaces), { status: 200 });
      }
      return new Response('', { status: 404 });
    });

    render(
      <AuthProvider>
        <WorkspaceSwitchTestHarness />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
    });

    expect(screen.getByTestId('active-workspace').textContent).toBe('Workspace Alpha');
    expect(screen.getByTestId('workspace-version').textContent).toBe('0');
    expect(screen.getByTestId('workspace-count').textContent).toBe('2');
  });

  it('increments workspaceVersion after switching workspace', async () => {
    let activeId = 1;
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (url: any, opts?: any) => {
      if (url.toString().includes('/activate') && opts?.method === 'POST') {
        // Simulate server-side switch
        const match = url.toString().match(/\/workspaces\/(\d+)\/activate/);
        if (match) activeId = parseInt(match[1]);
        return new Response('', { status: 200 });
      }
      if (url.toString().includes('/auth/me')) {
        return new Response(JSON.stringify(mockUser(activeId)), { status: 200 });
      }
      if (url.toString().includes('/workspaces') && !url.toString().includes('/activate')) {
        return new Response(JSON.stringify(mockWorkspaces), { status: 200 });
      }
      return new Response('', { status: 404 });
    });

    render(
      <AuthProvider>
        <WorkspaceSwitchTestHarness />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('active-workspace').textContent).toBe('Workspace Alpha');
    });

    // Switch to Beta
    const switchBtn = screen.getByTestId('switch-2');
    await act(async () => {
      await userEvent.click(switchBtn);
    });

    await waitFor(() => {
      expect(screen.getByTestId('active-workspace').textContent).toBe('Workspace Beta');
    });

    expect(screen.getByTestId('workspace-version').textContent).toBe('1');
  });

  it('clears user state on logout', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (url: any, _opts?: any) => {
      if (url.toString().includes('/auth/me')) {
        return new Response(JSON.stringify(mockUser(1)), { status: 200 });
      }
      if (url.toString().includes('/workspaces')) {
        return new Response(JSON.stringify(mockWorkspaces), { status: 200 });
      }
      if (url.toString().includes('/auth/logout')) {
        return new Response('', { status: 200 });
      }
      return new Response('', { status: 404 });
    });

    // Mock window.location to prevent actual navigation
    const originalLocation = window.location;
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { ...originalLocation, href: '' },
    });

    function LogoutTestHarness() {
      const { authenticated, activeWorkspace, logout, workspaceVersion } = useAuth();
      return (
        <div>
          <div data-testid="auth-status">{authenticated ? 'authenticated' : 'unauthenticated'}</div>
          <div data-testid="active-workspace">{activeWorkspace?.name || 'none'}</div>
          <div data-testid="workspace-version">{workspaceVersion}</div>
          <button data-testid="logout-btn" onClick={logout}>Logout</button>
        </div>
      );
    }

    render(
      <AuthProvider>
        <LogoutTestHarness />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('auth-status').textContent).toBe('authenticated');
    });

    await act(async () => {
      await userEvent.click(screen.getByTestId('logout-btn'));
    });

    expect(screen.getByTestId('auth-status').textContent).toBe('unauthenticated');
    expect(screen.getByTestId('active-workspace').textContent).toBe('none');
    expect(screen.getByTestId('workspace-version').textContent).toBe('0');

    // Restore window.location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    });
  });
});
