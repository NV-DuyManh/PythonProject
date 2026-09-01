 import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AcceptInvite } from './AcceptInvite';
import * as AuthContext from '../contexts/AuthContext';

describe('AcceptInvite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  const renderComponent = (authenticated = true) => {
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      authenticated,
      user: authenticated ? { id: 1, username: 'test_user' } : null,
      refresh: vi.fn(),
      setActiveWorkspace: vi.fn(),
    } as any);

    return render(
      <MemoryRouter initialEntries={['/invite/test-token']}>
        <Routes>
          <Route path="/invite/:token" element={<AcceptInvite />} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('shows loading state initially', () => {
    renderComponent();
    expect(screen.getByText(/loading invitation/i)).toBeInTheDocument();
  });

  it('displays invitation details on success', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        team_name: 'Test Team',
        inviter_name: 'Admin',
        role: 'DEVELOPER',
        status: 'PENDING'
      })
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText(/You've been invited!/i)).toBeInTheDocument();
      expect(screen.getByText('Test Team')).toBeInTheDocument();
    });
  });

  it('shows error if invitation is invalid', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invitation expired' })
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('Invalid Invitation')).toBeInTheDocument();
      expect(screen.getByText('Invitation expired')).toBeInTheDocument();
    });
  });

  it('prompts to login if unauthenticated', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        team_name: 'Test Team',
        inviter_name: 'Admin',
        role: 'DEVELOPER',
        status: 'PENDING'
      })
    });

    renderComponent(false);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /log in to accept/i })).toBeInTheDocument();
    });
  });
});
