"use client";
import GradeBadge from "./GradeBadge";

interface JobCardProps {
  job: any;
  onClick: (job: any) => void;
  onBookmark: (id: string, val: boolean) => void;
  onMarkApplied?: (id: string) => void;
}

function formatSalary(min?: number, max?: number, period?: string) {
  if (!min && !max) return null;
  const fmt = (n: number) => n >= 1000 ? `$${Math.round(n / 1000)}k` : `$${n}`;
  const p = period === "monthly" ? "/mo" : period === "hourly" ? "/hr" : "/yr";
  if (min && max) return `${fmt(min)}–${fmt(max)}${p}`;
  if (min) return `${fmt(min)}+${p}`;
  return `Up to ${fmt(max!)}${p}`;
}

const DIMS: [string, string][] = [
  ["role_match", "Role"], ["skills_alignment", "Skills"], ["seniority_fit", "Level"],
  ["compensation", "Pay"], ["interview_likelihood", "Interview"],
  ["growth_potential", "Growth"], ["company_reputation", "Company"],
  ["location_fit", "Location"], ["tech_stack_match", "Tech"], ["culture_signals", "Culture"],
];

export default function JobCard({ job, onClick, onBookmark, onMarkApplied }: JobCardProps) {
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_period);
  const ev = job.evaluation;

  return (
    <div onClick={() => onClick(job)} className="card cursor-pointer group flex flex-col transition-shadow">
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-badge bg-powder border border-chalk flex items-center justify-center overflow-hidden flex-shrink-0">
          {job.company_logo_url ? (
            <img src={job.company_logo_url} alt="" className="w-7 h-7 object-contain" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; (e.target as HTMLImageElement).parentElement!.innerHTML = `<span style="color:#777169;font-size:14px;font-weight:600">${job.company?.[0] || "?"}</span>`; }} />
          ) : (
            <span className="text-[14px] font-semibold text-gravel">{job.company?.[0] || "?"}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-body-medium text-obsidian leading-tight truncate">{job.title}</h3>
          <p className="text-caption text-gravel mt-0.5 truncate">{job.company} · {job.location}</p>
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Mark Applied */}
          {onMarkApplied && (
            <button onClick={(e) => { e.stopPropagation(); onMarkApplied(job.id); }} className="p-1 rounded-lg hover:bg-green-50 transition-colors" title="Mark as Applied">
              <svg className="w-4 h-4 text-green-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 9V5a3 3 0 00-6 0v4" /><path d="M20 9H4l1 11h14l1-11z" /><path d="M8 14l2 2 4-4" />
              </svg>
            </button>
          )}
          {/* Bookmark */}
          <button onClick={(e) => { e.stopPropagation(); onBookmark(job.id, !job.is_bookmarked); }} className="p-1 rounded-lg hover:bg-powder transition-colors">
            <svg className={`w-4 h-4 ${job.is_bookmarked ? "text-obsidian fill-obsidian" : "text-chalk"}`} viewBox="0 0 24 24" fill={job.is_bookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
              <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {job.work_mode && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.work_mode}</span>}
        {job.experience_level && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.experience_level}</span>}
        {job.employment_type && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.employment_type.replace("-", " ")}</span>}
        {job.is_easy_apply && <span className="tag !py-0.5 !px-2 !text-[11px] !bg-green-50 !text-green-700 !border-green-200">Easy Apply</span>}
      </div>

      {/* Snippet */}
      <p className="text-caption text-gravel leading-[1.5] line-clamp-2 mb-3 flex-1">{job.description_snippet}</p>

      {/* 10-Dimension Evaluation */}
      {ev && ev.overall_score != null && (
        <div className="mb-3 pt-2 border-t border-chalk">
          <div className="flex items-center gap-2 mb-1.5">
            <GradeBadge grade={ev.grade} score={ev.overall_score} size="sm" />
            <span className="text-[10px] text-gravel">Profile Match</span>
          </div>
          <div className="grid grid-cols-5 gap-x-2 gap-y-1">
            {DIMS.map(([key, label]) => {
              const val = ev[key];
              if (val == null) return null;
              const color = val >= 7 ? "text-green-600" : val >= 4 ? "text-amber-600" : "text-red-500";
              return (
                <div key={key} className="flex items-center gap-0.5">
                  <span className={`text-[10px] font-semibold ${color}`}>{Math.round(val)}</span>
                  <span className="text-[9px] text-fog truncate">{label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-chalk">
        <div className="flex-1 min-w-0">
          {salary ? (
            <span className="text-body-medium text-obsidian">{salary}</span>
          ) : (job.hr_name || job.hr_email) ? (
            <div className="flex items-center gap-1.5" onClick={e => e.stopPropagation()}>
              <svg className="w-3 h-3 text-gravel flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 3a4 4 0 100 8 4 4 0 000-8z"/></svg>
              <span className="text-[11px] truncate">
                {job.hr_name && <span className="font-medium text-obsidian">{job.hr_name}</span>}
                {job.hr_email && <a href={`mailto:${job.hr_email}`} className="ml-1 text-blue-600 hover:underline" onClick={e => e.stopPropagation()}>{job.hr_email}</a>}
              </span>
            </div>
          ) : (
            <span className="text-caption text-fog">Salary unlisted</span>
          )}
        </div>
        <span className="text-[10px] font-medium text-gravel px-2 py-0.5 rounded-pill border border-chalk flex-shrink-0">{job.source}</span>
      </div>
    </div>
  );
}
