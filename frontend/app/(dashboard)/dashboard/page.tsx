"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function GradeRow({ grade, count, total, cls }: { grade: string; count: number; total: number; cls: string }) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div className="flex items-center gap-3">
      <span className={`grade grade-sm grade-${grade}`}>{grade}</span>
      <div className="flex-1 score-track"><div className={`score-fill ${cls}`} style={{ width: `${pct}%` }} /></div>
      <span className="text-caption text-gravel w-6 text-right font-medium">{count}</span>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { api.getJobStats().then(setStats).catch(console.error).finally(() => setLoading(false)); }, []);

  if (loading) return <div className="flex items-center justify-center min-h-[60vh]"><div className="w-6 h-6 border-2 border-obsidian border-t-transparent rounded-full animate-spin" /></div>;

  const totalGraded = stats ? Object.values(stats.grades || {}).reduce((a: number, b: any) => a + b, 0) : 0;

  return (
    <div>
      <div className="mb-10">
        <h1 className="text-heading text-obsidian font-display">Welcome back{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}</h1>
        <p className="text-body text-gravel mt-1">Here&apos;s what&apos;s happening with your job search today.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        {[
          { label: "APPLICATIONS", value: stats?.active || 0, sub: "Currently tracked" },
          { label: "INTERVIEWS", value: stats?.applied || 0, sub: "All time" },
          { label: "BOOKMARKED", value: stats?.bookmarked || 0, sub: "Saved for review" },
          { label: "RESPONSE RATE", value: `${totalGraded ? Math.round(((stats?.applied || 0) / (totalGraded as number)) * 100) : 0}%`, sub: "This month" },
        ].map((s) => (
          <div key={s.label} className="stat-card">
            <p className="stat-label">{s.label}</p>
            <p className="stat-value mt-2">{s.value}</p>
            <p className="stat-sub">{s.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
        {/* Grade Distribution */}
        <div className="card">
          <h2 className="text-body-medium text-obsidian mb-5">Grade Distribution</h2>
          <div className="space-y-3">
            <GradeRow grade="A" count={stats?.grades?.A || 0} total={totalGraded as number} cls="bg-grade-a" />
            <GradeRow grade="B" count={stats?.grades?.B || 0} total={totalGraded as number} cls="bg-grade-b" />
            <GradeRow grade="C" count={stats?.grades?.C || 0} total={totalGraded as number} cls="bg-grade-c" />
            <GradeRow grade="D" count={stats?.grades?.D || 0} total={totalGraded as number} cls="bg-grade-d" />
            <GradeRow grade="F" count={stats?.grades?.F || 0} total={totalGraded as number} cls="bg-grade-f" />
          </div>
        </div>

        {/* Sources */}
        <div className="card">
          <h2 className="text-body-medium text-obsidian mb-5">Jobs by Source</h2>
          <div className="space-y-3">
            {stats?.sources && Object.entries(stats.sources).sort(([, a]: any, [, b]: any) => b - a).map(([source, count]: any) => (
              <div key={source} className="flex items-center justify-between">
                <span className="text-body text-cinder capitalize">{source}</span>
                <span className="text-body-medium text-obsidian">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="card">
        <h2 className="text-body-medium text-obsidian mb-5">Jobs by Category</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 xl:grid-cols-7 gap-3">
          {stats?.categories && Object.entries(stats.categories).sort(([, a]: any, [, b]: any) => b - a).map(([cat, count]: any) => (
            <div key={cat} className="bg-powder rounded-card p-4 text-center">
              <p className="text-heading-sm text-obsidian font-display">{count}</p>
              <p className="text-label text-gravel mt-1 uppercase capitalize">{cat.replace("_", "/")}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
