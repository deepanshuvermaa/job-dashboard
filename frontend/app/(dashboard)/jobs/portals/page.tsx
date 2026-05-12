"use client";
import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";

export default function PortalsPage() {
  const [config, setConfig] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState<any>(null);
  const [results, setResults] = useState<any>(null);
  const [keywordFilter, setKeywordFilter] = useState("");
  const [locationFilter, setLocationFilter] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [detectProgress, setDetectProgress] = useState<any>(null);
  const pollRef = useRef<any>(null);

  useEffect(() => {
    api.getPortalConfig().then(setConfig).catch(console.error);
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const startScan = async () => {
    setScanning(true);
    setResults(null);
    try {
      await api.scanPortals({
        keyword_filter: keywordFilter || undefined,
        location_filter: locationFilter || undefined,
      });
      // Poll for status
      pollRef.current = setInterval(async () => {
        try {
          const status = await api.getScanStatus();
          setScanProgress(status);
          if (status.complete || status.status === "complete") {
            clearInterval(pollRef.current);
            setScanning(false);
            setResults(status);
            // Ingest results into v2 table
            if (status.jobs?.length > 0) {
              try { await api.ingestJobs(status.jobs, "portal_scan"); } catch {}
            }
          }
        } catch { clearInterval(pollRef.current); setScanning(false); }
      }, 2000);
    } catch (err: any) {
      setScanning(false);
      alert(err.message);
    }
  };

  const startDetect = async () => {
    setDetecting(true);
    try {
      await api.detectATS();
      const poll = setInterval(async () => {
        try {
          const status = await api.getDetectStatus();
          setDetectProgress(status);
          if (status.complete) { clearInterval(poll); setDetecting(false); }
        } catch { clearInterval(poll); setDetecting(false); }
      }, 3000);
    } catch (err: any) {
      setDetecting(false);
      alert(err.message);
    }
  };

  const portals = config?.portals || [];
  const queries = config?.search_queries || [];
  const enabledCount = portals.filter((p: any) => p.enabled !== false).length;

  // Group by ATS
  const atsCounts: Record<string, number> = {};
  portals.forEach((p: any) => { const ats = p.ats || "unknown"; atsCounts[ats] = (atsCounts[ats] || 0) + 1; });

  return (
    <div className="px-8 py-6 max-w-wide mx-auto">
      <h1 className="text-heading text-obsidian font-display">Portal Scanner</h1>
      <p className="text-body text-gravel mt-1">
        Scan {enabledCount} career pages + {queries.length} search queries across 696+ companies
      </p>

      {/* Scan Controls */}
      <div className="card mb-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-body-medium text-obsidian">Scan Configuration</h2>
          <button onClick={() => setShowFilters(!showFilters)} className="text-caption text-obsidian hover:underline">
            {showFilters ? "Hide Filters" : "Show Filters"}
          </button>
        </div>

        {showFilters && (
          <div className="grid grid-cols-2 gap-4 mb-4 p-4 bg-powder rounded-lg">
            <div>
              <label className="block text-caption text-gravel mb-1">Keyword Filter</label>
              <input value={keywordFilter} onChange={(e) => setKeywordFilter(e.target.value)} className="input-el !rounded-sm text-caption" placeholder="e.g. Python, React" />
            </div>
            <div>
              <label className="block text-caption text-gravel mb-1">Location Filter</label>
              <input value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)} className="input-el !rounded-sm text-caption" placeholder="e.g. Remote, San Francisco" />
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <button onClick={startScan} disabled={scanning} className="btn-primary disabled:opacity-50">
            {scanning ? "Scanning..." : "Scan All Portals"}
          </button>
          <button onClick={startDetect} disabled={detecting} className="btn-secondary disabled:opacity-50">
            {detecting ? "Detecting..." : "Detect ATS (600+ Companies)"}
          </button>
        </div>
      </div>

      {/* Scan Progress */}
      {scanning && scanProgress && (
        <div className="card mb-6 border-obsidian/20">
          <h3 className="text-body-medium text-obsidian mb-3">Scanning in progress...</h3>
          <div className="w-full h-2 bg-powder rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-obsidian rounded-full transition-all duration-300"
              style={{ width: `${((scanProgress.completed || 0) / Math.max(1, scanProgress.total || 1)) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-caption text-gravel">
            <span>Portal: {scanProgress.current_portal || "..."}</span>
            <span>{scanProgress.completed || 0}/{scanProgress.total || "?"} complete</span>
          </div>
          {scanProgress.jobs_found > 0 && (
            <p className="text-caption text-grade-a mt-2">{scanProgress.jobs_found} jobs found so far</p>
          )}
        </div>
      )}

      {/* ATS Detection Progress */}
      {detecting && detectProgress && (
        <div className="card mb-6 border-obsidian/20">
          <h3 className="text-body-medium text-obsidian mb-3">Detecting ATS types...</h3>
          <div className="w-full h-2 bg-powder rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-grade-c rounded-full transition-all duration-300"
              style={{ width: `${((detectProgress.completed || 0) / Math.max(1, detectProgress.total || 1)) * 100}%` }}
            />
          </div>
          <p className="text-caption text-gravel">{detectProgress.completed || 0}/{detectProgress.total || "?"} companies analyzed</p>
        </div>
      )}

      {/* Scan Results */}
      {results && (
        <div className="card mb-6 border-grade-a/30">
          <h3 className="text-body-medium text-obsidian mb-3">Scan Complete</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div><p className="text-caption text-gravel">Total Scraped</p><p className="text-heading text-obsidian">{results.total_scraped || 0}</p></div>
            <div><p className="text-caption text-gravel">New Jobs</p><p className="text-heading text-grade-a">{results.new_jobs || 0}</p></div>
            <div><p className="text-caption text-gravel">Duplicates</p><p className="text-heading text-gravel">{results.duplicates_skipped || 0}</p></div>
            <div><p className="text-caption text-gravel">Saved to DB</p><p className="text-heading text-obsidian">{results.saved_to_db || 0}</p></div>
          </div>
        </div>
      )}

      {/* ATS Type Breakdown */}
      <div className="card mb-6">
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

      {/* Portal Grid */}
      <div className="card">
        <h2 className="text-body-medium text-obsidian mb-4">
          Configured Portals ({portals.length})
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {portals.map((portal: any, i: number) => (
            <div
              key={i}
              className={`p-3 rounded-lg border text-center transition-colors ${
                portal.enabled !== false
                  ? "border-chalk bg-powder hover:border-gravel"
                  : "border-chalk bg-powder opacity-50"
              }`}
            >
              <p className="text-caption-strong text-obsidian truncate">{portal.name}</p>
              <p className="text-caption text-gravel mt-0.5">{portal.ats}</p>
              <span className={`inline-block mt-1 w-2 h-2 rounded-full ${portal.enabled !== false ? "bg-grade-a" : "bg-gravel"}`} />
            </div>
          ))}
        </div>
      </div>

      {/* Search Queries */}
      {queries.length > 0 && (
        <div className="card mt-6">
          <h2 className="text-body-medium text-obsidian mb-4">Search Queries ({queries.length})</h2>
          <div className="flex flex-wrap gap-2">
            {queries.map((q: any, i: number) => (
              <span key={i} className="px-3 py-1.5 bg-powder rounded-full text-caption text-cinder">
                {typeof q === "string" ? q : q.keywords || q.query || JSON.stringify(q)}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
