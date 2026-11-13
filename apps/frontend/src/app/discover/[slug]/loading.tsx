import Sidebar from "@/components/Sidebar";

export default function DiscoverTopicLoading() {
  return (
    <div className="flex min-h-screen bg-[#f5f7fb]">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <main className="mx-auto max-w-[1500px] px-6 py-16">
          <p className="text-center text-sm text-slate-500">Loading...</p>
        </main>
      </div>
    </div>
  );
}
