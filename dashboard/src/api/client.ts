import type { 
  DashboardOverviewResponse, 
  RepositoryDashboardItem, 
  PRDashboardItem, 
  PullRequestDashboardDetail
} from '../types';
const API_BASE_URL = import.meta.env.VITE_CODEGATE_API_URL || 'http://127.0.0.1:8000/api/v1';

export class CodeGateAPI {
  private static controllers: Record<string, AbortController> = {};

  private static getSignal(key: string): AbortSignal {
    if (this.controllers[key]) {
      this.controllers[key].abort();
    }
    this.controllers[key] = new AbortController();
    return this.controllers[key].signal;
  }

  private static async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    return fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      credentials: 'include',
    });
  }

  static async getSystemStatus(): Promise<{ status: string; database: string; data_mode: string; version: string }> {
    const res = await this.request('/system/status', { signal: this.getSignal('system_status') });
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  }

  static async getOverview(): Promise<DashboardOverviewResponse> {
    const res = await this.request('/dashboard/overview', { signal: this.getSignal('overview') });
    if (!res.ok) throw new Error('Failed to fetch overview');
    return res.json();
  }

  static async getRepositories(): Promise<RepositoryDashboardItem[]> {
    const res = await this.request('/dashboard/repositories', { signal: this.getSignal('repositories') });
    if (!res.ok) throw new Error('Failed to fetch repositories');
    return res.json();
  }

  static async getRepositoryDetail(id: number): Promise<any> {
    const res = await this.request(`/dashboard/repositories/${id}`, { signal: this.getSignal(`repo_detail_${id}`) });
    if (!res.ok) {
      if (res.status === 404) throw new Error('Repository not found');
      throw new Error('Failed to fetch repository detail');
    }
    return res.json();
  }

  static async getPullRequests(): Promise<PRDashboardItem[]> {
    const res = await this.request('/dashboard/pull-requests', { signal: this.getSignal('pull_requests') });
    if (!res.ok) throw new Error('Failed to fetch PRs');
    return res.json();
  }

  static async getPullRequestDetail(id: number): Promise<PullRequestDashboardDetail> {
    const res = await this.request(`/dashboard/pull-requests/${id}`, { signal: this.getSignal(`pr_detail_${id}`) });
    if (!res.ok) throw new Error('Failed to fetch PR detail');
    return res.json();
  }

  static async getGitHubConnections(): Promise<{ 
    id: number; 
    account_login: string; 
    account_type: string;
    status: string; 
    auth_type: string;
    repository_selection: string;
    installation_id: string;
    last_verified_at: string;
    last_sync_status: string;
    last_sync_error: string;
    last_synced_at: string;
  }[]> {
    const res = await this.request('/integrations/github/connections', { signal: this.getSignal('github_connections') });
    if (!res.ok) throw new Error('Failed to fetch GitHub connections');
    return res.json();
  }

  static async installGitHubApp(): Promise<{ install_url: string }> {
    const res = await this.request('/integrations/github/install', { signal: this.getSignal('github_install') });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || 'Failed to initiate GitHub installation');
    }
    return res.json();
  }

  static async verifyGitHubConnection(id: number): Promise<any> {
    const res = await this.request(`/integrations/github/connections/${id}/verify`, { 
      method: 'POST',
      signal: this.getSignal(`github_verify_${id}`) 
    });
    if (!res.ok) throw new Error('Failed to verify connection');
    return res.json();
  }

  static async disconnectGitHubConnection(id: number): Promise<any> {
    const res = await this.request(`/integrations/github/connections/${id}/disconnect`, { 
      method: 'POST',
      signal: this.getSignal(`github_disconnect_${id}`) 
    });
    if (!res.ok) throw new Error('Failed to disconnect connection');
    return res.json();
  }

  static async syncGitHubConnection(id: number): Promise<{ discovered: number; created: number; updated: number; unchanged: number; removed_access: number; failed: number }> {
    const res = await this.request(`/integrations/github/connections/${id}/sync`, { 
      method: 'POST',
      signal: this.getSignal(`github_sync_${id}`) 
    });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to sync repositories');
    }
    return res.json();
  }

  static async retryAnalysis(analysisId: number): Promise<{ status: string }> {
    const res = await this.request(`/analyses/${analysisId}/retry`, { 
      method: 'POST',
      signal: this.getSignal(`retry_analysis_${analysisId}`) 
    });
    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to retry analysis');
    }
    return res.json();
  }
}
