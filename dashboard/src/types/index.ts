export interface DashboardOverviewResponse {
  repositories_total: number;
  pull_requests_total: number;
  open_pull_requests: number;
  analyses_total: number;
  analyses_completed: number;
  analyses_failed: number;
  average_quality_score: number | null;
  average_risk_score: number | null;
  policy_pass_count: number;
  policy_warning_count: number;
  policy_block_count: number;
  policy_pass_rate: number | null;
  policy_warning_rate: number | null;
  policy_block_rate: number | null;
  tests_passed_runs: number;
  tests_failed_runs: number;
  test_pass_rate: number | null;
  average_line_coverage: number | null;
  average_changed_line_coverage: number | null;
  critical_findings: number;
  high_findings: number;
  high_security_findings: number;
  reviewer_recommendations_generated: number;
  quality_trend: any[];
  risk_trend: any[];
  changed_coverage_trend: any[];
  policy_trend: any[];
}

export interface RepositoryDashboardItem {
  repository_id: number;
  name: string;
  provider: string;
  active: boolean;
  open_pr_count: number;
  analysis_count: number;
  average_quality: number | null;
  average_risk: number | null;
  policy_pass_count: number;
  policy_warning_count: number;
  policy_block_count: number;
  block_rate: number | null;
  test_pass_rate: number | null;
  average_changed_coverage: number | null;
  critical_findings: number;
  last_analysis_at: string | null;
}

export interface PRDashboardItem {
  pull_request_id: number;
  repository: string;
  number: number;
  title: string;
  author: string;
  state: string;
  latest_analysis_id: number | null;
  analysis_status: string | null;
  quality_score: number | null;
  quality_grade: string | null;
  risk_score: number | null;
  risk_level: string | null;
  policy_decision: string | null;
  test_outcome: string | null;
  changed_line_coverage: number | null;
  critical_findings: number;
  high_findings: number;
  updated_at: string;
}

export interface PullRequestDashboardDetail {
  pr: {
    id: number;
    number: number;
    title: string;
    author: string;
    state: string;
    repository: string;
    head_branch?: string;
    head_sha?: string;
  };
  analysis: any;
  quality: any;
  risk: any;
  policy: any;
  tests: any;
  coverage: any;
  findings: any;
  reviewer_recommendation: any;
}
