import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { WorkspaceMembers } from './WorkspaceMembers';
import * as AuthContext from '../contexts/AuthContext';

const mockMembers = [
  { user_id: 1, github_login: 'admin_user', role: 'ADMIN', joined_at: '2023-01-01' },
  { user_id: 2, github_login: 'dev_user', role: 'DEVELOPER', joined_at: '2023-01-02' }
];

const mockInvitations = [
  { id: 1, role: 'REVIEWER', invitee_email: 'test@example.com', status: 'PENDING', expires_at: '2023-12-31' }
];

describe('WorkspaceMembers', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    globalThis.fetch = vi.fn();
  });

  const renderComponent = (role = 'ADMIN') => {
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      authenticated: true,
      user: { id: 1, username: 'admin_user' },
      activeWorkspace: { id: 1, name: 'Test WS', role },
    } as any);

    return render(
      <BrowserRouter>
        <WorkspaceMembers />
      </BrowserRouter>
    );
  };

  it('renders member list', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ members: mockMembers, invitations: mockInvitations })
    });

    renderComponent();

    await waitFor(() => {
      expect(screen.getByText('admin_user')).toBeInTheDocument();
      expect(screen.getByText('dev_user')).toBeInTheDocument();
    });
  });

  it('hides Invite button for non-admins/non-maintainers', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ members: mockMembers, invitations: [] })
    });

    renderComponent('DEVELOPER');

    await waitFor(() => {
      expect(screen.queryByText('Invite Teammate')).not.toBeInTheDocument();
    });
  });

  it('shows Invite button for maintainers but excludes ADMIN role option', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ members: mockMembers, invitations: [] })
    });

    renderComponent('MAINTAINER');

    await waitFor(() => {
      expect(screen.getByText('Invite Teammate')).toBeInTheDocument();
    });
    
    // Open modal
    fireEvent.click(screen.getByText('Invite Teammate'));
    
    // Verify options
    // The invite modal select is the last one on the screen since members have their own selects
    const selects = screen.getAllByRole('combobox');
    const select = selects[selects.length - 1];
    expect(select.innerHTML).not.toContain('ADMIN');
    expect(select.innerHTML).toContain('MAINTAINER');
    expect(select.innerHTML).toContain('REVIEWER');
  });

  it('shows all roles for admins', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ members: mockMembers, invitations: [] })
    });

    renderComponent('ADMIN');

    await waitFor(() => {
      expect(screen.getByText('Invite Teammate')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Invite Teammate'));
    
    const selects = screen.getAllByRole('combobox');
    const select = selects[selects.length - 1];
    expect(select.innerHTML).toContain('ADMIN');
  });

  it('shows pending invites for admins and maintainers', async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ members: mockMembers, invitations: mockInvitations })
    });

    renderComponent('ADMIN');

    await waitFor(() => {
      expect(screen.getByText('Pending Invitations')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });
});
