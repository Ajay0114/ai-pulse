"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import TopicTile from "@/components/TopicTile";
import {
  DISCOVER_TOPICS,
  DISCOVER_COMPANIES,
  DISCOVER_MODEL_CATEGORIES,
} from "@/lib/discoverTopics";

export default function DiscoverPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");

  function submitSearch() {
    const term = search.trim();
    if (!term) return;
    router.push(`/news?search=${encodeURIComponent(term)}`);
  }

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <p className="text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600">Dashboard</Link>
            {" / "}Discover
          </p>
          <h1 className="mt-1 text-2xl font-bold">Discover AI</h1>
          <p className="mt-1 text-sm text-slate-500">
            Explore topics, companies, models and developments across the AI ecosystem.
          </p>

          <div className="mt-4 max-w-xl">
            <div className="flex gap-2">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") submitSearch();
                }}
                placeholder="Search the full article collection..."
                className="min-w-0 flex-1 rounded-lg border border-slate-200 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
              <button
                onClick={submitSearch}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Search
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] space-y-8 px-6 py-8 lg:px-10">
          <section>
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Explore AI topics</h2>
              <p className="mt-1 text-sm text-slate-500">
                Select a topic to see its own curated feed.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {DISCOVER_TOPICS.map((topic) => (
                <TopicTile key={topic.slug} item={topic} />
              ))}
            </div>
          </section>

          <section>
            <div className="mb-4">
              <h2 className="text-lg font-semibold">AI companies</h2>
              <p className="mt-1 text-sm text-slate-500">
                Explore coverage of major companies in the AI ecosystem.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {DISCOVER_COMPANIES.map((company) => (
                <TopicTile key={company.slug} item={company} variant="compact" />
              ))}
            </div>
          </section>

          <section>
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Models and tools</h2>
              <p className="mt-1 text-sm text-slate-500">
                Browse AI product and technology coverage by category.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {DISCOVER_MODEL_CATEGORIES.map((category) => (
                <TopicTile key={category.slug} item={category} variant="compact" />
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
