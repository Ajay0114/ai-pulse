"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import {
  Article,
  articleKeyPoints,
  articleSummary,
  formatDate,
} from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

const FEED_TYPE_LABEL: Record<string, string> = {
  main: "AI News",
  research: "Research",
};

export default function ArticleDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadArticle() {
      setLoading(true);
      setError("");
      setNotFound(false);

      try {
        const response = await fetch(`${API}/articles/${id}`);

        if (response.status === 404) {
          setNotFound(true);
          return;
        }

        if (!response.ok) {
          throw new Error(`Article API returned HTTP ${response.status}`);
        }

        setArticle(await response.json());
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Unable to load this article."
        );
      } finally {
        setLoading(false);
      }
    }

    loadArticle();
  }, [id]);

  const summary = article ? articleSummary(article) : undefined;
  const keyPoints = article ? articleKeyPoints(article) : [];

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <p className="text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600">Dashboard</Link>
            {" / "}
            <Link href="/news" className="hover:text-blue-600">AI News Feed</Link>
            {" / "}Article
          </p>
        </header>

        <main className="mx-auto max-w-3xl space-y-6 px-6 py-8 lg:px-10">
          {loading && (
            <p className="py-16 text-center text-sm text-slate-500">
              Loading article...
            </p>
          )}

          {!loading && notFound && (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <p className="text-lg font-semibold">Article not found</p>
              <p className="mt-2 text-sm text-slate-500">
                This article may have been removed or the link is incorrect.
              </p>
              <Link
                href="/news"
                className="mt-4 inline-block text-sm font-semibold text-blue-600 hover:text-blue-800"
              >
                ← Back to the news feed
              </Link>
            </div>
          )}

          {!loading && error && (
            <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {!loading && article && (
            <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:p-8">
              <div className="flex flex-wrap items-center gap-2 text-xs">
                <span className="rounded-md bg-blue-50 px-2.5 py-1 font-semibold text-blue-700">
                  {article.source?.name ?? "Unknown source"}
                </span>

                {article.categories.map((category) => (
                  <span
                    key={category.id}
                    className="rounded-md bg-purple-50 px-2.5 py-1 font-semibold text-purple-700"
                  >
                    {category.name}
                  </span>
                ))}

                {FEED_TYPE_LABEL[article.feed_type] && (
                  <span className="rounded-md bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">
                    {FEED_TYPE_LABEL[article.feed_type]}
                  </span>
                )}

                <span className="text-slate-400">
                  {formatDate(article.published_at)}
                </span>
              </div>

              <h1 className="mt-4 text-2xl font-bold leading-8 text-slate-900">
                {article.title}
              </h1>

              <p className="mt-2 text-sm text-slate-500">
                {article.author ? `By ${article.author}` : "Author not specified"}
              </p>

              {summary && (
                <p className="mt-6 text-base leading-7 text-slate-700">
                  {summary.short_summary}
                </p>
              )}

              {keyPoints.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Key points
                  </h2>
                  <ul className="mt-3 space-y-2">
                    {keyPoints.map((point, index) => (
                      <li
                        key={index}
                        className="flex gap-2 text-sm leading-6 text-slate-700"
                      >
                        <span className="text-blue-500">●</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {summary?.why_it_matters && (
                <div className="mt-6 rounded-lg border border-blue-100 bg-blue-50 p-4">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-blue-700">
                    Why it matters
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-blue-900">
                    {summary.why_it_matters}
                  </p>
                </div>
              )}

              {article.tags.length > 0 && (
                <div className="mt-6 flex flex-wrap gap-2">
                  {article.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600"
                    >
                      {tag.name}
                    </span>
                  ))}
                </div>
              )}

              {article.entities.length > 0 && (
                <div className="mt-4">
                  <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Mentioned
                  </h2>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {article.entities.map((entity) => (
                      <span
                        key={entity.id}
                        className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600"
                      >
                        {entity.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-8 flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-6">
                <Link
                  href="/news"
                  className="text-sm font-medium text-slate-500 hover:text-blue-600"
                >
                  ← Back to the news feed
                </Link>

                <a
                  href={article.original_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Read original article ↗
                </a>
              </div>
            </article>
          )}
        </main>
      </div>
    </div>
  );
}
