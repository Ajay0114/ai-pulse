"use client";

import { useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import ArticleCard from "@/components/ArticleCard";
import { Article, ArticleListResponse } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

const topics = [
  { name: "AI Agents", description: "Autonomous agents, agentic workflows and orchestration", icon: "🤖", query: "AI agents" },
  { name: "Large Language Models", description: "LLMs, reasoning models and language technologies", icon: "🧠", query: "large language models" },
  { name: "Generative AI", description: "Text, image, video and audio generation", icon: "✨", query: "generative AI" },
  { name: "AI Coding", description: "Coding assistants, AI IDEs and software engineering", icon: "💻", query: "AI coding" },
  { name: "Robotics", description: "Robotics, physical AI and autonomous systems", icon: "🦾", query: "AI robotics" },
  { name: "Machine Learning", description: "ML research, algorithms and applications", icon: "📊", query: "machine learning" },
  { name: "Computer Vision", description: "Image recognition, vision models and multimodal AI", icon: "👁️", query: "computer vision AI" },
  { name: "AI Infrastructure", description: "GPUs, inference, training and AI infrastructure", icon: "⚙️", query: "AI infrastructure" },
];

const companies = [
  { name: "OpenAI", description: "AI models and products" },
  { name: "Google DeepMind", description: "AI research and foundation models" },
  { name: "Anthropic", description: "AI assistants and foundation models" },
  { name: "Meta AI", description: "Open models and AI research" },
  { name: "Microsoft AI", description: "AI platforms and products" },
  { name: "NVIDIA", description: "AI computing and infrastructure" },
  { name: "Hugging Face", description: "Open-source AI ecosystem" },
  { name: "xAI", description: "AI models and research" },
];

const modelCategories = [
  { name: "Language Models", query: "language models", icon: "🧠" },
  { name: "AI Coding Tools", query: "AI coding tools", icon: "💻" },
  { name: "Image Generation", query: "AI image generation", icon: "🎨" },
  { name: "Video Generation", query: "AI video generation", icon: "🎬" },
  { name: "Voice & Audio AI", query: "AI voice audio", icon: "🎙️" },
  { name: "AI Development Tools", query: "AI developer tools", icon: "🛠️" },
];

export default function DiscoverPage() {
  const [selectedTopic, setSelectedTopic] = useState("");
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function discover(query: string) {
    setSelectedTopic(query);
    setLoading(true);
    setError("");
    setArticles([]);

    try {
      const params = new URLSearchParams({
        search: query,
        page: "1",
        page_size: "10",
        sort_by: "newest",
      });

      const response = await fetch(`${API}/articles/?${params}`);

      if (!response.ok) {
        throw new Error(`Article API returned HTTP ${response.status}`);
      }

      const data: ArticleListResponse = await response.json();
      setArticles(data.articles ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to discover articles.");
    } finally {
      setLoading(false);
    }
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
        </header>

        <main className="mx-auto max-w-[1500px] space-y-8 px-6 py-8 lg:px-10">
          <section>
            <div className="mb-4">
              <h2 className="text-lg font-semibold">Explore AI topics</h2>
              <p className="mt-1 text-sm text-slate-500">
                Select a topic to discover related articles from your collected news.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {topics.map((topic) => (
                <button
                  key={topic.name}
                  onClick={() => discover(topic.query)}
                  className={`rounded-xl border bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md ${
                    selectedTopic === topic.query
                      ? "border-blue-500 ring-2 ring-blue-100"
                      : "border-slate-200"
                  }`}
                >
                  <span className="text-2xl">{topic.icon}</span>
                  <h3 className="mt-3 font-semibold">{topic.name}</h3>
                  <p className="mt-1 text-sm leading-5 text-slate-500">
                    {topic.description}
                  </p>
                  <span className="mt-4 inline-block text-sm font-semibold text-blue-600">
                    Explore articles →
                  </span>
                </button>
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
              {companies.map((company) => (
                <button
                  key={company.name}
                  onClick={() => discover(company.name)}
                  className="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-blue-300 hover:shadow-md"
                >
                  <h3 className="font-semibold">{company.name}</h3>
                  <p className="mt-1 text-sm text-slate-500">{company.description}</p>
                  <span className="mt-3 inline-block text-xs font-semibold text-blue-600">
                    Find coverage →
                  </span>
                </button>
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
              {modelCategories.map((category) => (
                <button
                  key={category.name}
                  onClick={() => discover(category.query)}
                  className="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm hover:border-blue-300"
                >
                  <span className="text-2xl">{category.icon}</span>
                  <div>
                    <h3 className="font-semibold">{category.name}</h3>
                    <p className="mt-1 text-xs text-blue-600">Explore coverage →</p>
                  </div>
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">
                {selectedTopic ? `Results for "${selectedTopic}"` : "Explore developments"}
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Search results from your existing article collection.
              </p>
            </div>

            {!selectedTopic && (
              <p className="py-8 text-center text-sm text-slate-500">
                Select any topic, company or category above to discover related articles.
              </p>
            )}

            {loading && (
              <p className="py-8 text-center text-sm text-slate-500">
                Searching your article collection...
              </p>
            )}

            {error && (
              <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</p>
            )}

            {!loading && selectedTopic && !error && articles.length === 0 && (
              <p className="py-8 text-center text-sm text-slate-500">
                No matching articles found. Try another topic.
              </p>
            )}

            {!loading &&
              articles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
          </section>
        </main>
      </div>
    </div>
  );
}
