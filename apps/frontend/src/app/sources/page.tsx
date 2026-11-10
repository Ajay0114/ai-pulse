"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";

const API = process.env.NEXT_PUBLIC_API_BASE_URL;

type Source = {
  id: string;
  name: string;
  source_type: string;
  platform?: string | null;
  base_url?: string | null;
  feed_url?: string | null;
  description?: string | null;
  language?: string | null;
  region?: string | null;
  poll_interval_minutes: number;
  last_fetched_at?: string | null;
  next_fetch_at?: string | null;
  health_status: string;
  consecutive_failures: number;
  priority: number;
  is_active: boolean;
};

type SourceForm = {
  name: string;
  platform: string;
  base_url: string;
  feed_url: string;
  description: string;
  poll_interval_minutes: number;
  priority: number;
};

const emptyForm: SourceForm = {
  name: "",
  platform: "",
  base_url: "",
  feed_url: "",
  description: "",
  poll_interval_minutes: 30,
  priority: 5,
};

function formatDate(value?: string | null) {
  if (!value) return "Not available";

  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function HealthBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    healthy: "bg-emerald-50 text-emerald-700",
    blocked: "bg-red-50 text-red-700",
    failing: "bg-orange-50 text-orange-700",
    unknown: "bg-slate-100 text-slate-600",
  };

  const normalized = status?.toLowerCase() || "unknown";

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        styles[normalized] ?? styles.unknown
      }`}
    >
      {normalized.toUpperCase()}
    </span>
  );
}

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [healthFilter, setHealthFilter] = useState("all");
  const [activeFilter, setActiveFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionId, setActionId] = useState("");
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState<SourceForm>(emptyForm);

  const loadSources = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API}/sources/?skip=0&limit=100`);

      if (!response.ok) {
        throw new Error(`Sources API returned HTTP ${response.status}`);
      }

      const data = await response.json();
      setSources(data.items ?? []);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load sources."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  const healthy = sources.filter(
    (source) => source.health_status === "healthy"
  ).length;

  const blocked = sources.filter(
    (source) => source.health_status === "blocked"
  ).length;

  const active = sources.filter((source) => source.is_active).length;

  const filteredSources = sources.filter((source) => {
    const matchesSearch =
      source.name.toLowerCase().includes(search.toLowerCase()) ||
      (source.platform ?? "").toLowerCase().includes(search.toLowerCase());

    const matchesHealth =
      healthFilter === "all" ||
      source.health_status === healthFilter;

    const matchesActive =
      activeFilter === "all" ||
      (activeFilter === "active" && source.is_active) ||
      (activeFilter === "inactive" && !source.is_active);

    return matchesSearch && matchesHealth && matchesActive;
  });

  async function addSource(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSaving(true);
    setFormError("");

    try {
      const payload = {
        name: form.name,
        source_type: "rss",
        platform: form.platform || null,
        base_url: form.base_url || null,
        feed_url: form.feed_url,
        description: form.description || null,
        language: "en",
        poll_interval_minutes: Number(form.poll_interval_minutes),
        priority: Number(form.priority),
        metadata: {},
      };

      const response = await fetch(`${API}/sources/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      setForm(emptyForm);
      setShowForm(false);
      await loadSources();
    } catch (err) {
      setFormError(
        err instanceof Error ? err.message : "Unable to add source."
      );
    } finally {
      setSaving(false);
    }
  }

  async function toggleSource(source: Source) {
    setActionId(source.id);

    try {
      const response = await fetch(
        `${API}/sources/${source.id}/toggle`,
        { method: "PATCH" }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadSources();
    } catch (err) {
      alert(
        `Unable to update source: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
    } finally {
      setActionId("");
    }
  }

  async function deactivateSource(source: Source) {
    if (!window.confirm(`Deactivate "${source.name}"?`)) return;

    setActionId(source.id);

    try {
      const response = await fetch(
        `${API}/sources/${source.id}`,
        { method: "DELETE" }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      await loadSources();
    } catch (err) {
      alert(
        `Unable to deactivate source: ${
          err instanceof Error ? err.message : "Unknown error"
        }`
      );
    } finally {
      setActionId("");
    }
  }

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-500">
                <Link href="/" className="hover:text-blue-600">
                  Dashboard
                </Link>
                {" / "}Sources
              </p>
              <h1 className="mt-1 text-2xl font-bold">
                Sources Management
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Manage publishers, RSS feeds and source health.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={loadSources}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm hover:bg-slate-50"
              >
                ↻ Refresh
              </button>
              <button
                onClick={() => {
                  setFormError("");
                  setShowForm(!showForm);
                }}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
              >
                + Add Source
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1500px] space-y-6 px-6 py-8 lg:px-10">
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Total sources" value={sources.length} />
            <StatCard label="Active sources" value={active} />
            <StatCard label="Healthy sources" value={healthy} />
            <StatCard label="Blocked sources" value={blocked} />
          </section>

          {showForm && (
            <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold">Add RSS Source</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Register a new publisher feed.
                  </p>
                </div>
                <button
                  onClick={() => setShowForm(false)}
                  className="text-sm text-slate-500 hover:text-slate-900"
                >
                  Close ✕
                </button>
              </div>

              <form onSubmit={addSource} className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <FormField label="Source name">
                    <input
                      required
                      minLength={2}
                      value={form.name}
                      onChange={(e) =>
                        setForm({ ...form, name: e.target.value })
                      }
                      placeholder="Example: Example AI Blog"
                      className="form-input"
                    />
                  </FormField>

                  <FormField label="Platform">
                    <input
                      value={form.platform}
                      onChange={(e) =>
                        setForm({ ...form, platform: e.target.value })
                      }
                      placeholder="Example: technology_news"
                      className="form-input"
                    />
                  </FormField>

                  <FormField label="Website URL">
                    <input
                      type="url"
                      value={form.base_url}
                      onChange={(e) =>
                        setForm({ ...form, base_url: e.target.value })
                      }
                      placeholder="https://example.com"
                      className="form-input"
                    />
                  </FormField>

                  <FormField label="RSS Feed URL">
                    <input
                      required
                      type="url"
                      value={form.feed_url}
                      onChange={(e) =>
                        setForm({ ...form, feed_url: e.target.value })
                      }
                      placeholder="https://example.com/feed.xml"
                      className="form-input"
                    />
                  </FormField>

                  <FormField label="Polling interval (minutes)">
                    <input
                      type="number"
                      min="5"
                      value={form.poll_interval_minutes}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          poll_interval_minutes: Number(e.target.value),
                        })
                      }
                      className="form-input"
                    />
                  </FormField>

                  <FormField label="Priority (1–10)">
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={form.priority}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          priority: Number(e.target.value),
                        })
                      }
                      className="form-input"
                    />
                  </FormField>
                </div>

                <FormField label="Description">
                  <textarea
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                    rows={2}
                    placeholder="Brief description of this publisher"
                    className="form-input"
                  />
                </FormField>

                {formError && (
                  <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    {formError}
                  </p>
                )}

                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="rounded-lg border border-slate-200 px-4 py-2 text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={saving}
                    className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {saving ? "Adding..." : "Add Source"}
                  </button>
                </div>
              </form>
            </section>
          )}

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-5">
              <h2 className="text-lg font-semibold">Registered sources</h2>
              <p className="mt-1 text-sm text-slate-500">
                Search, monitor and manage your registered publishers.
              </p>
            </div>

            <div className="mb-5 grid gap-3 md:grid-cols-3">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search source or platform..."
                className="form-input"
              />

              <select
                value={healthFilter}
                onChange={(e) => setHealthFilter(e.target.value)}
                className="form-input"
              >
                <option value="all">All health statuses</option>
                <option value="healthy">Healthy</option>
                <option value="blocked">Blocked</option>
                <option value="failing">Failing</option>
                <option value="unknown">Unknown</option>
              </select>

              <select
                value={activeFilter}
                onChange={(e) => setActiveFilter(e.target.value)}
                className="form-input"
              >
                <option value="all">All sources</option>
                <option value="active">Active only</option>
                <option value="inactive">Inactive only</option>
              </select>
            </div>

            {loading && (
              <p className="py-10 text-center text-sm text-slate-500">
                Loading registered sources...
              </p>
            )}

            {!loading && error && (
              <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}

            {!loading && !error && (
              <>
                <div className="mb-3 text-sm text-slate-500">
                  Showing {filteredSources.length} of {sources.length} sources
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full min-w-[1050px] text-left text-sm">
                    <thead>
                      <tr className="border-y border-slate-100 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                        <th className="px-4 py-3">Source</th>
                        <th className="px-4 py-3">Type</th>
                        <th className="px-4 py-3">Health</th>
                        <th className="px-4 py-3">Failures</th>
                        <th className="px-4 py-3">Last fetched</th>
                        <th className="px-4 py-3">Active</th>
                        <th className="px-4 py-3">Actions</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredSources.map((source) => (
                        <tr
                          key={source.id}
                          className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
                        >
                          <td className="px-4 py-4">
                            <p className="font-semibold text-slate-800">
                              {source.name}
                            </p>
                            <p className="mt-1 text-xs text-slate-400">
                              {source.platform || "Platform not specified"}
                            </p>
                            {source.feed_url && (
                              <a
                                href={source.feed_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-1 block max-w-[250px] truncate text-xs text-blue-600 hover:underline"
                              >
                                {source.feed_url}
                              </a>
                            )}
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {source.source_type}
                          </td>

                          <td className="px-4 py-4">
                            <HealthBadge status={source.health_status} />
                          </td>

                          <td className="px-4 py-4 text-slate-600">
                            {source.consecutive_failures}
                          </td>

                          <td className="px-4 py-4 text-xs text-slate-500">
                            {formatDate(source.last_fetched_at)}
                          </td>

                          <td className="px-4 py-4">
                            <span
                              className={
                                source.is_active
                                  ? "text-emerald-700"
                                  : "text-slate-400"
                              }
                            >
                              {source.is_active ? "Active" : "Inactive"}
                            </span>
                          </td>

                          <td className="px-4 py-4">
                            <div className="flex items-center gap-3">
                              <button
                                disabled={actionId === source.id}
                                onClick={() => toggleSource(source)}
                                className="text-xs font-semibold text-blue-600 hover:text-blue-800 disabled:opacity-50"
                              >
                                {actionId === source.id
                                  ? "Updating..."
                                  : source.is_active
                                    ? "Deactivate"
                                    : "Activate"}
                              </button>

                              {source.is_active && (
                                <button
                                  disabled={actionId === source.id}
                                  onClick={() => deactivateSource(source)}
                                  className="text-xs text-red-600 hover:text-red-800 disabled:opacity-50"
                                >
                                  Remove
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {filteredSources.length === 0 && (
                  <p className="py-10 text-center text-sm text-slate-500">
                    No matching sources found.
                  </p>
                )}
              </>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-bold">{value}</p>
    </div>
  );
}

function FormField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-slate-700">
        {label}
      </span>
      {children}
    </label>
  );
}
