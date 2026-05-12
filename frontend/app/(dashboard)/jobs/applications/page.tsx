"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: string }> = {
  applied: { label: "Applied", color: "#4da6ff", icon: "" },
  interview: { label: "Interview", color: "#34d399", icon: "" },
  rejected: { label: "Rejected", color: "#f87171", icon: "" },
  offer: { label: "Offer", color: "#34d399", icon: "" },
  withdrawn: { label: "Withdrawn", color: "#5c6b82", icon: "" },
};

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [filter, setFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getApplications(filter || undefined).then((d) => setApplications(d.applications || [])),
      api.getApplicationStats().then(setStats),
    ])
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-8 py-6 max-w-wide mx-auto">
      <h1 className="text-heading text-obsidian font-display">My Applications</h1>
      <p className="text-body text-gravel mt-1">Track your job application pipeline</p>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8 mt-8">
        {[
          { label: "Total", value: stats?.total || 0, color: "#ffffff" },
          { label: "Applied", value: stats?.applied || 0, color: "#4da6ff" },
          { label: "Interview", value: stats?.interview || 0, color: "#34d399" },
          { label: "Rejected", value: stats?.rejected || 0, color: "#f87171" },
          { label: "Response Rate", value: `${stats?.response_rate || 0}%`, color: "#fbbf24" },
        ].map((s) => (
          <div key={s.label} className="card text-center">
            <p className="text-caption text-gravel">{s.label}</p>
            <p className="text-heading tracking-tight" style={{ color: s.color }}>
              {s.value}
            </p>
          </div>
        ))}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        {["", "applied", "interview", "rejected", "offer"].map((f) => (
          <button
            key={f}
            onClick={() => { setFilter(f); setLoading(true); }}
            className={`px-4 py-2 rounded-full text-caption transition-all active:scale-95 ${
              filter === f
                ? "bg-obsidian text-obsidian"
                : "bg-powder text-cinder border border-chalk hover:border-gravel"
            }`}
          >
            {f ? STATUS_CONFIG[f]?.label || f : "All"}
          </button>
        ))}
      </div>

      {/* Applications list */}
      {applications.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-body-lg text-gravel">No applications yet</p>
          <p className="text-body text-gravel mt-2">Start applying to jobs from the Jobs feed or Search page</p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map((app: any) => {
            const cfg = STATUS_CONFIG[app.status] || STATUS_CONFIG.applied;
            return (
              <div key={app.id} className="card flex items-center gap-4">
                <div
                  className="w-10 h-10 rounded-sm flex items-center justify-center text-obsidian text-caption-strong flex-shrink-0"
                  style={{ backgroundColor: cfg.color }}
                >
                  {cfg.label.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-body-medium text-obsidian truncate">{app.job_title}</h3>
                  <p className="text-caption text-gravel">{app.company} · {app.location}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span
                    className="inline-block px-3 py-1 rounded-full text-caption font-medium text-obsidian"
                    style={{ backgroundColor: cfg.color }}
                  >
                    {cfg.label}
                  </span>
                  {app.applied_at && (
                    <p className="text-caption text-gravel mt-1">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
                {app.job_url && (
                  <a href={app.job_url} target="_blank" rel="noopener noreferrer" className="text-obsidian hover:underline text-caption flex-shrink-0">
                    View
                  </a>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
