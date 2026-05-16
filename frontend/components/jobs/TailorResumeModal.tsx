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
@page{size:letter;margin:0}
body{margin:0;padding:0;font-family:'Times New Roman','Georgia',serif}
.page{width:8.5in;min-height:11in;padding:0.45in 0.55in;font-size:10.5pt;line-height:1.28;color:#000;box-sizing:border-box}
h1{font-size:20pt;font-weight:700;text-align:center;margin:0 0 1px;letter-spacing:0.3px}
.title{text-align:center;font-size:10pt;color:#333;margin:0 0 4px;font-style:italic}
.contact{text-align:center;font-size:9.5pt;color:#333;margin:0 0 8px}
.contact a{color:#0066cc;text-decoration:none}
.sec{border-bottom:1.5px solid #000;padding-bottom:1px;margin:9px 0 5px}
.sec h2{font-size:11.5pt;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0}
.exp{margin-bottom:7px}
.exp-row{display:flex;justify-content:space-between;align-items:baseline}
.exp-row b{font-size:11pt}
.exp-row i{font-size:9.5pt;color:#444}
.exp p{font-size:10pt;font-style:italic;color:#222;margin:0 0 3px}
ul{margin:0;padding-left:15px;list-style-type:disc}
li{font-size:9.5pt;color:#111;margin-bottom:1.5px;line-height:1.3;text-align:justify}
li a{color:#0066cc;text-decoration:none;font-weight:500}
.proj{margin-bottom:5px}
.proj b{font-size:10.5pt}
.proj .sub{color:#444;font-size:9.5pt}
.proj .tech{color:#666;font-size:9pt}
.proj a{color:#0066cc;font-size:9pt;text-decoration:none;margin-left:4px}
.skills p{margin:1px 0;font-size:9.5pt;line-height:1.3}
.skills b{font-weight:700}
.edu-row{display:flex;justify-content:space-between;margin-bottom:3px}
.edu-row b{font-size:10.5pt}
.edu-row .detail{font-size:9.5pt;color:#222;margin:0}
.edu-row i{font-size:9pt;color:#444;white-space:nowrap}
@media print{*{-webkit-print-color-adjust:exact!important}}
</style></head><body><div class="page">
<h1>${name}</h1>
<p class="title">${profile.title || profile.headline || 'Software Engineer'}</p>
<p class="contact">${phone}${email ? ' | <a href="mailto:' + email + '">' + email + '</a>' : ''}${linkedin ? ' | <a href="' + linkedin + '">LinkedIn</a>' : ''}${github ? ' | <a href="' + github + '">GitHub</a>' : ''}${profile.portfolio ? ' | <a href="' + profile.portfolio + '">Portfolio</a>' : ''}</p>

${summary ? '<div class="sec"><h2>About</h2></div><p style="font-size:9.5pt;text-align:justify;margin:0">' + summary + '</p>' : ''}

<div class="sec"><h2>Work Experience</h2></div>
${experience.map((e: any) => `<div class="exp"><div class="exp-row"><b>${e.company}</b><i>${e.start_date || e.dates || ''} – ${e.end_date || 'Present'}</i></div><p>${e.title || e.role || ''}</p><ul>${(e.responsibilities || e.bullets || []).map((b: any) => '<li>' + (typeof b === 'string' ? b : b.text || '') + (typeof b === 'object' && b.link ? ' <a href="' + (b.link.url || '#') + '">' + (b.link.text || 'Link') + '</a>' : '') + '</li>').join('')}</ul></div>`).join('')}

<div class="sec"><h2>Projects & SaaS Products</h2></div>
${projects.map((p: any) => `<div class="proj"><b>${p.name}</b>${p.subtitle ? '<span class="sub"> – ' + p.subtitle + '</span>' : ''}<span class="tech"> | ${(p.technologies || []).join(', ') || p.tech || ''}</span>${p.link ? '<a href="' + p.link + '">↗</a>' : ''}<ul>${(p.bullets || p.outcomes || [p.description]).filter(Boolean).map((b: string) => '<li>' + b + '</li>').join('')}</ul></div>`).join('')}

<div class="sec"><h2>Technical Skills</h2></div>
<div class="skills">${typeof skills === 'object' && !Array.isArray(skills) ? Object.entries(skills).map(([cat, val]: [string, any]) => Array.isArray(val) && val.length ? '<p><b>' + cat.replace(/_/g, ' ') + ':</b> ' + val.join(', ') + '</p>' : typeof val === 'string' ? '<p><b>' + cat + ':</b> ' + val + '</p>' : '').join('') : '<p>' + (Array.isArray(skills) ? skills.join(', ') : '') + '</p>'}</div>

${education.length ? '<div class="sec"><h2>Education</h2></div>' + education.map((e: any) => '<div class="edu-row"><div><b>' + (e.institution || e.school || '') + '</b><p class="detail">' + (e.degree || '') + (e.major ? ' in ' + e.major : '') + (e.gpa ? ' | CGPA: ' + e.gpa : '') + (e.detail ? ' | ' + e.detail : '') + '</p></div><i>' + (e.graduation_year || e.dates || '') + '</i></div>').join('') : ''}

</div></body></html>`;
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
