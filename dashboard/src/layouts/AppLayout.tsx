import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  GitBranch,
  GitPullRequest,
  ChartNoAxesCombined,
  Shield,
  Zap,
  Server,
  Settings,
  Database
} from 'lucide-react';

export function AppLayout() {
  const location = useLocation();
  const [sysStatus, setSysStatus] = useState<any>(null);

  useEffect(() => {
    fetch('/api/v1/system/status')
      .then(r => r.json())
      .then(setSysStatus)
      .catch(console.error);
  }, []);

  const navSections = [
    {
      label: 'OVERVIEW',
      items: [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
      ],
    },
    {
      label: 'CODE REVIEW',
      items: [
        { name: 'Repositories', href: '/repositories', icon: GitBranch },
        { name: 'Pull Requests', href: '/pull-requests', icon: GitPullRequest },
      ],
    },
    {
      label: 'INTELLIGENCE',
      items: [
        { name: 'Analytics', href: '/analytics', icon: ChartNoAxesCombined },
      ],
    },
    {
      label: 'SETTINGS',
      items: [
        { name: 'Integrations', href: '/integrations', icon: Settings },
      ],
    },
  ];

  const isActive = (href: string) =>
    location.pathname === href || location.pathname.startsWith(`${href}/`);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar__brand">
          <div className="sidebar__brand-icon">
            <Shield size={20} strokeWidth={2} />
          </div>
          <div className="sidebar__brand-text">
            <span className="sidebar__brand-name">CodeGate</span>
            <span className="sidebar__brand-sub">PR Intelligence Platform</span>
          </div>
        </div>

        <div className="sidebar__status">
          <div className="sidebar__status-title">System Status</div>
          
          <div className="sidebar__status-row">
            <span className="sidebar__status-dot" style={{ background: sysStatus?.system?.status === 'HEALTHY' ? 'var(--cg-success)' : 'var(--cg-warning)' }} />
            <Server size={13} strokeWidth={1.8} />
            <span>API {sysStatus?.system?.status === 'HEALTHY' ? 'Connected' : 'Offline'}</span>
          </div>

          <div className="sidebar__status-row">
            <span className="sidebar__status-dot" style={{ background: sysStatus?.database?.status === 'CONNECTED' ? 'var(--cg-success)' : 'var(--cg-warning)' }} />
            <Database size={13} strokeWidth={1.8} />
            <span>DB {sysStatus?.database?.status === 'CONNECTED' ? 'Connected' : 'Offline'}</span>
          </div>

          <div className="sidebar__status-row">
            <span className="sidebar__status-dot" style={{ background: sysStatus?.github?.status === 'CONNECTED' ? 'var(--cg-success)' : 'var(--cg-danger)' }} />
            <Zap size={13} strokeWidth={1.8} />
            <span>GitHub {sysStatus?.github?.status === 'CONNECTED' ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>

        {navSections.map((section) => (
          <div key={section.label}>
            <div className="sidebar__section">{section.label}</div>
            <nav className="sidebar__nav">
              {section.items.map((item) => (
                <NavLink
                  key={item.href}
                  to={item.href}
                  className={`nav-link${isActive(item.href) ? ' nav-link--active' : ''}`}
                >
                  <item.icon size={18} strokeWidth={1.8} className="nav-link__icon" />
                  {item.name}
                </NavLink>
              ))}
            </nav>
          </div>
        ))}

        <div className="sidebar__footer">
          <div className="sidebar__footer-text">CodeGate v1.0</div>
        </div>
      </aside>

      {/* Content */}
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
