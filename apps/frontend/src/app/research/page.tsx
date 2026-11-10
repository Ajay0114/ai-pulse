"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

type Article = {
  id: string;
  title: string;
  description?: string | null;
  original_url: string;
  author?: string | null;
  published_at?: string | null;
  content_type: string;
  source: {
    id: string;
    name: string;
    platform?: string | null;
  };
};

function formatDate(value?: string | null) {
  if (!value) return "Date unavailable";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

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
        });

        const response = await fetch(`${API}/articles/?${params}`);

        if (!response.ok) {
          throw new Error(`API returned HTTP ${response.status}`);
        }

        const data = await response.json();

        const researchArticles = (data.articles ?? []).filter(
          (article: Article) =>
            article.source?.platform === "research_repository" ||
            article.source?.name?.toLowerCase().includes("arxiv")
        );

        setArticles(researchArticles);
        setTotal(researchArticles.length);
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
            Explore AI research, scientific publications and technical papers.
          </p>
        </header>

        <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8 lg:px-10">
          <section className="grid gap-4 sm:grid-cols-3">
            <StatCard label="Research articles loaded" value={total} />
            <StatCard label="Research repositories" value={3} />
            <StatCard label="Page size" value="100" />
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
                Publications from currently indexed research repositories.
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

            {!loading && filteredArticles.map((article) => (
              <article
                key={article.id}
                className="border-b border-slate-100 py-5 last:border-0"
              >
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded-md bg-purple-50 px-2.5 py-1 font-semibold text-purple-700">
                    {article.source.name}
                  </span>

                  <span className="text-slate-400">
                    {formatDate(article.published_at)}
                  </span>
                </div>

                <h3 className="mt-3 font-semibold leading-6">
                  {article.title}
                </h3>

                {article.description && (
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    {article.description}
                  </p>
                )}

                <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                  <span className="text-xs text-slate-400">
                    {article.author || "Authors not specified"}
                  </span>

                  <a
                    href={article.original_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm font-semibold text-blue-600 hover:text-blue-800"
                  >
                    Read research paper ↗
                  </a>
                </div>
              </article>
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
