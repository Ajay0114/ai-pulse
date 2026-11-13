"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import ArticleCard from "@/components/ArticleCard";
import { Article, ArticleListResponse } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function ResearchPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    async function loadResearch() {
      setLoading(true);
      setError("");

      try {
        const params = new URLSearchParams({
          page: "1",
          page_size: "100",
          sort_by: "newest",
          feed_type: "research",
        });

        const response = await fetch(`${API}/articles/?${params}`);

        if (!response.ok) {
          throw new Error(`API returned HTTP ${response.status}`);
        }

        const data: ArticleListResponse = await response.json();

        setArticles(data.articles ?? []);
        setTotal(data.total ?? 0);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Unable to load research."
        );
      } finally {
        setLoading(false);
      }
    }

    loadResearch();
  }, []);

  const filteredArticles = articles.filter((article) => {
    const term = search.toLowerCase();

    return (
      article.title.toLowerCase().includes(term) ||
      (article.description ?? "").toLowerCase().includes(term)
    );
  });

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <p className="text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600">Dashboard</Link>
            {" / "}Research & Papers
          </p>

          <h1 className="mt-1 text-2xl font-bold">
            Research & Papers
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Research developments that passed AI Pulse&apos;s editorial bar for
            significance (score ≥ 8).
          </p>
        </header>

        <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8 lg:px-10">
          <section className="grid gap-4 sm:grid-cols-2">
            <StatCard label="Research articles" value={total} />
            <StatCard label="Editorial score threshold" value="≥ 8 / 10" />
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold">Research discovery</h2>

            <p className="mt-1 text-sm text-slate-500">
              Search research publications collected by AI Pulse.
            </p>

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search research papers, topics or keywords..."
              className="mt-5 w-full rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
            />
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-5">
              <h2 className="text-lg font-semibold">Latest research papers</h2>
              <p className="mt-1 text-sm text-slate-500">
                Publications that passed AI Pulse&apos;s research-feed relevance gate.
              </p>
            </div>

            {loading && (
              <p className="py-10 text-center text-sm text-slate-500">
                Loading research publications...
              </p>
            )}

            {error && (
              <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
                {error}
              </p>
            )}

            {!loading && !error && filteredArticles.length === 0 && (
              <p className="py-10 text-center text-sm text-slate-500">
                No matching research papers found.
              </p>
            )}

            {!loading &&
              filteredArticles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
          </section>
        </main>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number | string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-bold">{value}</p>
    </div>
  );
}
