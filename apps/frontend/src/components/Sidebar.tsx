"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const workspace = [
  { label: "Dashboard", href: "/", icon: "▦" },
  { label: "AI News Feed", href: "/news", icon: "◉" },
  { label: "Discover", href: "/discover", icon: "⌕" },
  { label: "Research & Papers", href: "/research", icon: "◷" },
];

const management = [
  { label: "Sources", href: "/sources", icon: "▤" },
  { label: "Settings", href: "/settings", icon: "⚙" },
];

export default function Sidebar() {
  const pathname = usePathname();

  function renderLinks(items: typeof workspace) {
    return items.map((item) => {
      const active = pathname === item.href;

      return (
        <Link
          key={item.href}
          href={item.href}
          className={`flex items-center gap-3 rounded-lg px-3 py-3 text-sm transition-colors ${
            active
              ? "bg-blue-500/20 font-medium text-blue-300"
              : "text-slate-300 hover:bg-white/10 hover:text-white"
          }`}
        >
          <span>{item.icon}</span>
          {item.label}
        </Link>
      );
    });
  }

  return (
    <aside className="hidden w-64 shrink-0 flex-col bg-[#111827] text-white md:flex">
      <Link href="/" className="border-b border-white/10 px-6 py-7">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500 text-xl font-bold">
            AI
          </div>
          <div>
            <h1 className="text-xl font-bold">AI Pulse</h1>
            <p className="text-xs text-slate-400">Global AI Intelligence</p>
          </div>
        </div>
      </Link>

      <nav className="flex-1 space-y-2 px-4 py-6">
        <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Workspace
        </p>

        {renderLinks(workspace)}

        <p className="mb-3 mt-9 px-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Management
        </p>

        {renderLinks(management)}
      </nav>

      <div className="border-t border-white/10 p-5">
        <p className="text-xs text-slate-400">Platform status</p>
        <div className="mt-2 flex items-center gap-2 text-sm">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          API connected
        </div>
      </div>
    </aside>
  );
}
