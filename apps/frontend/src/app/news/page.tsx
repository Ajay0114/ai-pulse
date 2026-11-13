"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import ArticleCard from "@/components/ArticleCard";
import { Article, ArticleListResponse } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

type Source = {
  id: string;
  name: string;
};

type CategoryOption = {
  id: string;
  name: string;
  slug: string;
  article_count: number;
};

export default function NewsPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [categories, setCategories] = useState<CategoryOption[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [category, setCategory] = useState("");
  const [sortBy, setSortBy] = useState("newest");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadArticles = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: "10",
        sort_by: sortBy,
        feed_type: "main",
      });

      if (search) params.set("search", search);
      if (sourceId) params.set("source_id", sourceId);
      if (category) params.set("category", category);

      const response = await fetch(`${API}/articles/?${params}`);

      if (!response.ok) {
        throw new Error(`Article API returned HTTP ${response.status}`);
      }

      const data: ArticleListResponse = await response.json();

      setArticles(data.articles ?? []);
      setTotal(data.total ?? 0);
      setTotalPages(data.total_pages ?? 1);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load articles."
      );
    } finally {
      setLoading(false);
    }
  }, [page, search, sourceId, category, sortBy]);

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
      } catch (err) {
        console.error("Unable to load sources:", err);
      }
    }

    loadSources();
  }, []);

  useEffect(() => {
    async function loadCategories() {
      try {
        const response = await fetch(`${API}/categories/`);

        if (!response.ok) return;

        setCategories(await response.json());
      } catch (err) {
        console.error("Unable to load categories:", err);
      }
    }

    loadCategories();
  }, []);

  function applySearch() {
    setPage(1);
    setSearch(searchInput.trim());
  }

  function resetFilters() {
    setSearchInput("");
    setSearch("");
    setSourceId("");
    setCategory("");
    setSortBy("newest");
    setPage(1);
  }

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
    <Sidebar />
    <div className="min-w-0 flex-1">
      <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-sm text-slate-500">
              <Link href="/" className="hover:text-blue-600">
                Dashboard
              </Link>
              {" / "}AI News Feed
            </div>
            <h1 className="mt-1 text-2xl font-bold tracking-tight">
              AI News Feed
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Monitor the latest developments across the global AI ecosystem.
            </p>
          </div>

          <button
            onClick={loadArticles}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            ↻ Refresh
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8 lg:px-10">
        <section className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Matching articles</p>
            <p className="mt-2 text-3xl font-bold">
              {total.toLocaleString()}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Based on your current filters
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">Available publishers</p>
            <p className="mt-2 text-3xl font-bold">{sources.length}</p>
            <p className="mt-1 text-xs text-slate-400">
              Registered content sources
            </p>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-5">
            <h2 className="text-lg font-semibold">Search and filters</h2>
            <p className="mt-1 text-sm text-slate-500">
              Find articles using keywords, publishers and categories.
            </p>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Search articles
              </label>
              <div className="flex gap-2">
                <input
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") applySearch();
                  }}
                  placeholder="Search AI, OpenAI, agents, models..."
                  className="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
                <button
                  onClick={applySearch}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Search
                </button>
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Publisher
              </label>
              <select
                value={sourceId}
                onChange={(e) => {
                  setSourceId(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500"
              >
                <option value="">All publishers</option>
                {sources.map((source) => (
                  <option key={source.id} value={source.id}>
                    {source.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => {
                  setCategory(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500"
              >
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.slug}>
                    {c.name} ({c.article_count})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Sort by
              </label>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500"
              >
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
                <option value="importance">Importance</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex justify-end">
            <button
              onClick={resetFilters}
              className="text-sm font-medium text-slate-500 hover:text-blue-600"
            >
              Reset all filters
            </button>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h2 className="text-lg font-semibold">Articles</h2>
              <p className="mt-1 text-sm text-slate-500">
                {total.toLocaleString()} matching results
              </p>
            </div>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
              Page {page} of {totalPages}
            </span>
          </div>

          {loading && (
            <p className="py-12 text-center text-sm text-slate-500">
              Loading articles...
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
            <p className="py-12 text-center text-sm text-slate-500">
              No articles found. Try changing your search or filters.
            </p>
          )}

          {!loading &&
            !error &&
            articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}

          <div className="flex items-center justify-between border-t border-slate-100 pt-4">
            <p className="text-xs text-slate-500">
              Page {page} of {totalPages}
            </p>

            <div className="flex gap-2">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => p - 1)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>

              <button
                disabled={page >= totalPages || loading}
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
    </div>
  );
}
