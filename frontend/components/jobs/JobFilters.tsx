"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface FilterState {
  search: string;
  category: string;
  source: string;
  grade: string;
  work_mode: string;
  sort: string;
  bookmarked: boolean;
  posted_after: string;
  location: string;
  salary_min: string;
  experience_level: string;
  easy_apply: boolean;
  company: string;
}

interface Props {
  filters: FilterState;
  onChange: (f: FilterState) => void;
  stats: any;
  total: number;
}

const CATEGORIES = [
  { key: "", label: "All" }, { key: "backend", label: "Backend" }, { key: "frontend", label: "Frontend" },
  { key: "fullstack", label: "Full Stack" }, { key: "devops", label: "DevOps" }, { key: "data", label: "Data" },
  { key: "ai_ml", label: "AI/ML" }, { key: "design", label: "Design" }, { key: "product", label: "Product" },
  { key: "other", label: "Other" },
];

export default function JobFilters({ filters, onChange, stats, total }: Props) {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [locations, setLocations] = useState<any[]>([]);

  useEffect(() => {
    api.getLocations().then(setLocations).catch(() => {});
  }, []);

  const set = (key: keyof FilterState, value: any) => onChange({ ...filters, [key]: value });

  // Extract top locations for quick-pick (India focused)
  const indiaLocations = locations.filter((l: any) =>
    /india|bengaluru|bangalore|mumbai|hyderabad|pune|delhi|gurgaon|noida|chennai|kolkata|remote/i.test(l.name)
  );

  return (
    <div className="space-y-4 mb-6">
      {/* Row 1: Search + key controls */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 min-w-[250px]">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-fog" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
          <input type="text" value={filters.search} onChange={(e) => set("search", e.target.value)} placeholder="Search jobs or companies..." className="input-el !pl-10 !rounded-pill" />
        </div>

        <select value={filters.posted_after} onChange={(e) => set("posted_after", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
          <option value="">Any Time</option>
          <option value="1d">Last 24 hours</option>
          <option value="3d">Last 3 days</option>
          <option value="7d">Last 7 days</option>
          <option value="14d">Last 2 weeks</option>
          <option value="30d">Last 30 days</option>
        </select>

        <select value={filters.location} onChange={(e) => set("location", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
          <option value="">All Locations</option>
          <option value="india">India</option>
          <option value="remote">Remote</option>
          <option value="bangalore">Bangalore</option>
          <option value="mumbai">Mumbai</option>
          <option value="hyderabad">Hyderabad</option>
          <option value="pune">Pune</option>
          <option value="delhi">Delhi / NCR</option>
          <option value="chennai">Chennai</option>
          <option value="united states">United States</option>
          <option value="san francisco">San Francisco</option>
          <option value="new york">New York</option>
          <option value="london">London</option>
        </select>

        <select value={filters.source} onChange={(e) => set("source", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
          <option value="">All Sources</option>
          <option value="greenhouse">Greenhouse</option>
          <option value="lever">Lever</option>
          <option value="ashby">Ashby</option>
          <option value="reddit">Reddit</option>
          <option value="linkedin">LinkedIn</option>
        </select>

        <button onClick={() => setShowAdvanced(!showAdvanced)} className="btn-ghost text-[13px]">
          {showAdvanced ? "Less filters" : "More filters"}
          <svg className={`w-3 h-3 ml-1 inline transition-transform ${showAdvanced ? "rotate-180" : ""}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9" /></svg>
        </button>
      </div>

      {/* Row 2: Advanced filters (collapsible) */}
      {showAdvanced && (
        <div className="flex items-center gap-3 flex-wrap p-4 bg-powder rounded-card">
          <select value={filters.experience_level} onChange={(e) => set("experience_level", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
            <option value="">All Experience</option>
            <option value="entry">Entry Level</option>
            <option value="mid">Mid Level (1-3 yrs)</option>
            <option value="senior">Senior (3+ yrs)</option>
            <option value="lead">Lead / Staff</option>
          </select>

          <select value={filters.work_mode} onChange={(e) => set("work_mode", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
            <option value="">All Work Modes</option>
            <option value="remote">Remote</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
          </select>

          <select value={filters.salary_min} onChange={(e) => set("salary_min", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
            <option value="">Any Salary</option>
            <option value="50000">$50k+</option>
            <option value="80000">$80k+</option>
            <option value="100000">$100k+</option>
            <option value="150000">$150k+</option>
            <option value="200000">$200k+</option>
          </select>

          <select value={filters.sort} onChange={(e) => set("sort", e.target.value)} className="input-el !w-auto !rounded-pill text-[13px]">
            <option value="newest">Newest First</option>
            <option value="score">Best Score</option>
            <option value="company">Company A-Z</option>
          </select>

          <label className="flex items-center gap-2 text-[13px] text-cinder cursor-pointer select-none">
            <input type="checkbox" checked={filters.easy_apply} onChange={(e) => set("easy_apply", e.target.checked)} className="w-4 h-4 accent-obsidian rounded" />
            Easy Apply only
          </label>

          <button onClick={() => set("bookmarked", !filters.bookmarked)} className={`btn-ghost flex items-center gap-1.5 text-[13px] ${filters.bookmarked ? "!text-obsidian !bg-powder font-medium" : ""}`}>
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill={filters.bookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" /></svg>
            Saved
          </button>
        </div>
      )}

      {/* Row 3: Category + Grade pills */}
      <div className="flex items-center gap-1.5 flex-wrap">
        {CATEGORIES.map((c) => (
          <button key={c.key} onClick={() => set("category", c.key)} className={filters.category === c.key ? "tag-active" : "tag"}>
            {c.label}
            {c.key && stats.categories?.[c.key] ? <span className="opacity-60 ml-0.5">{stats.categories[c.key]}</span> : null}
          </button>
        ))}
        <div className="w-px h-4 bg-chalk mx-1" />
        {[{ key: "", label: "All" }, { key: "A", label: "A" }, { key: "B", label: "B" }, { key: "C", label: "C" }].map((g) => (
          <button key={g.key} onClick={() => set("grade", g.key)} className={filters.grade === g.key ? "tag-active" : "tag"}>
            {g.key ? `Grade ${g.label}` : "All Grades"}
          </button>
        ))}
      </div>

      {/* Results count + active filter summary */}
      <div className="flex items-center justify-between">
        <p className="text-caption text-gravel">
          <span className="text-obsidian font-medium">{total}</span> jobs match your criteria
          {filters.location && <span> in <span className="text-obsidian capitalize">{filters.location}</span></span>}
        </p>
        {/* Clear all filters */}
        {(filters.posted_after || filters.location || filters.salary_min || filters.experience_level || filters.easy_apply || filters.company) && (
          <button onClick={() => onChange({
            search: "", category: "", source: "", grade: "", work_mode: "", sort: "newest",
            bookmarked: false, posted_after: "", location: "", salary_min: "", experience_level: "", easy_apply: false, company: "",
          })} className="text-caption text-gravel hover:text-obsidian underline">
            Clear all filters
          </button>
        )}
      </div>
    </div>
  );
}
