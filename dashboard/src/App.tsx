
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Login } from './pages/Login';
import { Onboarding } from './pages/Onboarding';
import { AppLayout } from './layouts/AppLayout';
import { Overview } from './pages/Overview';
import { Repositories } from './pages/Repositories';
import { RepositoryDetail } from './pages/RepositoryDetail';
import { PullRequests } from './pages/PullRequests';
import { PullRequestDetail } from './pages/PullRequestDetail';
import { Analytics } from './pages/Analytics';
import { Integrations } from './pages/Integrations';
import { GitHubIntegration } from './pages/GitHubIntegration';
import { WorkspaceMembers } from './pages/WorkspaceMembers';
import { AcceptInvite } from './pages/AcceptInvite';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { authenticated, loading, workspaces } = useAuth();
  const location = useLocation();

  if (loading) return null;

  if (!authenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (workspaces.length === 0 && location.pathname !== '/onboarding') {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/invite/:token" element={<AcceptInvite />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<Overview />} />
            <Route path="/repositories" element={<Repositories />} />
            <Route path="/repositories/:repositoryId" element={<RepositoryDetail />} />
            <Route path="/pull-requests" element={<PullRequests />} />
            <Route path="/pull-requests/:pullRequestId" element={<PullRequestDetail />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/integrations/github" element={<GitHubIntegration />} />
            <Route path="/settings/members" element={<WorkspaceMembers />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
