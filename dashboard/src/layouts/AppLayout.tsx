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

  const apiStatusStr = apiError ? 'OFFLINE' : (sysStatus?.status === 'healthy' ? 'READY' : (sysStatus?.status || 'READY'));
  const dbStatusStr = apiError ? 'UNKNOWN' : (sysStatus?.database?.status?.toUpperCase() || 'CONNECTED');
  const ghStatusStr = apiError ? 'UNKNOWN' : (sysStatus?.github?.status?.toUpperCase() || 'NOT_CONFIGURED');

  const getStatusColor = (status: string) => {
    if (status === 'HEALTHY' || status === 'CONNECTED' || status === 'READY') return '#16a34a';
    if (status === 'OFFLINE' || status === 'ERROR' || status === 'DISCONNECTED') return '#dc2626';
    return '#d97706';
  };

  const isDemo = sysStatus?.data_mode === 'DEMO';
  const isLive = sysStatus?.github?.status?.toUpperCase() === 'CONNECTED' && !isDemo;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#f4f7fb]">
      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0b1220] border-r border-white/5 p-4 flex flex-col transition-transform duration-200 lg:static lg:translate-x-0 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex justify-between items-center mb-3 px-1">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/25 shrink-0">
              <Shield size={20} strokeWidth={2.2} />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-white text-[16px] tracking-tight leading-tight">CodeGate</span>
              <span className="text-[11px] text-slate-400 font-medium">Local PR Quality Platform</span>
            </div>
          </div>
          <button 
            className="lg:hidden text-slate-400 hover:text-white p-1"
            onClick={() => setMobileMenuOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-3 bg-white/[0.04] border border-white/10 rounded-2xl my-3">
          <div className="text-[10px] font-bold text-slate-400 tracking-wider uppercase mb-2">System Status</div>

          <div className="flex items-center gap-2 text-[12px] text-slate-200 mb-1.5 font-medium">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: getStatusColor(apiStatusStr) }} />
            <Server size={13} className="text-slate-400" />
            <span className="capitalize">API {apiStatusStr.toLowerCase()}</span>
          </div>

          <div className="flex items-center gap-2 text-[12px] text-slate-200 mb-1.5 font-medium">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: getStatusColor(dbStatusStr) }} />
            <Database size={13} className="text-slate-400" />
            <span className="capitalize">DB {dbStatusStr.toLowerCase()}</span>
          </div>

          <div className="flex items-center gap-2 text-[12px] text-slate-200 font-medium">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: getStatusColor(ghStatusStr) }} />
            <Zap size={13} className="text-slate-400" />
            <span className="capitalize">GitHub {ghStatusStr.toLowerCase()}</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {navSections.map((section) => (
            <div key={section.label}>
              <div className="px-2 mb-1.5 text-[11px] font-bold text-slate-400/90 tracking-wider uppercase">{section.label}</div>
              <nav className="space-y-1">
                {section.items.map((item) => (
                  <NavLink
                    key={item.href}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-semibold transition-all ${
                      isActive(item.href)
                        ? 'bg-indigo-600/25 text-white border border-indigo-500/40 shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-white/[0.06]'
                    }`}
                  >
                    <item.icon size={17} className={isActive(item.href) ? 'text-indigo-400' : 'text-slate-400'} />
                    {item.name}
                  </NavLink>
                ))}
              </nav>
            </div>
          ))}
        </div>

        <div className="pt-3 mt-auto border-t border-white/5 text-center">
          <div className="text-[11px] text-slate-400/70 font-medium">CodeGate v1.0</div>
        </div>
      </aside>

      {/* Content Area */}
      <div className="flex flex-col flex-1 h-screen overflow-hidden min-w-0">
        {/* Global Header */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between shrink-0 shadow-sm z-20">
          <div className="flex items-center gap-4">
            <button 
              className="lg:hidden text-slate-600 hover:text-slate-900"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu size={22} />
            </button>
            <div className="relative">
              <button 
                onClick={() => setShowWorkspaceMenu(!showWorkspaceMenu)}
                className="flex items-center gap-2 text-sm font-bold text-slate-800 hover:text-indigo-600 px-3 py-1.5 rounded-lg hover:bg-slate-100/80 transition-colors border border-slate-200/60 shadow-xs"
              >
                {activeWorkspace?.name || 'Select Workspace'}
                <ChevronDown size={15} className="text-slate-400" />
              </button>
              
              {showWorkspaceMenu && (
                <div className="absolute top-full left-0 mt-1.5 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-3.5 py-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    Workspaces
                  </div>
                  {workspaces.map(w => (
                    <button
                      key={w.id}
                      onClick={() => {
                        setActiveWorkspace(w.id);
                        setShowWorkspaceMenu(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm transition-colors flex items-center justify-between ${
                        activeWorkspace?.id === w.id ? 'text-indigo-600 font-bold bg-indigo-50/70' : 'text-slate-600 font-medium hover:bg-slate-50'
                      }`}
                    >
                      <span>{w.name}</span>
                      {activeWorkspace?.id === w.id && <span className="w-1.5 h-1.5 rounded-full bg-indigo-600" />}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="flex items-center gap-2">
              {isDemo && (
                <Badge variant="warning" className="px-3 py-1 font-bold text-xs">
                  DEMO DATA
                </Badge>
              )}
              {isLive && (
                <Badge variant="success" className="px-3 py-1 font-bold text-xs">
                  LIVE GITHUB
                </Badge>
              )}
            </div>
            
            <div className="relative border-l border-slate-200 pl-4 sm:pl-6">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2.5 focus:outline-none p-1 rounded-xl hover:bg-slate-50 transition-colors"
              >
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-slate-200 shadow-xs" />
                ) : (
                  <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-xs shadow-xs">
                    {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
                  </div>
                )}
                <div className="flex flex-col items-start hidden sm:flex text-left">
                  <span className="text-sm font-bold text-slate-800 leading-tight">{user?.display_name || user?.username || 'User'}</span>
                  <span className="text-xs text-slate-500 font-medium leading-tight">@{user?.username || 'user'}</span>
                </div>
                <ChevronDown size={14} className="text-slate-400" />
              </button>

              {showUserMenu && (
                <div className="absolute top-full right-0 mt-1.5 w-52 bg-white border border-slate-200 rounded-2xl shadow-xl py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
                  <div className="px-4 py-2 border-b border-slate-100 mb-1">
                    <p className="text-xs font-semibold text-slate-500">Signed in as</p>
                    <p className="text-sm font-bold text-slate-800 truncate">{user?.display_name || user?.username}</p>
                  </div>
                  <button
                    onClick={() => logout()}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50/80 flex items-center gap-2.5 font-semibold transition-colors"
                  >
                    <LogOut size={15} />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>
        
        <main className="flex-1 overflow-y-auto p-6 min-w-0 bg-[#f4f7fb]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
