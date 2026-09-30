import { Link, useOutletContext } from 'react-router-dom';
import { GitBranch, ArrowRight, MessageSquare, Terminal } from 'lucide-react';
import { useState, useEffect } from 'react';
import { CodeGateAPI } from '../api/client';
import { useAuth } from '../contexts/AuthContext';
import { PageHeader } from '../components/ui/PageHeader';
import { Badge } from '../components/ui/Badge';

export function Integrations() {
  const { workspaceVersion } = useAuth();
  const system = useOutletContext<{ sysStatus: any; apiError: boolean } | undefined>();
  const [ghStatus, setGhStatus] = useState<string>('Checking...');

  useEffect(() => {
    if (system) {
      setGhStatus(
        system.apiError
          ? 'Unavailable'
          : !system.sysStatus
          ? 'Checking...'
          : system.sysStatus.github?.status === 'CONNECTED'
          ? 'Configured'
          : 'Not Configured'
      );
      return;
    }
    CodeGateAPI.getSystemStatus()
      .then((sys: any) => {
        setGhStatus(sys?.github?.status === 'CONNECTED' ? 'Configured' : 'Not Configured');
      })
      .catch(() => setGhStatus('Unavailable'));
  }, [workspaceVersion, system]);

  return (
    <div className="page-stack">
      <PageHeader
        title="Integrations"
        description="Connect your git providers, CI/CD runners, and notification channels to power automated reviews."
      />

      <div className="grid grid-cols-1 gap-4">
        {/* Active GitHub Integration */}
        <Link className="service-row group" to="/integrations/github">
          <div className="w-14 h-14 rounded-2xl bg-slate-900 text-white flex items-center justify-center flex-shrink-0 shadow-md group-hover:scale-105 transition-transform">
            <GitBranch size={28} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-base font-bold text-slate-900">GitHub App</h2>
              <Badge variant={ghStatus === 'Configured' ? 'success' : 'default'}>
                {ghStatus === 'Configured' ? 'Active' : 'Setup Required'}
              </Badge>
            </div>
            <p className="muted text-sm">Automated webhooks, repository sync, and pull request analysis bot.</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs font-bold text-slate-500" role="status">
              {ghStatus}
            </span>
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
              <ArrowRight size={16} />
            </div>
          </div>
        </Link>

        {/* Coming Soon Preview Integrations */}
        <div className="service-row opacity-75">
          <div className="w-14 h-14 rounded-2xl bg-orange-50 text-orange-600 border border-orange-100 flex items-center justify-center flex-shrink-0">
            <Terminal size={26} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-base font-bold text-slate-900">GitLab CI & Webhooks</h2>
              <Badge variant="outline">Coming Soon</Badge>
            </div>
            <p className="muted text-sm">Merge request scanning and pipeline feedback for GitLab teams.</p>
          </div>
        </div>

        <div className="service-row opacity-75">
          <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 border border-indigo-100 flex items-center justify-center flex-shrink-0">
            <MessageSquare size={26} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-base font-bold text-slate-900">Discord & Slack Coach Bot</h2>
              <Badge variant="outline">Coming Soon</Badge>
            </div>
            <p className="muted text-sm">Daily review digests and student coaching notifications in your chat channels.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
