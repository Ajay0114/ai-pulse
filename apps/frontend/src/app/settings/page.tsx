"use client";

import { useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";

const sections = [
  { id: "general", label: "General", icon: "⚙️" },
  { id: "collection", label: "Data Collection", icon: "📡" },
  { id: "ai", label: "AI Configuration", icon: "🧠" },
  { id: "notifications", label: "Notifications", icon: "🔔" },
  { id: "health", label: "System Health", icon: "💚" },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("general");

  const [platformName, setPlatformName] = useState("AI Pulse");
  const [description, setDescription] = useState(
    "Global AI Intelligence Platform"
  );
  const [timezone, setTimezone] = useState("Asia/Kolkata");

  const [pollInterval, setPollInterval] = useState("30");
  const [automaticIngestion, setAutomaticIngestion] = useState(true);
  const [retryFailures, setRetryFailures] = useState(true);

  const [provider, setProvider] = useState("openrouter");
  const [model, setModel] = useState("openai/gpt-4.1-mini");

  const [dailySummary, setDailySummary] = useState(true);
  const [systemAlerts, setSystemAlerts] = useState(true);
  const [sourceAlerts, setSourceAlerts] = useState(true);

  const [savedMessage, setSavedMessage] = useState("");

  function handleSave() {
    setSavedMessage(
      "These settings are currently local UI preferences. Backend persistence will be implemented in a later step."
    );
  }

  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />

      <div className="min-w-0 flex-1">
        <header className="border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
          <p className="text-sm text-slate-500">
            <Link href="/" className="hover:text-blue-600">Dashboard</Link>
            {" / "}Settings
          </p>

          <h1 className="mt-1 text-2xl font-bold">Settings</h1>

          <p className="mt-1 text-sm text-slate-500">
            Configure AI Pulse platform preferences and system behaviour.
          </p>
        </header>

        <main className="mx-auto max-w-[1500px] px-6 py-8 lg:px-10">
          <div className="grid gap-6 lg:grid-cols-[250px_minmax(0,1fr)]">
            <aside className="h-fit rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
              <p className="px-3 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Configuration
              </p>

              <nav className="space-y-1">
                {sections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => {
                      setActiveSection(section.id);
                      setSavedMessage("");
                    }}
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm font-medium transition ${
                      activeSection === section.id
                        ? "bg-blue-50 text-blue-700"
                        : "text-slate-600 hover:bg-slate-50"
                    }`}
                  >
                    <span>{section.icon}</span>
                    {section.label}
                  </button>
                ))}
              </nav>
            </aside>

            <div className="space-y-6">
              {activeSection === "general" && (
                <SettingsCard
                  title="General Settings"
                  description="Manage the basic identity and regional preferences of AI Pulse."
                >
                  <Field label="Platform name">
                    <input
                      value={platformName}
                      onChange={(e) => setPlatformName(e.target.value)}
                      className="setting-input"
                    />
                  </Field>

                  <Field label="Platform description">
                    <input
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      className="setting-input"
                    />
                  </Field>

                  <Field label="Timezone">
                    <select
                      value={timezone}
                      onChange={(e) => setTimezone(e.target.value)}
                      className="setting-input"
                    >
                      <option value="Asia/Kolkata">India Standard Time (IST)</option>
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="Europe/London">London Time</option>
                      <option value="Asia/Singapore">Singapore Time</option>
                    </select>
                  </Field>
                </SettingsCard>
              )}

              {activeSection === "collection" && (
                <SettingsCard
                  title="Data Collection"
                  description="Configure preferences for collecting information from registered sources."
                >
                  <Field label="Default polling interval">
                    <select
                      value={pollInterval}
                      onChange={(e) => setPollInterval(e.target.value)}
                      className="setting-input"
                    >
                      <option value="15">Every 15 minutes</option>
                      <option value="30">Every 30 minutes</option>
                      <option value="60">Every hour</option>
                      <option value="180">Every 3 hours</option>
                      <option value="360">Every 6 hours</option>
                      <option value="720">Every 12 hours</option>
                      <option value="1440">Once daily</option>
                    </select>
                  </Field>

                  <Toggle
                    label="Automatic ingestion"
                    description="Allow the platform to collect updates from active sources automatically."
                    checked={automaticIngestion}
                    onChange={setAutomaticIngestion}
                  />

                  <Toggle
                    label="Retry failed sources"
                    description="Retry source collection when temporary errors occur."
                    checked={retryFailures}
                    onChange={setRetryFailures}
                  />
                </SettingsCard>
              )}

              {activeSection === "ai" && (
                <SettingsCard
                  title="AI Configuration"
                  description="Choose the AI provider and model for future intelligence processing."
                >
                  <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
                    AI provider settings are currently preferences only. API keys
                    will be configured securely on the backend, never in the browser.
                  </div>

                  <Field label="AI provider">
                    <select
                      value={provider}
                      onChange={(e) => setProvider(e.target.value)}
                      className="setting-input"
                    >
                      <option value="openrouter">OpenRouter</option>
                      <option value="openai">OpenAI</option>
                      <option value="azure">Azure OpenAI</option>
                    </select>
                  </Field>

                  <Field label="Model identifier">
                    <input
                      value={model}
                      onChange={(e) => setModel(e.target.value)}
                      placeholder="Provider model identifier"
                      className="setting-input"
                    />
                  </Field>

                  <p className="text-xs text-slate-500">
                    The selected model has not yet been connected to the ingestion
                    or article-processing workflows.
                  </p>
                </SettingsCard>
              )}

              {activeSection === "notifications" && (
                <SettingsCard
                  title="Notifications"
                  description="Choose which platform events should eventually generate notifications."
                >
                  <Toggle
                    label="Daily AI intelligence summary"
                    description="Receive a summary of important AI developments collected each day."
                    checked={dailySummary}
                    onChange={setDailySummary}
                  />

                  <Toggle
                    label="System alerts"
                    description="Receive alerts about API, database and processing failures."
                    checked={systemAlerts}
                    onChange={setSystemAlerts}
                  />

                  <Toggle
                    label="Source health alerts"
                    description="Receive alerts when registered sources become unavailable."
                    checked={sourceAlerts}
                    onChange={setSourceAlerts}
                  />
                </SettingsCard>
              )}

              {activeSection === "health" && (
                <SettingsCard
                  title="System Health"
                  description="View the current status of the AI Pulse infrastructure."
                >
                  <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                    Live infrastructure monitoring will be connected to the
                    existing backend health endpoint in a later step.
                  </div>

                  <HealthItem name="FastAPI Backend" detail="Port 8001" />
                  <HealthItem name="PostgreSQL Database" detail="Port 5433" />
                  <HealthItem name="Redis Cache" detail="Port 6380" />
                  <HealthItem name="Frontend" detail="Next.js · Port 3000" />
                </SettingsCard>
              )}

              <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="text-xs text-slate-500">
                  Changes are not persisted yet.
                </div>

                <button
                  onClick={handleSave}
                  className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Save preferences
                </button>
              </div>

              {savedMessage && (
                <p className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                  {savedMessage}
                </p>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function SettingsCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-1 text-sm text-slate-500">{description}</p>
      <div className="mt-6 space-y-6">{children}</div>
    </section>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-2">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-5 last:border-0 last:pb-0">
      <div>
        <p className="text-sm font-medium text-slate-800">{label}</p>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative mt-1 h-6 w-11 shrink-0 rounded-full transition ${
          checked ? "bg-blue-600" : "bg-slate-300"
        }`}
      >
        <span
          className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${
            checked ? "left-6" : "left-1"
          }`}
        />
      </button>
    </div>
  );
}

function HealthItem({
  name,
  detail,
}: {
  name: string;
  detail: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-4 last:border-0">
      <div>
        <p className="text-sm font-medium text-slate-800">{name}</p>
        <p className="mt-1 text-xs text-slate-500">{detail}</p>
      </div>

      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
        Not connected
      </span>
    </div>
  );
}
