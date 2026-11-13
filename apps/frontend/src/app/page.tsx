"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import ArticleCard from "@/components/ArticleCard";
import { Article, ArticleListResponse, Source } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function Home() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [totalArticles, setTotalArticles] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadArticles = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: "10",
        sort_by: "newest",
      });

      if (search.trim()) params.set("search", search.trim());

      const response = await fetch(`${API}/articles/?${params}`);

      if (!response.ok) {
        throw new Error(`Article API returned HTTP ${response.status}`);
      }

      const data: ArticleListResponse = await response.json();

      setArticles(data.articles ?? []);
      setTotalArticles(data.total ?? 0);
      setTotalPages(data.total_pages ?? 1);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load articles."
      );
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  useEffect(() => {
    async function loadSources() {
      try {
        const response = await fetch(`${API}/sources/?skip=0&limit=100`);
        if (!response.ok) return;

        const data = await response.json();
        setSources(data.items ?? []);
      } catch {
        // Source statistics remain unavailable if the API cannot be reached.
      }
    }

    loadSources();
  }, []);

  function handleSearch(value: string) {
    setSearch(value);
    setPage(1);
  }

  return (
    <div className="min-h-screen bg-[#f5f7fb] text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />

        <main className="min-w-0 flex-1">
          <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
            <div>
              <p className="text-sm text-slate-500">Workspace / Overview</p>
              <h2 className="mt-1 text-2xl font-bold tracking-tight">
                AI Intelligence Dashboard
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-medium text-emerald-700">
                ● Live data
              </span>
              <button
                onClick={loadArticles}
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
              >
                ↻ Refresh
              </button>
            </div>
          </header>

          <div className="mx-auto max-w-[1500px] space-y-7 px-6 py-8 lg:px-10">
            <section>
              <p className="text-sm text-slate-500">
                Your global AI news monitoring centre
              </p>
              <h3 className="mt-1 text-xl font-semibold">
                Welcome to AI Pulse
              </h3>
              <p className="mt-1 text-sm text-slate-500">
                Discover developments across AI research, companies, models,
                products and technology.
              </p>
            </section>

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="Articles collected"
                value={totalArticles.toLocaleString()}
                detail="Relevant, AI Pulse-reviewed stories"
                icon="▤"
              />
              <StatCard
                label="Registered sources"
                value={sources.length.toString()}
                detail="Configured publishers and feeds"
                icon="◎"
              />
              <StatCard
                label="Healthy sources"
                value={sources.filter((s) => s.health_status === "healthy").length.toString()}
                detail="Last recorded source status"
                icon="✓"
              />
              <StatCard
                label="Current page"
                value={`${page} / ${totalPages}`}
                detail="Article feed pagination"
                icon="◷"
              />
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                <div>
                  <h3 className="text-lg font-semibold">Latest AI developments</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Recently collected stories from across the AI ecosystem.
                  </p>
                </div>
                <div className="relative w-full sm:max-w-sm">
                  <span className="absolute left-3 top-2.5 text-slate-400">⌕</span>
                  <input
                    value={search}
                    onChange={(e) => handleSearch(e.target.value)}
                    placeholder="Search AI articles..."
                    className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                  />
                </div>
              </div>

              <div className="mt-5 border-t border-slate-100">
                {loading && (
                  <p className="py-10 text-center text-sm text-slate-500">
                    Loading AI developments...
                  </p>
                )}

                {!loading && error && (
                  <div className="my-5 rounded-lg bg-red-50 p-4 text-sm text-red-700">
                    {error}
                    <p className="mt-1">
                      Check that the FastAPI backend is running on port 8001.
                    </p>
                  </div>
                )}

                {!loading && !error && articles.length === 0 && (
                  <p className="py-10 text-center text-sm text-slate-500">
                    No articles found.
                  </p>
                )}

                {!loading &&
                  !error &&
                  articles.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
              </div>

              <div className="flex items-center justify-between border-t border-slate-100 pt-4">
                <p className="text-xs text-slate-500">
                  Page {page} of {totalPages}
                </p>
                <div className="flex gap-2">
                  <button
                    disabled={page <= 1 || loading}
                    onClick={() => setPage((p) => p - 1)}
                    className="rounded-lg border border-slate-200 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Previous
                  </button>
                  <button
                    disabled={page >= totalPages || loading}
                    onClick={() => setPage((p) => p + 1)}
                    className="rounded-lg border border-slate-200 px-3 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>
            </section>

            <footer className="pb-4 text-center text-xs text-slate-400">
              AI Pulse · Global AI News Intelligence Platform
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  detail,
  icon,
}: {
  label: string;
  value: string;
  detail: string;
  icon: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-lg text-blue-600">
          {icon}
        </span>
      </div>
      <p className="mt-4 text-3xl font-bold tracking-tight">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{detail}</p>
    </div>
  );
}
