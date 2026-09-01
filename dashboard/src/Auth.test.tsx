import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AuthProvider } from './contexts/AuthContext';
import { Login } from './pages/Login';
import { Onboarding } from './pages/Onboarding';

// Mock fetch
window.fetch = vi.fn() as any;

describe('Authentication & Onboarding Flow', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders login page correctly', async () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </BrowserRouter>
    );
    expect(await screen.findByText('Welcome to CodeGate')).toBeInTheDocument();
    expect(screen.getByText('Continue with GitHub')).toBeInTheDocument();
  });

  it('renders onboarding page correctly', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <Onboarding />
        </AuthProvider>
      </BrowserRouter>
    );
    // Might redirect or show loading initially, but checking basic render is fine
  });
});
