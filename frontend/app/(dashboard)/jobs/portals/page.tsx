"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function PortalsPage() {
  const [config, setConfig] = useState<any>(null);

  useEffect(() => {
    api.getPortalConfig().then(setConfig).catch(console.error);
  }, []);

  const portals = config?.portals || [];
  const queries = config?.search_queries || [];
  const enabledCount = portals.filter((p: any) => p.enabled !== false).length;

  const atsCounts: Record<string, number> = {};
  portals.forEach((p: any) => {
    const ats = p.ats || "unknown";
    atsCounts[ats] = (atsCounts[ats] || 0) + 1;
  });

  return (
    <div className="px-8 py-6 max-w-wide mx-auto">
      <h1 className="text-heading text-obsidian font-display">Portal Scanner</h1>
      <p className="text-body text-gravel mt-1">
        {enabledCount} career pages + {queries.length} search queries across 696+ companies
      </p>

      <div className="card mb-6 mt-8">
        <h2 className="text-body-medium text-obsidian mb-4">ATS Type Breakdown</h2>
        <div className="flex flex-wrap gap-2">
          {Object.entries(atsCounts)
            .sort(([, a], [, b]) => (b as number) - (a as number))
            .map(([ats, count]) => (
              <span key={ats} className="px-3 py-1.5 bg-powder rounded-full text-caption text-cinder">
                {ats} <span className="text-obsidian font-semibold ml-1">{count as number}</span>
              </span>
            ))}
        </div>
      </div>

      <div className="card">
        <h2 className="text-body-medium text-obsidian mb-4">Configured Portals ({portals.length})</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {portals.map((portal: any, i: number) => (
            <div key={i} className={`p-3 rounded-lg border text-center ${portal.enabled !== false ? "border-chalk bg-powder" : "border-chalk bg-powder opacity-50"}`}>
              <p className="text-caption-strong text-obsidian truncate">{portal.name}</p>
              <p className="text-caption text-gravel mt-0.5">{portal.ats}</p>
              <span className={`inline-block mt-1 w-2 h-2 rounded-full ${portal.enabled !== false ? "bg-grade-a" : "bg-gravel"}`} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
