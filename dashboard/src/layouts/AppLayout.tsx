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
  Database,
  LogOut,
  ChevronDown,
  Users,
  Menu,
  X
} from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { useAuth } from '../contexts/AuthContext';

export function AppLayout() {
  const { user, workspaces, activeWorkspace, setActiveWorkspace, logout } = useAuth();
  const location = useLocation();
  const [sysStatus, setSysStatus] = useState<any>(null);
  const [apiError, setApiError] = useState(false);
  const [showWorkspaceMenu, setShowWorkspaceMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
        { name: 'Workspace Members', href: '/settings/members', icon: Users },
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
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${mobileMenuOpen ? 'sidebar--mobile-open' : ''}`}>
        <div className="flex justify-between items-center mb-1">
          <div className="sidebar__brand">
          <div className="sidebar__brand-icon">
            <Shield size={20} strokeWidth={2} />
          </div>
          <div className="sidebar__brand-text">
            <span className="sidebar__brand-sub">Local PR Quality Platform</span>
          </div>
        </div>
        <button 
          className="lg:hidden text-slate-400 hover:text-white"
          onClick={() => setMobileMenuOpen(false)}
        >
          <X size={20} />
        </button>
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
                  onClick={() => setMobileMenuOpen(false)}
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
      <div className="flex flex-col flex-1 h-screen overflow-hidden min-w-0">
        {/* Global Header */}
        <header className="topbar shrink-0">
          <div className="flex items-center gap-4">
            <button 
              className="lg:hidden text-slate-600 hover:text-slate-900"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu size={24} />
            </button>
            <div className="relative">
              <button 
                onClick={() => setShowWorkspaceMenu(!showWorkspaceMenu)}
                className="flex items-center gap-2 text-sm font-semibold text-slate-700 hover:text-indigo-600 px-3 py-1.5 rounded-md hover:bg-slate-100 transition-colors"
              >
                {activeWorkspace?.name || 'Select Workspace'}
                <ChevronDown size={16} />
              </button>
              
              {showWorkspaceMenu && (
                <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-slate-200 rounded-xl shadow-lg py-1 z-50">
                  <div className="px-3 py-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Workspaces
                  </div>
                  {workspaces.map(w => (
                    <button
                      key={w.id}
                      onClick={() => {
                        setActiveWorkspace(w.id);
                        setShowWorkspaceMenu(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 ${
                        activeWorkspace?.id === w.id ? 'text-indigo-600 font-bold bg-indigo-50/50' : 'text-slate-600 font-medium'
                      }`}
                    >
                      {w.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="flex items-center gap-2 sm:gap-4">
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
            </div>
            
            <div className="relative border-l border-slate-200 pl-4 sm:pl-6">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 focus:outline-none"
              >
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-slate-200" />
                ) : (
                  <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold">
                    {user?.username.charAt(0).toUpperCase()}
                  </div>
                )}
                <div className="flex flex-col items-start hidden sm:flex">
                  <span className="text-sm font-bold text-slate-800">{user?.display_name || user?.username}</span>
                  <span className="text-xs text-slate-500 font-medium">@{user?.username}</span>
                </div>
                <ChevronDown size={14} className="text-slate-400" />
              </button>

              {showUserMenu && (
                <div className="absolute top-full right-0 mt-1 w-48 bg-white border border-slate-200 rounded-xl shadow-lg py-1 z-50">
                  <button
                    onClick={() => logout()}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 font-medium"
                  >
                    <LogOut size={16} />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>
        
        <main className="content overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
