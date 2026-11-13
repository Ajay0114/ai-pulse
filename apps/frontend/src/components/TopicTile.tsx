"use client";

import Link from "next/link";
import { DiscoverItem } from "@/lib/discoverTopics";

export default function TopicTile({
  item,
  variant = "default",
}: {
  item: DiscoverItem;
  variant?: "default" | "compact";
}) {
  if (variant === "compact") {
    return (
      <Link
        href={`/discover/${item.slug}`}
        className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md"
      >
        <span className="text-2xl">{item.icon}</span>
        <div className="min-w-0">
          <h3 className="truncate font-semibold text-slate-900">
            {item.name}
          </h3>
          <p className="mt-0.5 text-xs font-medium text-blue-600">
            Explore →
          </p>
        </div>
      </Link>
    );
  }

  return (
    <Link
      href={`/discover/${item.slug}`}
      className="block rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:shadow-md"
    >
      <span className="text-2xl">{item.icon}</span>
      <h3 className="mt-3 font-semibold text-slate-900">{item.name}</h3>
      <p className="mt-1 text-sm leading-5 text-slate-500">
        {item.description}
      </p>
      <span className="mt-4 inline-block text-sm font-semibold text-blue-600">
        Explore articles →
      </span>
    </Link>
  );
}
