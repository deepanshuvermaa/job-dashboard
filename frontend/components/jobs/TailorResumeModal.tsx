"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface Props { job: any; onClose: () => void; }

export default function TailorResumeModal({ job, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [coverLetter, setCoverLetter] = useState<string | null>(null);
  const [clLoading, setClLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await api.tailorResume(job.id);
      setResult(res);
    } catch (err: any) {
      alert(err.message || "Failed");
    } finally { setLoading(false); }
  };

  const handleCoverLetter = async () => {
    setClLoading(true);
    try {
      const res = await api.generateCoverLetter(job.id);
      setCoverLetter(res.cover_letter);
    } catch (err: any) {
      alert(err.message || "Failed");
    } finally { setClLoading(false); }
  };

  const handleDownload = () => {
    if (!result) return;
    const profile = result.original_profile || {};
    const name = profile.name || "Candidate";
    const email = profile.email || "";
    const phone = profile.phone || "";
    const linkedin = profile.linkedin || "";
    const github = profile.github || "";
    const summary = profile.summary || "";
    const experience = profile.experience || [];
    const projects = profile.projects || [];
    const skills = profile.skills || {};
    const education = profile.education || [];

    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${name} - Resume</title>
<style>
body{font-family:'Calibri','Segoe UI',sans-serif;max-width:700px;margin:24px auto;padding:0 28px;font-size:10.5pt;line-height:1.45;color:#1a1a1a}
h1{font-size:16pt;margin:0 0 2px;font-weight:700}
.contact{font-size:9pt;color:#333;margin:2px 0 10px}
.contact a{color:#0055cc;text-decoration:none}
h2{font-size:10.5pt;font-weight:700;border-bottom:1.5px solid #1a1a1a;padding-bottom:2px;margin:14px 0 6px;text-transform:uppercase;letter-spacing:0.3px}
.exp-header{display:flex;justify-content:space-between;margin:8px 0 2px}
.exp-header h3{font-size:10.5pt;font-weight:600;margin:0}
.exp-header span{font-size:9pt;color:#555}
ul{margin:2px 0 8px;padding-left:15px}
li{margin:1px 0;font-size:10pt}
.proj-title{font-weight:600;font-size:10pt;margin:6px 0 1px}
.proj-title a{color:#0055cc;font-weight:400;font-size:9pt;margin-left:4px}
.tech{font-size:9pt;color:#444;margin:1px 0 6px}
.skills-section p{margin:2px 0;font-size:10pt}
.skills-section strong{font-size:9.5pt}
.edu{margin:4px 0}
.ats-note{margin-top:16px;padding:8px 12px;background:#f0f7ff;border:1px solid #cce;border-radius:4px;font-size:9pt;color:#333}
.ats-note strong{color:#0055cc}
mark{background:#d4edda;padding:0 2px;border-radius:2px}
@media print{body{margin:0;padding:16px}.ats-note{display:none}}
</style></head><body>
<h1>${name}</h1>
<p class="contact">${phone}${email ? ' | <a href="mailto:' + email + '">' + email + '</a>' : ''}${linkedin ? ' | <a href="' + linkedin + '">LinkedIn</a>' : ''}${github ? ' | <a href="' + github + '">GitHub</a>' : ''}${profile.portfolio ? ' | <a href="' + profile.portfolio + '">Portfolio</a>' : ''}</p>

<h2>About</h2>
<p>${summary}</p>

<h2>Work Experience</h2>
${experience.map((e: any) => `
<div class="exp-header"><h3>${e.title || e.role} — ${e.company}</h3><span>${e.start_date || ''} – ${e.end_date || 'Present'}</span></div>
<ul>${(e.responsibilities || e.bullets || []).map((b: string) => '<li>' + b + '</li>').join('')}${(e.achievements || []).map((a: string) => '<li><strong>' + a + '</strong></li>').join('')}</ul>
`).join('')}

<h2>Projects</h2>
${projects.map((p: any) => `
<p class="proj-title">${p.name}${p.link ? ' <a href="' + p.link + '">↗ Live</a>' : ''}</p>
<ul>${(p.outcomes || p.responsibilities || [p.description]).filter(Boolean).map((d: string) => '<li>' + d + '</li>').join('')}</ul>
<p class="tech">${(p.technologies || []).join(' · ')}</p>
`).join('')}

<h2>Technical Skills</h2>
<div class="skills-section">
${typeof skills === 'object' && !Array.isArray(skills) ? Object.entries(skills).map(([cat, vals]: [string, any]) => Array.isArray(vals) && vals.length ? '<p><strong>' + cat.replace(/_/g, ' ') + ':</strong> ' + vals.join(', ') + '</p>' : '').join('') : '<p>' + (Array.isArray(skills) ? skills.join(', ') : String(skills)) + '</p>'}
</div>

${education.length ? '<h2>Education</h2>' + education.map((e: any) => '<p class="edu"><strong>' + (e.degree || '') + (e.major ? ' in ' + e.major : '') + '</strong> — ' + (e.institution || '') + (e.graduation_year ? ' (' + e.graduation_year + ')' : '') + (e.gpa ? ' | CGPA: ' + e.gpa : '') + '</p>').join('') : ''}

<div class="ats-note">
<strong>ATS Match: ${result.ats_score}%</strong> for ${job.title} at ${job.company}<br>
<strong>Matched:</strong> ${(result.matched_keywords || []).join(', ')}<br>
<strong>Consider adding:</strong> ${(result.missing_keywords || []).join(', ')}
</div>

${coverLetter ? '<h2 style="margin-top:24px">Cover Letter</h2><p>' + coverLetter.replace(/\n/g, '<br>') + '</p>' : ''}
</body></html>`;

    const w = window.open("", "_blank");
    if (w) { w.document.write(html); w.document.close(); setTimeout(() => w.print(), 600); }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center">
      <div className="absolute inset-0 bg-obsidian/40" onClick={onClose} />
      <div className="relative bg-eggshell rounded-card shadow-card w-full max-w-[700px] max-h-[85vh] overflow-y-auto mx-4">
        <div className="sticky top-0 bg-eggshell border-b border-chalk px-6 py-4 flex items-center justify-between z-10">
          <div>
            <h2 className="text-subheading text-obsidian font-display">ATS Resume Optimizer</h2>
            <p className="text-caption text-gravel">{job.title} at {job.company}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-powder">
            <svg className="w-4 h-4 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">
          {!result ? (
            <div className="text-center py-8">
              <p className="text-body text-gravel mb-4">Analyze how your resume matches this job's requirements. Your content stays untouched — we only show keyword gaps and suggestions.</p>
              <button onClick={handleAnalyze} disabled={loading} className="btn-primary disabled:opacity-50">
                {loading ? "Analyzing..." : "Analyze ATS Match"}
              </button>
            </div>
          ) : (
            <>
              {/* ATS Score */}
              <div className="flex items-center gap-4 p-4 bg-powder rounded-card">
                <div className="w-16 h-16 rounded-full border-4 border-obsidian flex items-center justify-center flex-shrink-0">
                  <span className="text-heading text-obsidian font-display">{result.ats_score}%</span>
                </div>
                <div>
                  <p className="text-body-medium text-obsidian">ATS Match Score</p>
                  <p className="text-caption text-gravel">Matched: {result.matched_keywords?.length || 0} | Missing: {result.missing_keywords?.length || 0}</p>
                </div>
              </div>

              {/* Keywords */}
              <div>
                <h3 className="text-body-medium text-obsidian mb-2">Keywords Found in Your Resume</h3>
                <div className="flex flex-wrap gap-1.5">
                  {(result.matched_keywords || []).map((k: string) => (
                    <span key={k} className="px-2 py-0.5 rounded-pill text-[11px] bg-green-50 text-green-700 border border-green-200">{k}</span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-body-medium text-obsidian mb-2">Missing Keywords (consider adding)</h3>
                <div className="flex flex-wrap gap-1.5">
                  {(result.missing_keywords || []).map((k: string) => (
                    <span key={k} className="px-2 py-0.5 rounded-pill text-[11px] bg-red-50 text-red-500 border border-red-200">{k}</span>
                  ))}
                </div>
              </div>

              {/* Suggestions */}
              {result.suggestions && (
                <div>
                  <h3 className="text-body-medium text-obsidian mb-2">Suggestions</h3>
                  <ul className="space-y-1.5">
                    {result.suggestions.map((s: string, i: number) => (
                      <li key={i} className="text-[12px] text-cinder flex items-start gap-2">
                        <span className="text-green-600 mt-0.5">→</span> {s}
                      </li>
                    ))}
                  </ul>
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

              {/* Download */}
              <div className="flex gap-3 pt-2">
                <button onClick={handleDownload} className="btn-primary flex-1">Download Resume as PDF</button>
                <a href={job.job_url} target="_blank" rel="noopener" className="btn-secondary flex-1 text-center">Apply Now</a>
              </div>
              <p className="text-[10px] text-fog text-center">Downloads your ORIGINAL resume with ATS notes. Use browser's "Save as PDF" in print dialog.</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
