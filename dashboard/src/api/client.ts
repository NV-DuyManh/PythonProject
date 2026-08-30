import type { 
  DashboardOverviewResponse, 
  RepositoryDashboardItem, 
  PRDashboardItem, 
  PullRequestDashboardDetail
} from '../types';

const API_BASE_URL = import.meta.env.VITE_CODEGATE_API_URL || 'http://localhost:8000/api/v1';

export class CodeGateAPI {
  static async getOverview(): Promise<DashboardOverviewResponse> {
    const res = await fetch(`${API_BASE_URL}/dashboard/overview`);
    if (!res.ok) throw new Error('Failed to fetch overview');
    return res.json();
  }

  static async getRepositories(): Promise<RepositoryDashboardItem[]> {
    const res = await fetch(`${API_BASE_URL}/dashboard/repositories`);
    if (!res.ok) throw new Error('Failed to fetch repositories');
    return res.json();
  }

  static async getPullRequests(): Promise<PRDashboardItem[]> {
    const res = await fetch(`${API_BASE_URL}/dashboard/pull-requests`);
    if (!res.ok) throw new Error('Failed to fetch PRs');
    return res.json();
  }

  static async getPullRequestDetail(id: number): Promise<PullRequestDashboardDetail> {
    const res = await fetch(`${API_BASE_URL}/dashboard/pull-requests/${id}`);
    if (!res.ok) throw new Error('Failed to fetch PR detail');
    return res.json();
  }
}
