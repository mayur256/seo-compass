export interface AnalysisJob {
  job_id: string;
  url: string;
  status: 'QUEUED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
  created_at: string;
  completed_at?: string;
}

export interface Competitor {
  rank: number;
  url: string;
  keyword: string;
  estimated_traffic: number;
}

export interface Keyword {
  keyword: string;
  search_volume: number;
  difficulty: number;
}

export interface ContentDraft {
  page_name: string;
  content: string;
}

export interface AnalysisReport {
  job_id: string;
  competitors: Competitor[];
  keywords: Keyword[];
  content_drafts: ContentDraft[];
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}