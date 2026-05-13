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

const SEED_CONTACTS: Recruiter[] = [
  { name: "Sergio Saborio", company: "Flexport", profile_url: "https://linkedin.com/in/sergiosaborio", source: "spreadsheet" },
  { name: "Dmitry Aflitonov", company: "Bolt (EU)", profile_url: "https://linkedin.com/in/dmitry-aflitonov-3a784b9b", source: "spreadsheet" },
  { name: "N. Stachowicz", company: "CKSource", email: "n.stachowicz@cksource.com", source: "spreadsheet" },
  { name: "Pragati Singh", company: "GrayQuest", profile_url: "https://linkedin.com/in/pragati-singh-bb9388191", source: "spreadsheet" },
  { name: "C. Goncalves", company: "Benevity", email: "Cgoncalves@benevity.com", source: "spreadsheet" },
  { name: "C. Deveis", company: "Pure Storage", email: "cdeveis@purestorage.com", source: "spreadsheet" },
  { name: "Rachel", company: "Grow Therapy", email: "rachel@growtherapy.com", source: "spreadsheet" },
  { name: "Tech Hiring", company: "Monzo", email: "tech-hiring@monzo.com", source: "spreadsheet" },
  { name: "Tech", company: "Walgreens", email: "tech@wba.com", source: "spreadsheet" },
  { name: "Carrie Collier", company: "Appian", email: "carrie.collier@appian.com", source: "spreadsheet" },
  { name: "Andrew Joynt", company: "Olo", email: "andrew.joynt@olo.com", source: "spreadsheet" },
  { name: "Jin Wu", company: "PlayStation (Sony)", profile_url: "https://linkedin.com/in/jinwurecruits", source: "spreadsheet" },
  { name: "Tanzeem Nayaz", company: "TuringMinds", profile_url: "https://linkedin.com/in/tanzeemnayaz", source: "spreadsheet" },
  { name: "Careers", company: "Condor Software", email: "careers@condorsoftware.com", source: "spreadsheet" },
  { name: "Careers", company: "TLG Aerospace", email: "careers@tlgaerospace.com", source: "spreadsheet" },
  { name: "Yana Busko", company: "Planner 5D", profile_url: "https://linkedin.com/in/yana-busko-98bb2572", source: "spreadsheet" },
  { name: "Matthew Blais", company: "In-House", profile_url: "https://linkedin.com/in/matthew-blais-b68472121", source: "spreadsheet" },
];

export default function RecruitersPage() {
  const [recruiters, setRecruiters] = useState<Recruiter[]>([]);
  const [loading, setLoading] = useState(true);
  const [manualName, setManualName] = useState("");
  const [manualEmail, setManualEmail] = useState("");
  const [manualCompany, setManualCompany] = useState("");

  useEffect(() => { fetchRecruiters(); }, []);

  const fetchRecruiters = async () => {
    setLoading(true);
    try {
      const data = await api.getJobs({ per_page: 100 });
      const found: Recruiter[] = [];
      const seen = new Set<string>();
      for (const job of data.jobs || []) {
        if (job.hr_name || job.hr_email) {
          const key = `${job.hr_name}|${job.hr_email}`;
          if (!seen.has(key)) { seen.add(key); found.push({ name: job.hr_name || "", email: job.hr_email || "", company: job.company, source: job.source }); }
        }
      }
      const saved = JSON.parse(localStorage.getItem("saved_recruiters") || "[]");
      // Seed with spreadsheet contacts if localStorage is empty
      if (saved.length === 0) {
        const seed = SEED_CONTACTS.filter(c => c.name && c.name !== "Careers" && c.name !== "Tech-Hiring");
        localStorage.setItem("saved_recruiters", JSON.stringify(seed));
        setRecruiters([...seed, ...found]);
      } else {
        setRecruiters([...saved, ...found]);
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const addManual = () => {
    if (!manualName && !manualEmail) return;
    const newR: Recruiter = { name: manualName, email: manualEmail, company: manualCompany, source: "manual" };
    const updated = [newR, ...recruiters];
    setRecruiters(updated);
    const saved = JSON.parse(localStorage.getItem("saved_recruiters") || "[]");
    saved.unshift(newR);
    localStorage.setItem("saved_recruiters", JSON.stringify(saved));
    setManualName(""); setManualEmail(""); setManualCompany("");
  };

  const handleFileImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      if (!text) return;
      const lines = text.split("\n").filter(l => l.trim());
      const headers = lines[0].toLowerCase().split(",").map(h => h.trim().replace(/"/g, ""));
      const nameIdx = headers.findIndex(h => h.includes("name"));
      const emailIdx = headers.findIndex(h => h.includes("email"));
      const companyIdx = headers.findIndex(h => h.includes("company"));

      const imported: Recruiter[] = [];
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(",").map(c => c.trim().replace(/"/g, ""));
        const name = cols[nameIdx >= 0 ? nameIdx : 0] || "";
        const email = cols[emailIdx >= 0 ? emailIdx : 1] || "";
        const company = cols[companyIdx >= 0 ? companyIdx : 2] || "";
        if (name || email) imported.push({ name, email, company, source: "import" });
      }

      const saved = JSON.parse(localStorage.getItem("saved_recruiters") || "[]");
      saved.push(...imported);
      localStorage.setItem("saved_recruiters", JSON.stringify(saved));
      setRecruiters(prev => [...imported, ...prev]);
      alert(`Imported ${imported.length} contacts`);
    };
    reader.readAsText(file);
  };

  const exportAll = () => {
    const csv = "Name,Email,Company,Source\n" + recruiters.map(r => `"${r.name}","${r.email || ""}","${r.company}","${r.source}"`).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "recruiters.csv"; a.click();
  };

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-heading text-obsidian font-display">Recruiter Contacts</h1>
          <p className="text-body text-gravel mt-1">HR contacts from scraping, imports & manual entries</p>
        </div>
        <div className="flex gap-2">
          <label className="btn-secondary flex items-center gap-2 cursor-pointer">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
            Import CSV
            <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={e => { if (e.target.files?.[0]) handleFileImport(e.target.files[0]); }} />
          </label>
          <button onClick={exportAll} className="btn-secondary flex items-center gap-2">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            Export
          </button>
        </div>
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
          <p className="text-caption text-fog mt-1">Import a CSV or add manually</p>
        </div>
      ) : (
        <div className="space-y-2">
          <p className="text-caption text-gravel mb-2">{recruiters.length} contacts</p>
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
                <a href={`/outreach?emails=${encodeURIComponent(r.email)}&company=${encodeURIComponent(r.company)}`} className="text-[11px] text-blue-600 hover:underline">Cold Email</a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
