"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface Props { job: any; onClose: () => void; }

export default function TailorResumeModal({ job, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const [clLoading, setClLoading] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editedSummary, setEditedSummary] = useState("");

  const handleTailor = async () => {
    setLoading(true);
    try {
      const res = await api.tailorResume(job.id);
      setResult(res);
      setEditedSummary(res.summary || "");
    } catch (err: any) {
      alert(err.message || "Failed to tailor resume");
    } finally { setLoading(false); }
  };

  const handleCoverLetter = async () => {
    setClLoading(true);
    try {
      const res = await api.generateCoverLetter(job.id);
      setCoverLetter(res.cover_letter);
    } catch (err: any) {
      alert(err.message || "Failed to generate cover letter");
    } finally { setClLoading(false); }
  };

  const handleDownload = () => {
    if (!result) return;
    // Generate text file for download
    let content = `TAILORED RESUME\n${"=".repeat(50)}\n\n`;
    content += `Target: ${result.job_title} at ${result.company}\n`;
    content += `ATS Match: ${result.ats_score}%\n\n`;
    content += `SUMMARY\n${"-".repeat(30)}\n${editedSummary || result.summary}\n\n`;
    if (result.experience) {
      content += `EXPERIENCE\n${"-".repeat(30)}\n`;
      for (const exp of result.experience) {
        content += `\n${exp.title} | ${exp.company}\n`;
        for (const b of (exp.bullets || [])) content += `• ${b}\n`;
      }
    }
    if (result.projects) {
      content += `\nPROJECTS\n${"-".repeat(30)}\n`;
      for (const proj of result.projects) {
        content += `\n${proj.name}${proj.link ? ` (${proj.link})` : ""}\n`;
        content += `${proj.description}\n`;
        if (proj.technologies) content += `Tech: ${proj.technologies.join(", ")}\n`;
      }
    }
    content += `\nSKILLS HIGHLIGHTED\n${"-".repeat(30)}\n${(result.skills_highlighted || []).join(", ")}\n`;
    if (coverLetter) {
      content += `\n\nCOVER LETTER\n${"=".repeat(50)}\n${coverLetter}\n`;
    }
    const blob = new Blob([content], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `Resume_${result.company}_${result.job_title?.replace(/\s+/g, "_")}.txt`;
    a.click();
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center">
      <div className="absolute inset-0 bg-obsidian/40" onClick={onClose} />
      <div className="relative bg-eggshell rounded-card shadow-card w-full max-w-[700px] max-h-[85vh] overflow-y-auto mx-4">
        {/* Header */}
        <div className="sticky top-0 bg-eggshell border-b border-chalk px-6 py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="text-subheading text-obsidian font-display">Tailor Resume</h2>
            <p className="text-caption text-gravel">{job.title} at {job.company}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-powder">
            <svg className="w-4 h-4 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">
          {!result ? (
            /* Initial state - generate button */
            <div className="text-center py-8">
              <svg className="w-16 h-16 text-chalk mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
              <p className="text-body text-gravel mb-4">AI will tailor your resume to match this job's requirements while keeping your format and word count intact.</p>
              <button onClick={handleTailor} disabled={loading} className="btn-primary disabled:opacity-50">
                {loading ? "Tailoring..." : "Generate Tailored Resume"}
              </button>
            </div>
          ) : (
            /* Results */
            <>
              {/* ATS Score */}
              <div className="flex items-center gap-4 p-4 bg-powder rounded-card">
                <div className="w-16 h-16 rounded-full border-4 border-obsidian flex items-center justify-center flex-shrink-0">
                  <span className="text-heading text-obsidian font-display">{result.ats_score}%</span>
                </div>
                <div>
                  <p className="text-body-medium text-obsidian">ATS Match Score</p>
                  <p className="text-caption text-gravel">Keywords matched: {result.keywords_added?.length || 0} | Missing: {result.keywords_missing?.length || 0}</p>
                </div>
              </div>

              {/* Keywords */}
              <div className="flex flex-wrap gap-1.5">
                {(result.keywords_added || []).map((k: string) => (
                  <span key={k} className="px-2 py-0.5 rounded-pill text-[11px] bg-green-50 text-green-700 border border-green-200">{k}</span>
                ))}
                {(result.keywords_missing || []).map((k: string) => (
                  <span key={k} className="px-2 py-0.5 rounded-pill text-[11px] bg-red-50 text-red-500 border border-red-200">{k}</span>
                ))}
              </div>

              {/* Summary */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-body-medium text-obsidian">Summary</h3>
                  <button onClick={() => setEditing(!editing)} className="text-[11px] text-blue-600 hover:underline">{editing ? "Done" : "Edit"}</button>
                </div>
                {editing ? (
                  <textarea value={editedSummary} onChange={e => setEditedSummary(e.target.value)} className="w-full h-24 px-3 py-2 border border-chalk rounded-lg text-[13px] bg-white focus:outline-none focus:border-obsidian resize-none" />
                ) : (
                  <p className="text-[13px] text-cinder leading-relaxed">{editedSummary || result.summary}</p>
                )}
              </div>

              {/* Experience */}
              {result.experience && (
                <div>
                  <h3 className="text-body-medium text-obsidian mb-2">Tailored Experience</h3>
                  <div className="space-y-3">
                    {result.experience.map((exp: any, i: number) => (
                      <div key={i} className="pl-3 border-l-2 border-chalk">
                        <p className="text-[13px] font-medium text-obsidian">{exp.title} · {exp.company}</p>
                        <ul className="mt-1 space-y-0.5">
                          {(exp.bullets || []).map((b: string, j: number) => (
                            <li key={j} className="text-[12px] text-gravel leading-relaxed">• {b}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {result.projects && result.projects.length > 0 && (
                <div>
                  <h3 className="text-body-medium text-obsidian mb-2">Tailored Projects</h3>
                  <div className="space-y-3">
                    {result.projects.map((proj: any, i: number) => (
                      <div key={i} className="pl-3 border-l-2 border-green-200">
                        <p className="text-[13px] font-medium text-obsidian">{proj.name} {proj.link && <a href={proj.link} target="_blank" className="text-blue-600 text-[11px] ml-1">↗</a>}</p>
                        <p className="text-[12px] text-gravel mt-0.5">{proj.description}</p>
                        {proj.technologies && <p className="text-[11px] text-fog mt-1">{proj.technologies.join(" · ")}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {result.skills_highlighted && (
                <div>
                  <h3 className="text-body-medium text-obsidian mb-2">Highlighted Skills</h3>
                  <p className="text-[13px] text-gravel">{result.skills_highlighted.join(" · ")}</p>
                </div>
              )}

              {/* Cover Letter */}
              <div className="border-t border-chalk pt-4">
                {coverLetter ? (
                  <div>
                    <h3 className="text-body-medium text-obsidian mb-2">Cover Letter</h3>
                    <p className="text-[12px] text-cinder leading-relaxed whitespace-pre-line">{coverLetter}</p>
                  </div>
                ) : (
                  <button onClick={handleCoverLetter} disabled={clLoading} className="btn-secondary w-full disabled:opacity-50">
                    {clLoading ? "Generating..." : "Generate Cover Letter"}
                  </button>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <button onClick={handleDownload} className="btn-primary flex-1">Download</button>
                <a href={job.job_url} target="_blank" rel="noopener" className="btn-secondary flex-1 text-center">Apply Now</a>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
