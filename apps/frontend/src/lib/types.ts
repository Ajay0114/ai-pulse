export type ArticleSource = {
  id: string;
  name: string;
  platform?: string | null;
};

export type ArticleCategory = {
  id: string;
  name: string;
  slug: string;
};

export type ArticleTag = {
  id: string;
  name: string;
  slug: string;
};

export type ArticleEntity = {
  id: string;
  name: string;
  entity_type: string;
};

export type ArticleSummary = {
  short_summary: string;
  detailed_summary?: string | null;
  why_it_matters?: string | null;
};

export type Article = {
  id: string;
  source_id: string;
  title: string;
  original_url: string;
  canonical_url?: string | null;
  author?: string | null;
  description?: string | null;
  content?: string | null;
  content_type: string;
  language?: string | null;
  published_at?: string | null;
  discovered_at: string;
  importance_score?: number | null;
  engagement_count?: number | null;
  processing_status: string;
  relevance_status: string;
  relevance_score?: number | null;
  feed_type: string;
  importance_reason?: string | null;
  source: ArticleSource;
  categories: ArticleCategory[];
  tags: ArticleTag[];
  entities: ArticleEntity[];
  summaries: ArticleSummary[];
};

export type ArticleListResponse = {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  articles: Article[];
};

export type Source = {
  id: string;
  name: string;
  source_type: string;
  platform?: string | null;
  base_url?: string | null;
  feed_url?: string | null;
  description?: string | null;
  language?: string | null;
  region?: string | null;
  poll_interval_minutes: number;
  last_fetched_at?: string | null;
  next_fetch_at?: string | null;
  health_status: string;
  consecutive_failures: number;
  priority: number;
  is_active: boolean;
};

export function articleSummary(article: Article): ArticleSummary | undefined {
  return article.summaries?.[0];
}

export function articleKeyPoints(article: Article): string[] {
  const detailed = articleSummary(article)?.detailed_summary;

  if (!detailed) return [];

  return detailed
    .split("\n")
    .map((line) => line.replace(/^-+\s*/, "").trim())
    .filter(Boolean);
}

export function formatDate(value?: string | null) {
  if (!value) return "Date unavailable";

  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
