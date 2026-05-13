"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function HacksPage() {
  const [tab, setTab] = useState<"dorks" | "engage" | "group">("dorks");
  const [role, setRole] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("India");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleGoogleDork = async () => {
    setLoading(true);
    try {
      const res = await api.generateGoogleDork({ role: role || "Software Engineer", company, location });
      setResults(res);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  const handleRecruiterEngage = async () => {
    setLoading(true);
    try {
      const res = await api.recruiterEngage({ role: role || "Software Engineer", company, location });
      setResults(res);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  const handleGroupMessage = async () => {
    setLoading(true);
    try {
      const res = await api.groupMessage({ role: role || "Software Engineer", message_type: "introduction" });
      setResults(res);
    } catch (err) { console.error(err); } finally { setLoading(false); }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-heading text-obsidian font-display">LinkedIn Hacks</h1>
        <p className="text-body text-gravel mt-1">Google dorks, recruiter engagement strategies & group messaging</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-chalk">
        {[
          { id: "dorks", label: "Google Dorks" },
          { id: "engage", label: "Recruiter Engagement" },
          { id: "group", label: "Group Messaging" },
        ].map(t => (
          <button key={t.id} onClick={() => { setTab(t.id as any); setResults(null); }} className={`pb-2 text-[13px] font-medium border-b-2 transition-colors ${tab === t.id ? "border-obsidian text-obsidian" : "border-transparent text-gravel hover:text-obsidian"}`}>{t.label}</button>
        ))}
      </div>

      {/* Input */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input value={role} onChange={e => setRole(e.target.value)} placeholder="Target Role (e.g. Cloud Engineer)" className="px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
          <input value={company} onChange={e => setCompany(e.target.value)} placeholder="Company (optional)" className="px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
          <input value={location} onChange={e => setLocation(e.target.value)} placeholder="Location" className="px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
        </div>
        <button onClick={tab === "dorks" ? handleGoogleDork : tab === "engage" ? handleRecruiterEngage : handleGroupMessage} disabled={loading} className="btn-primary mt-3 disabled:opacity-50">
          {loading ? "Generating..." : tab === "dorks" ? "Generate Dorks" : tab === "engage" ? "Get Strategies" : "Generate Message"}
        </button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-4">
          {/* Google Dorks */}
          {results.dorks && (
            <div className="space-y-3">
              {results.dorks.map((dork: any, i: number) => (
                <div key={i} className="card">
                  <p className="text-[11px] text-gravel mb-1">{dork.description}</p>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-[12px] text-obsidian bg-powder px-3 py-2 rounded-lg font-mono break-all">{dork.query}</code>
                    <a href={`https://www.google.com/search?q=${encodeURIComponent(dork.query)}`} target="_blank" rel="noopener" className="btn-secondary text-[11px] flex-shrink-0">Search</a>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recruiter Engagement */}
          {results.strategies && (
            <div className="space-y-3">
              {results.strategies.map((s: any, i: number) => (
                <div key={i} className="card">
                  <h4 className="text-body-medium text-obsidian mb-1">{s.title}</h4>
                  <p className="text-[12px] text-gravel leading-relaxed">{s.description}</p>
                  {s.template && <pre className="mt-2 text-[11px] text-obsidian bg-powder px-3 py-2 rounded-lg whitespace-pre-wrap">{s.template}</pre>}
                </div>
              ))}
            </div>
          )}

          {/* Group Message */}
          {results.message && (
            <div className="card">
              <h4 className="text-body-medium text-obsidian mb-2">Generated Message</h4>
              <pre className="text-[12px] text-obsidian bg-powder px-4 py-3 rounded-lg whitespace-pre-wrap leading-relaxed">{results.message}</pre>
              <button onClick={() => navigator.clipboard.writeText(results.message)} className="btn-secondary mt-3 text-[11px]">Copy to Clipboard</button>
            </div>
          )}

          {/* Generic results */}
          {!results.dorks && !results.strategies && !results.message && (
            <div className="card">
              <pre className="text-[12px] text-obsidian whitespace-pre-wrap">{JSON.stringify(results, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
