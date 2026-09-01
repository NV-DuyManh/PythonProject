import { Link } from 'react-router-dom';
import { GitBranch } from 'lucide-react';
import { useState, useEffect } from 'react';
import { CodeGateAPI } from '../api/client';
import { useAuth } from '../contexts/AuthContext';

export function Integrations() {
  const { workspaceVersion } = useAuth();
  const [ghStatus, setGhStatus] = useState<string>('Checking...');

  useEffect(() => {
    CodeGateAPI.getSystemStatus().then((sys: any) => {
      if (sys?.github?.status === 'CONNECTED') {
        setGhStatus('Configured');
      } else {
        setGhStatus('Not Configured');
      }
    }).catch(() => setGhStatus('Unknown'));
  }, [workspaceVersion]);

  return (
    <div className="flex flex-col gap-6">
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">INTEGRATIONS</p>
          <h2 className="page-hero__title">Connected Services</h2>
          <p className="page-hero__desc">Manage your VCS providers, CI/CD, and identity services.</p>
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid--stats">
        <Link to="/integrations/github" className="stat-card" style={{ textDecoration: 'none', cursor: 'pointer', transition: 'transform 0.15s, box-shadow 0.15s' }}>
          <div className="stat-card__icon"><GitBranch size={28} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">GitHub App</div>
            <div className="stat-card__value" style={{ fontSize: '20px' }}>{ghStatus}</div>
            <div className="stat-card__note">Manage repositories and permissions</div>
          </div>
        </Link>

      </div>
    </div>
  );
}
