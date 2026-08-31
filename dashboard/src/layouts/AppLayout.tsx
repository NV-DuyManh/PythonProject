import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { CodeGateAPI } from '../api/client';
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
import { Badge } from '../components/ui/Badge';

export function AppLayout() {
  const location = useLocation();
  const [sysStatus, setSysStatus] = useState<any>(null);
  const [apiError, setApiError] = useState(false);

  useEffect(() => {
    CodeGateAPI.getSystemStatus()
      .then(data => {
        setSysStatus(data);
        setApiError(false);
      })
      .catch((e) => {
        console.error(e);
        setApiError(true);
      });
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

  const apiStatusStr = apiError ? 'OFFLINE' : (sysStatus?.status === 'healthy' ? 'READY' : (sysStatus?.status || 'UNKNOWN'));
  
  // If API is offline, everything downstream is UNKNOWN
  const dbStatusStr = apiError ? 'UNKNOWN' : (sysStatus?.database?.status?.toUpperCase() || 'UNKNOWN');
  const ghStatusStr = apiError ? 'UNKNOWN' : (sysStatus?.github?.status?.toUpperCase() || 'UNKNOWN');

  const getStatusColor = (status: string) => {
    if (status === 'HEALTHY' || status === 'CONNECTED' || status === 'READY') return 'var(--cg-success)';
    if (status === 'OFFLINE' || status === 'ERROR' || status === 'DISCONNECTED') return 'var(--cg-danger)';
    return 'var(--cg-warning)';
  };

  const isDemo = sysStatus?.data_mode === 'DEMO';
  const isLive = sysStatus?.github?.status?.toUpperCase() === 'CONNECTED' && !isDemo;

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
            <span className="sidebar__status-dot" style={{ background: getStatusColor(apiStatusStr) }} />
            <Server size={13} strokeWidth={1.8} />
            <span className="capitalize">API {apiStatusStr.toLowerCase()}</span>
          </div>

          <div className="sidebar__status-row">
            <span className="sidebar__status-dot" style={{ background: getStatusColor(dbStatusStr) }} />
            <Database size={13} strokeWidth={1.8} />
            <span className="capitalize">DB {dbStatusStr.toLowerCase()}</span>
          </div>

          <div className="sidebar__status-row">
            <span className="sidebar__status-dot" style={{ background: getStatusColor(ghStatusStr) }} />
            <Zap size={13} strokeWidth={1.8} />
            <span className="capitalize">GitHub {ghStatusStr.toLowerCase()}</span>
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

      {/* Content Area */}
      <div className="flex flex-col flex-1 h-screen overflow-hidden">
        {/* Global Header */}
        <header className="h-14 border-b border-border bg-background flex items-center justify-between px-8 shrink-0 z-10 shadow-sm">
          <div className="text-sm font-medium text-muted">
            {location.pathname.split('/')[1]?.toUpperCase() || 'DASHBOARD'}
          </div>
          <div className="flex items-center gap-4">
            {isDemo && (
              <Badge variant="warning" className="px-3 py-1 font-bold">
                DEMO DATA
              </Badge>
            )}
            {isLive && (
              <Badge variant="success" className="px-3 py-1 font-bold">
                LIVE GITHUB
              </Badge>
            )}
            {!isDemo && !isLive && (
              <Badge variant="default" className="px-3 py-1 font-bold">
                DATA: UNKNOWN
              </Badge>
            )}
          </div>
        </header>
        
        <main className="content overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
