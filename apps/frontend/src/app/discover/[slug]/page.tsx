"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import ArticleCard from "@/components/ArticleCard";
import { getDiscoverItem } from "@/lib/discoverTopics";
import { Article, ArticleListResponse } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function DiscoverTopicPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const item = getDiscoverItem(slug);

  const [articles, setArticles] = useState<Article[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadArticles = useCallback(async () => {
    if (!item) return;

    setLoading(true);
    setError("");

    try {
      const query = new URLSearchParams({
        search: item.query,
        page: String(page),
        page_size: "10",
        sort_by: "newest",
      });

      const response = await fetch(`${API}/articles/?${query}`);

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
  }, [item, page]);

  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  if (!item) {
    notFound();
  }

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <p className="text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600">Dashboard</Link>
            {" / "}
            <Link href="/discover" className="hover:text-blue-600">Discover</Link>
            {" / "}{item.name}
          </p>

          <div className="mt-2 flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-2xl">
              {item.icon}
            </span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">{item.name}</h1>
              <p className="mt-0.5 text-sm text-slate-500">{item.description}</p>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8 lg:px-10">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div>
                <h2 className="text-lg font-semibold">Coverage</h2>
                <p className="mt-1 text-sm text-slate-500">
                  {total.toLocaleString()} matching articles
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
              </div>
            )}

            {!loading && !error && articles.length === 0 && (
              <p className="py-12 text-center text-sm text-slate-500">
                No articles found for this topic yet.
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

          <Link
            href="/discover"
            className="inline-block text-sm font-medium text-slate-500 hover:text-blue-600"
          >
            ← Back to Discover
          </Link>
        </main>
      </div>
    </div>
  );
}
