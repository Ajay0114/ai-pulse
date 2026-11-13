"use client";

import Link from "next/link";
import { Article, articleSummary, formatDate } from "@/lib/types";

const FEED_TYPE_LABEL: Record<string, string> = {
  research: "Research",
};

export default function ArticleCard({ article }: { article: Article }) {
  const summary = articleSummary(article);
  const category = article.categories[0];
  const feedLabel = FEED_TYPE_LABEL[article.feed_type];

  return (
    <article className="border-b border-slate-100 py-5 last:border-0">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-md bg-blue-50 px-2.5 py-1 font-semibold text-blue-700">
          {article.source?.name ?? "Unknown source"}
        </span>

        {category && (
          <span className="rounded-md bg-purple-50 px-2.5 py-1 font-semibold text-purple-700">
            {category.name}
          </span>
        )}

        {feedLabel && (
          <span className="rounded-md bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">
            {feedLabel}
          </span>
        )}

        <span className="text-slate-400">
          {formatDate(article.published_at)}
        </span>
      </div>

      <Link href={`/article/${article.id}`}>
        <h3 className="mt-3 text-base font-semibold leading-6 text-slate-900 hover:text-blue-700">
          {article.title}
        </h3>
      </Link>

      <p className="mt-2 line-clamp-3 text-sm leading-6 text-slate-600">
        {summary?.short_summary ||
          article.description ||
          "No summary available yet."}
      </p>

      {article.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {article.tags.slice(0, 4).map((tag) => (
            <span
              key={tag.id}
              className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
            >
              {tag.name}
            </span>
          ))}
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <Link
          href={`/article/${article.id}`}
          className="text-sm font-semibold text-blue-600 hover:text-blue-800"
        >
          Read full summary →
        </Link>

        <a
          href={article.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-xs text-slate-400 hover:text-blue-600"
        >
          Original source ↗
        </a>
      </div>
    </article>
  );
}
