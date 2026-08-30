
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { Overview } from './pages/Overview';
import { Repositories } from './pages/Repositories';
import { RepositoryDetail } from './pages/RepositoryDetail';
import { PullRequests } from './pages/PullRequests';
import { PullRequestDetail } from './pages/PullRequestDetail';
import { Analytics } from './pages/Analytics';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Overview />} />
          <Route path="/repositories" element={<Repositories />} />
          <Route path="/repositories/:repositoryId" element={<RepositoryDetail />} />
          <Route path="/pull-requests" element={<PullRequests />} />
          <Route path="/pull-requests/:pullRequestId" element={<PullRequestDetail />} />
          <Route path="/analytics" element={<Analytics />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
