import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { GitBranch, Database } from 'lucide-react';
import { CodeGateAPI } from '../api/client';

export function RepositoryDetail() {
  const { repositoryId } = useParams<{ repositoryId: string }>();
  const [sysStatus, setSysStatus] = useState<any>(null);

  useEffect(() => {
    CodeGateAPI.getSystemStatus().then(setSysStatus).catch(() => {});
  }, []);

  return (
    <div>
      {/* HERO */}
      <div className="page-hero">
        <div className="page-hero__content">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <p className="page-hero__kicker">REPOSITORY DETAILS</p>
            {sysStatus && (
              <span style={{ 
                fontSize: '11px', fontWeight: 'bold', padding: '2px 8px', borderRadius: '12px',
                backgroundColor: sysStatus.data_mode === 'DEMO' ? 'var(--cg-amber-10)' : 'var(--cg-green-10)',
                color: sysStatus.data_mode === 'DEMO' ? 'var(--cg-amber)' : 'var(--cg-green)',
                border: `1px solid ${sysStatus.data_mode === 'DEMO' ? 'var(--cg-amber-30)' : 'var(--cg-green-30)'}`
              }}>
                <Database size={10} style={{ display: 'inline', marginRight: '4px' }}/>
                {sysStatus.data_mode} MODE
              </span>
            )}
          </div>
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
