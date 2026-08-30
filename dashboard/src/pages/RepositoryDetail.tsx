import { useParams } from 'react-router-dom';
import { GitBranch } from 'lucide-react';

export function RepositoryDetail() {
  const { repositoryId } = useParams<{ repositoryId: string }>();

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <p className="page-hero__kicker">REPOSITORY DETAILS</p>
          <h2 className="page-hero__title">Repository #{repositoryId}</h2>
          <p className="page-hero__desc">
            View quality, risk, and policy metrics for this repository.
          </p>
        </div>
      </div>

      {/* Placeholder KPI */}
      <div className="dashboard-grid dashboard-grid--stats">
        <div className="stat-card stat-card--green">
          <div className="stat-card__icon"><GitBranch size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Quality</div>
            <div className="stat-card__value">—</div>
          </div>
        </div>
        <div className="stat-card stat-card--amber">
          <div className="stat-card__icon"><GitBranch size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Avg Risk</div>
            <div className="stat-card__value">—</div>
          </div>
        </div>
        <div className="stat-card stat-card--red">
          <div className="stat-card__icon"><GitBranch size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Block Rate</div>
            <div className="stat-card__value">—</div>
          </div>
        </div>
        <div className="stat-card stat-card--blue">
          <div className="stat-card__icon"><GitBranch size={26} strokeWidth={1.8} /></div>
          <div className="stat-card__body">
            <div className="stat-card__label">Coverage</div>
            <div className="stat-card__value">—</div>
          </div>
        </div>
      </div>

      <div className="dashboard-panel">
        <div className="dashboard-panel__head">
          <div className="dashboard-panel__title">Recent Pull Requests</div>
        </div>
        <div className="dashboard-panel__body">
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--cg-muted)', fontSize: '13px' }}>
            Repository-specific PR data will appear here once API support is complete.
          </div>
        </div>
      </div>
    </div>
  );
}
