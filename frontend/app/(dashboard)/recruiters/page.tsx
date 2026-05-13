"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface Recruiter {
  name: string;
  email?: string;
  company: string;
  title?: string;
  profile_url?: string;
  source: string;
}

export default function RecruitersPage() {
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [loading, setLoading] = useState(true);
  const [manualName, setManualName] = useState("");
  const [manualEmail, setManualEmail] = useState("");
  const [manualCompany, setManualCompany] = useState("");

  useEffect(() => {
    fetchRecruiters();
  }, []);

  const fetchRecruiters = async () => {
    setLoading(true);
    try {
      // Get jobs that have HR info
      const data = await api.getJobs({ per_page: 100 });
      const found: Recruiter[] = [];
      const seen = new Set<string>();
      for (const job of data.jobs || []) {
        if (job.hr_name || job.hr_email) {
          const key = `${job.hr_name}|${job.hr_email}`;
          if (!seen.has(key)) {
            seen.add(key);
            found.push({ name: job.hr_name || "", email: job.hr_email || "", company: job.company, source: job.source });
          }
        }
      }
      // Load saved recruiters from localStorage
      const saved = JSON.parse(localStorage.getItem("saved_recruiters") || "[]");
      setRecruiters([...saved, ...found]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addManual = () => {
    if (!manualName && !manualEmail) return;
    const newR: Recruiter = { name: manualName, email: manualEmail, company: manualCompany, source: "manual" };
    const updated = [newR, ...recruiters];
    setRecruiters(updated);
    // Save manual ones to localStorage
    const saved = JSON.parse(localStorage.getItem("saved_recruiters") || "[]");
    saved.unshift(newR);
    localStorage.setItem("saved_recruiters", JSON.stringify(saved));
    setManualName(""); setManualEmail(""); setManualCompany("");
  };

  const sendToOutreach = (r: Recruiter) => {
    // Navigate to outreach with pre-filled email
    window.location.href = `/outreach?email=${encodeURIComponent(r.email || "")}`;
  };

  const exportAll = () => {
    const csv = "Name,Email,Company,Source\n" + recruiters.map(r => `"${r.name}","${r.email || ""}","${r.company}","${r.source}"`).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "recruiters.csv"; a.click();
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-heading text-obsidian font-display">Recruiter Contacts</h1>
          <p className="text-body text-gravel mt-1">HR contacts collected from job scraping & manual entries</p>
        </div>
        <button onClick={exportAll} className="btn-secondary flex items-center gap-2">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
          Export CSV
        </button>
      </div>

      {/* Add Manual */}
      <div className="card mb-6">
        <h3 className="text-body-medium text-obsidian mb-3">Add Contact</h3>
        <div className="flex gap-3">
          <input value={manualName} onChange={e => setManualName(e.target.value)} placeholder="Name" className="flex-1 px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
          <input value={manualEmail} onChange={e => setManualEmail(e.target.value)} placeholder="Email" className="flex-1 px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
          <input value={manualCompany} onChange={e => setManualCompany(e.target.value)} placeholder="Company" className="flex-1 px-3 py-2 border border-chalk rounded-lg text-[13px] bg-eggshell focus:outline-none focus:border-obsidian" />
          <button onClick={addManual} className="btn-primary">Add</button>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-obsidian border-t-transparent rounded-full animate-spin" /></div>
      ) : recruiters.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-body text-gravel">No recruiter contacts yet</p>
          <p className="text-caption text-fog mt-1">They'll appear here as jobs are scraped with HR info</p>
        </div>
      ) : (
        <div className="space-y-2">
          {recruiters.map((r, i) => (
            <div key={i} className="card flex items-center gap-4">
              <div className="w-9 h-9 rounded-full bg-powder border border-chalk flex items-center justify-center flex-shrink-0">
                <span className="text-[12px] font-semibold text-gravel">{r.name?.[0]?.toUpperCase() || "?"}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[13px] text-obsidian font-medium truncate">{r.name || "Unknown"}</p>
                <p className="text-[11px] text-gravel truncate">{r.company}{r.email ? ` · ${r.email}` : ""}</p>
              </div>
              <span className="text-[10px] font-medium text-gravel px-2 py-0.5 rounded-pill border border-chalk">{r.source}</span>
              {r.email && (
                <button onClick={() => sendToOutreach(r)} className="text-[11px] text-blue-600 hover:underline">Cold Email</button>
              )}
              {r.profile_url && (
                <a href={r.profile_url} target="_blank" rel="noopener" className="text-[11px] text-blue-600 hover:underline">LinkedIn</a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
