"use client";
import GradeBadge from "./GradeBadge";

interface JobCardProps { job: any; onClick: (job: any) => void; onBookmark: (id: string, val: boolean) => void; }

function formatSalary(min?: number, max?: number, period?: string) {
  if (!min && !max) return null;
  const fmt = (n: number) => n >= 1000 ? `$${Math.round(n / 1000)}k` : `$${n}`;
  const p = period === "monthly" ? "/mo" : period === "hourly" ? "/hr" : "/yr";
  if (min && max) return `${fmt(min)}–${fmt(max)}${p}`;
  if (min) return `${fmt(min)}+${p}`;
  return `Up to ${fmt(max!)}${p}`;
}

export default function JobCard({ job, onClick, onBookmark }: JobCardProps) {
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_period);

  return (
    <div onClick={() => onClick(job)} className="card cursor-pointer group flex flex-col transition-shadow">
      {/* Header */}
      <div className="flex items-start gap-3 mb-3">
        <div className="w-10 h-10 rounded-badge bg-powder border border-chalk flex items-center justify-center overflow-hidden flex-shrink-0">
          {job.company_logo_url ? (
            <img src={job.company_logo_url} alt="" className="w-7 h-7 object-contain" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; (e.target as HTMLImageElement).parentElement!.innerHTML = `<span style="color:#777169;font-size:14px;font-weight:600">${job.company[0]}</span>`; }} />
          ) : (
            <span className="text-[14px] font-semibold text-gravel">{job.company[0]}</span>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-body-medium text-obsidian leading-tight truncate">{job.title}</h3>
          <p className="text-caption text-gravel mt-0.5 truncate">{job.company} · {job.location}</p>
        </div>
        <button onClick={(e) => { e.stopPropagation(); onBookmark(job.id, !job.is_bookmarked); }} className="p-1 rounded-lg hover:bg-powder transition-colors flex-shrink-0">
          <svg className={`w-4 h-4 ${job.is_bookmarked ? "text-obsidian fill-obsidian" : "text-chalk"}`} viewBox="0 0 24 24" fill={job.is_bookmarked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" />
          </svg>
        </button>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {job.work_mode && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.work_mode}</span>}
        {job.experience_level && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.experience_level}</span>}
        {job.employment_type && <span className="tag !py-0.5 !px-2 !text-[11px]">{job.employment_type.replace("-", " ")}</span>}
      </div>

      {/* Snippet */}
      <p className="text-caption text-gravel leading-[1.5] line-clamp-2 mb-4 flex-1">{job.description_snippet}</p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-chalk">
        {salary ? <span className="text-body-medium text-obsidian">{salary}</span> : <span className="text-caption text-fog">Salary unlisted</span>}
        <div className="flex items-center gap-2">
          {job.evaluation && <GradeBadge grade={job.evaluation.grade} score={job.evaluation.overall_score} size="sm" />}
          <span className="text-[10px] font-medium text-gravel px-2 py-0.5 rounded-pill border border-chalk">{job.source}</span>
        </div>
      </div>

      {/* HR Contact */}
      {(job.hr_name || job.hr_email) && (
        <div className="mt-2 pt-2 border-t border-chalk flex items-center gap-2" onClick={e => e.stopPropagation()}>
          <svg className="w-3 h-3 text-gravel flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2M12 3a4 4 0 100 8 4 4 0 000-8z"/></svg>
          <span className="text-[11px] text-gravel truncate">
            {job.hr_name && <span className="font-medium text-obsidian">{job.hr_name}</span>}
            {job.hr_email && (
              <a href={`mailto:${job.hr_email}`} className="ml-1 text-blue-600 hover:underline" onClick={e => e.stopPropagation()}>
                {job.hr_email}
              </a>
            )}
          </span>
        </div>
      )}
    </div>
  );
}
