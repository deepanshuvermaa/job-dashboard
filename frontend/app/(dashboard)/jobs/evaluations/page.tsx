"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

const GRADE_COLORS: Record<string, string> = {
  A: "#34d399", B: "#4da6ff", C: "#fbbf24", D: "#f87171", F: "#5c6b82",
};

const DIMENSIONS = [
  { key: "role_match", label: "Role Match" },
  { key: "skills_alignment", label: "Skills" },
  { key: "seniority_fit", label: "Seniority" },
  { key: "compensation", label: "Compensation" },
  { key: "interview_likelihood", label: "Interview Chance" },
  { key: "growth_potential", label: "Growth" },
  { key: "company_reputation", label: "Reputation" },
  { key: "location_fit", label: "Location" },
  { key: "tech_stack_match", label: "Tech Stack" },
  { key: "culture_signals", label: "Culture" },
];

export default function EvaluationsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [gradeFilter, setGradeFilter] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [stats, setStats] = useState<any>({});

  useEffect(() => {
    setLoading(true);
    api
      .getJobs({ per_page: 100, sort: "score", grade: gradeFilter || undefined })
      .then((data) => {
        setJobs(data.jobs.filter((j: any) => j.evaluation));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
    api.getJobStats().then(setStats).catch(console.error);
  }, [gradeFilter]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-8 py-6 max-w-wide mx-auto">
      <h1 className="text-heading text-obsidian font-display">Job Evaluations</h1>
      <p className="text-body text-gravel mt-1">10-dimension AI scoring for every discovered job</p>

      {/* Grade summary */}
      <div className="grid grid-cols-5 gap-4 mb-8 mt-8">
        {["A", "B", "C", "D", "F"].map((grade) => (
          <button
            key={grade}
            onClick={() => setGradeFilter(gradeFilter === grade ? "" : grade)}
            className={`card text-center cursor-pointer transition-all active:scale-95 ${
              gradeFilter === grade ? "ring-2 ring-obsidian" : ""
            }`}
          >
            <div
              className="w-12 h-12 rounded-sm flex items-center justify-center text-obsidian text-heading-sm font-semibold mx-auto mb-2"
              style={{ backgroundColor: GRADE_COLORS[grade] }}
            >
              {grade}
            </div>
            <p className="text-heading text-obsidian">{stats?.grades?.[grade] || 0}</p>
            <p className="text-caption text-gravel">
              {grade === "A" ? "Excellent" : grade === "B" ? "Good" : grade === "C" ? "Fair" : grade === "D" ? "Poor" : "Reject"}
            </p>
          </button>
        ))}
      </div>

      {/* Evaluations table */}
      {jobs.length === 0 ? (
        <div className="card text-center py-16">
          <p className="text-body-lg text-gravel">No evaluated jobs</p>
        </div>
      ) : (
        <div className="space-y-2">
          {jobs.map((job) => {
            const ev = job.evaluation;
            const isExpanded = expandedId === job.id;
            return (
              <div key={job.id} className="card !p-0 overflow-hidden">
                {/* Row */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : job.id)}
                  className="w-full flex items-center gap-4 p-4 text-left hover:bg-powder transition-colors"
                >
                  <div
                    className="w-8 h-8 rounded-xs flex items-center justify-center text-obsidian text-caption-strong flex-shrink-0"
                    style={{ backgroundColor: GRADE_COLORS[ev.grade] || "#5c6b82" }}
                  >
                    {ev.grade}
                  </div>
                  <span className="text-caption text-gravel w-10">{Math.round(ev.overall_score)}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-body-medium text-obsidian truncate">{job.title}</p>
                    <p className="text-caption text-gravel">{job.company}</p>
                  </div>
                  <span className={`text-caption ${ev.gate_pass ? "text-grade-a" : "text-grade-d"}`}>
                    {ev.gate_pass ? "Pass" : "Fail"}
                  </span>
                  <a href={job.job_url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="text-obsidian text-caption hover:underline">
                    View
                  </a>
                  <svg
                    className={`w-4 h-4 text-gravel transition-transform ${isExpanded ? "rotate-180" : ""}`}
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </button>

                {/* Expanded detail */}
                {isExpanded && (
                  <div className="px-4 pb-4 pt-0 border-t border-chalk">
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
                      {DIMENSIONS.map((dim) => (
                        <div key={dim.key}>
                          <p className="text-caption text-gravel mb-1">{dim.label}</p>
                          <div className="flex items-center gap-2">
                            <div className="flex-1 h-1.5 bg-powder rounded-full overflow-hidden">
                              <div
                                className="h-full bg-obsidian rounded-full"
                                style={{ width: `${ev[dim.key] || 0}%` }}
                              />
                            </div>
                            <span className="text-caption text-cinder w-6 text-right">
                              {Math.round(ev[dim.key] || 0)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                    {ev.reasoning && (
                      <p className="text-caption text-gravel italic mt-4">{ev.reasoning}</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
