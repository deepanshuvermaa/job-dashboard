"use client";
import { useEffect } from "react";
import GradeBadge from "./GradeBadge";

interface Props { job: any | null; onClose: () => void; onBookmark: (id: string, val: boolean) => void; }

const DIMS = [
  { key: "role_match", label: "Role Match" }, { key: "skills_alignment", label: "Skills" },
  { key: "seniority_fit", label: "Seniority" }, { key: "compensation", label: "Compensation" },
  { key: "interview_likelihood", label: "Interview" }, { key: "growth_potential", label: "Growth" },
  { key: "company_reputation", label: "Reputation" }, { key: "location_fit", label: "Location" },
  { key: "tech_stack_match", label: "Tech Stack" }, { key: "culture_signals", label: "Culture" },
];

function RadarChart({ ev }: { ev: any }) {
  const s = 200, cx = s/2, cy = s/2, maxR = 80;
  const dims = DIMS.map((d, i) => ({ ...d, angle: (Math.PI * 2 * i) / DIMS.length - Math.PI / 2, value: (ev[d.key] || 0) / 10 }));
  const gridPaths = [0.25, 0.5, 0.75, 1].map(level => {
    const pts = dims.map(d => `${cx + maxR * level * Math.cos(d.angle)},${cy + maxR * level * Math.sin(d.angle)}`).join(" ");
    return `M${pts.split(" ")[0]} L${pts.split(" ").slice(1).join(" L")} Z`;
  });
  const dataPts = dims.map(d => `${cx + maxR * d.value * Math.cos(d.angle)},${cy + maxR * d.value * Math.sin(d.angle)}`);
  return (
    <svg viewBox={`0 0 ${s} ${s}`} className="w-full max-w-[200px] mx-auto">
      {gridPaths.map((p, i) => <path key={i} d={p} fill="none" stroke="#e5e5e5" strokeWidth="0.5" />)}
      {dims.map((d, i) => <line key={i} x1={cx} y1={cy} x2={cx + maxR * Math.cos(d.angle)} y2={cy + maxR * Math.sin(d.angle)} stroke="#e5e5e5" strokeWidth="0.5" />)}
      <polygon points={dataPts.join(" ")} fill="rgba(0,0,0,0.04)" stroke="#000000" strokeWidth="1.5" />
      {dims.map((d, i) => { const r = maxR * d.value; return <circle key={i} cx={cx + r * Math.cos(d.angle)} cy={cy + r * Math.sin(d.angle)} r="2.5" fill="#000000" />; })}
      {dims.map((d, i) => { const lr = maxR + 16; return <text key={i} x={cx + lr * Math.cos(d.angle)} y={cy + lr * Math.sin(d.angle)} textAnchor="middle" dominantBaseline="middle" fill="#777169" fontSize="7">{d.label}</text>; })}
    </svg>
  );
}

export default function JobDetailDrawer({ job, onClose, onBookmark }: Props) {
  useEffect(() => {
    const fn = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", fn);
    return () => document.removeEventListener("keydown", fn);
  }, [onClose]);

  if (!job) return null;
  const ev = job.evaluation;

  return (
    <>
      <div className="fixed inset-0 bg-obsidian/20 z-40" onClick={onClose} />
      <div className="fixed right-0 top-0 h-full w-full max-w-[500px] bg-eggshell z-50 overflow-y-auto shadow-card">
        {/* Header */}
        <div className="sticky top-0 z-10 px-6 py-4 flex items-center justify-between bg-eggshell border-b border-chalk">
          <div className="flex items-center gap-3">
            {ev && <GradeBadge grade={ev.grade} score={ev.overall_score} size="lg" />}
            <span className="text-body-medium text-obsidian">{job.company}</span>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-powder transition-colors">
            <svg className="w-4 h-4 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          </button>
        </div>

        <div className="px-6 py-6 space-y-6">
          {/* Title */}
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-badge bg-powder border border-chalk flex items-center justify-center flex-shrink-0 overflow-hidden">
              {job.company_logo_url ? (
                <img src={job.company_logo_url} alt="" className="w-8 h-8 object-contain" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; (e.target as HTMLImageElement).parentElement!.innerHTML = `<span style="color:#777169;font-size:16px;font-weight:600">${job.company[0]}</span>`; }} />
              ) : <span className="text-[16px] font-semibold text-gravel">{job.company[0]}</span>}
            </div>
            <div>
              <h2 className="text-heading-sm text-obsidian font-display">{job.title}</h2>
              <p className="text-body text-gravel mt-1">{job.company} · {job.location}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <a href={job.job_url} target="_blank" rel="noopener noreferrer" className="btn-primary flex-1 text-center">Apply Now</a>
            <button onClick={() => onBookmark(job.id, !job.is_bookmarked)} className="btn-secondary">{job.is_bookmarked ? "Saved" : "Save"}</button>
          </div>

          {/* Tags */}
          <div className="flex flex-wrap gap-2">
            {job.work_mode && <span className="tag">{job.work_mode}</span>}
            {job.experience_level && <span className="tag">{job.experience_level} level</span>}
            {job.employment_type && <span className="tag">{job.employment_type.replace("-", " ")}</span>}
            {job.is_easy_apply && <span className="tag-active">Easy Apply</span>}
          </div>

          {/* Salary */}
          {(job.salary_min || job.salary_max) && (
            <div className="bg-powder rounded-card p-4">
              <p className="text-label text-gravel uppercase">Salary Range</p>
              <p className="text-heading text-obsidian font-display mt-1">
                {job.salary_min && `$${(job.salary_min / 1000).toFixed(0)}k`}
                {job.salary_min && job.salary_max && " – "}
                {job.salary_max && `$${(job.salary_max / 1000).toFixed(0)}k`}
                <span className="text-body text-gravel"> /{job.salary_period || "year"}</span>
              </p>
            </div>
          )}

          {/* Skills */}
          {job.skills_required?.length > 0 && (
            <div>
              <h3 className="text-body-medium text-obsidian mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {job.skills_required.map((skill: string) => {
                  const matched = job.skills_matched?.includes(skill);
                  return (
                    <span key={skill} className={`px-3 py-1 rounded-pill text-caption ${matched ? "bg-green-50 text-green-700 border border-green-200" : "bg-powder text-gravel border border-chalk"}`}>
                      {matched && <svg className="w-3 h-3 inline mr-1 -mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg>}
                      {skill}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Radar */}
          {ev && (
            <div>
              <h3 className="text-body-medium text-obsidian mb-4">Evaluation</h3>
              <RadarChart ev={ev} />
              <div className="mt-4 space-y-2">
                {DIMS.map((d) => (
                  <div key={d.key} className="flex items-center gap-3">
                    <span className="text-caption text-gravel w-24 text-right flex-shrink-0">{d.label}</span>
                    <div className="flex-1 score-track"><div className="score-fill bg-obsidian" style={{ width: `${(ev[d.key] || 0) * 10}%` }} /></div>
                    <span className="text-caption text-cinder w-6">{Math.round(ev[d.key] || 0)}</span>
                  </div>
                ))}
              </div>
              {ev.reasoning && <p className="text-caption text-gravel italic mt-4">{ev.reasoning}</p>}
            </div>
          )}

          {/* Description */}
          <div>
            <h3 className="text-body-medium text-obsidian mb-3">Description</h3>
            <p className="text-body text-cinder leading-[1.6] whitespace-pre-line">{job.description_full || job.description_snippet}</p>
          </div>

          <div className="divider" />
          <div className="space-y-1">
            <p className="text-caption text-fog">Source: {job.source} · Seen {job.times_seen}x</p>
            {job.posted_date && <p className="text-caption text-fog">Posted: {new Date(job.posted_date).toLocaleDateString()}</p>}
          </div>
        </div>
      </div>
    </>
  );
}
