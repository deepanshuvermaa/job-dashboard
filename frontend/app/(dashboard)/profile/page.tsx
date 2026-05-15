"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    api.getProfile()
      .then((data) => { if (data.success) setProfile(data.profile); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const data = await api.uploadResume(file);
      if (data.success) {
        setProfile(data.profile);
      } else {
        alert(data.message || "Upload failed");
      }
    } catch (err: any) {
      alert(err.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // No profile yet -- upload state
  if (!profile) {
    return (
      <div className="px-8 py-6 max-w-content mx-auto">
        <h1 className="text-heading text-obsidian font-display">AI Profile Builder</h1>
        <p className="text-body text-gravel mt-1">Upload your resume and let AI build your profile</p>

        <div className="card text-center py-16 mt-8">
          <div className="w-20 h-20 rounded-full bg-powder flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="12" y1="18" x2="12" y2="12" />
              <line x1="9" y1="15" x2="15" y2="15" />
            </svg>
          </div>
          <h2 className="text-heading-sm text-obsidian mb-2">Upload Your Resume</h2>
          <p className="text-body text-gravel mb-6">PDF format recommended -- AI will extract all your information</p>
          <label className="btn-primary cursor-pointer inline-block">
            {uploading ? "Uploading & Parsing..." : "Upload Resume (PDF)"}
            <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
          </label>
          <p className="text-caption text-gravel mt-3">Supports PDF files</p>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-8">
          {[
            { title: "Smart Extraction", desc: "AI reads your resume and extracts skills, experience, education" },
            { title: "Review & Edit", desc: "Review extracted data and make corrections before saving" },
            { title: "Auto-Fill Applications", desc: "Profile data powers auto-apply and resume tailoring" },
          ].map((f) => (
            <div key={f.title} className="card text-center">
              <h3 className="text-body-medium text-obsidian mb-1">{f.title}</h3>
              <p className="text-caption text-gravel">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Profile loaded -- display
  return (
    <div className="px-8 py-6 max-w-content mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-heading text-obsidian font-display">{profile.name || "Your Profile"}</h1>
          <p className="text-body text-gravel mt-1">{profile.primary_industry || profile.headline || "Software Professional"}</p>
        </div>
        <button onClick={() => setEditing(!editing)} className="btn-secondary">
          {editing ? "Done Editing" : "Edit Profile"}
        </button>
      </div>

      {/* Summary */}
      {profile.summary && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-2">Summary</h2>
          <p className="text-body text-cinder">{profile.summary}</p>
        </div>
      )}

      {/* Contact */}
      <div className="card mb-6">
        <h2 className="text-body-medium text-obsidian mb-3">Personal Information</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Email", value: profile.email },
            { label: "Phone", value: profile.phone },
            { label: "Location", value: profile.location },
            { label: "Experience", value: profile.total_experience_years ? `${profile.total_experience_years} years` : "" },
          ].map((f) => f.value && (
            <div key={f.label}>
              <p className="text-caption text-gravel">{f.label}</p>
              <p className="text-caption text-obsidian">{f.value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Skills */}
      {profile.skills && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Skills</h2>
          <div className="space-y-3">
            {Object.entries(profile.skills).map(([category, skills]: [string, any]) => (
              Array.isArray(skills) && skills.length > 0 && (
                <div key={category}>
                  <p className="text-caption-strong text-gravel capitalize mb-1">{category.replace(/_/g, " ")}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.map((s: string) => (
                      <span key={s} className="px-2 py-0.5 bg-powder rounded-full text-caption text-cinder">{s}</span>
                    ))}
                  </div>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Experience */}
      {profile.experience?.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Work Experience</h2>
          <div className="space-y-4">
            {profile.experience.map((exp: any, i: number) => (
              <div key={i} className="border-l-2 border-obsidian/20 pl-4">
                <h3 className="text-body-medium text-obsidian">{exp.title || exp.role}</h3>
                <p className="text-caption text-gravel">{exp.company} · {exp.duration || exp.duration_display || `${exp.start_date || ""} - ${exp.end_date || "Present"}`}</p>
                {exp.responsibilities && (
                  <ul className="mt-2 space-y-1">
                    {(Array.isArray(exp.responsibilities) ? exp.responsibilities : [exp.responsibilities]).map((r: string, j: number) => (
                      <li key={j} className="text-caption text-cinder">- {r}</li>
                    ))}
                  </ul>
                )}
                {exp.achievements && (
                  <ul className="mt-1 space-y-1">
                    {(Array.isArray(exp.achievements) ? exp.achievements : []).map((a: string, j: number) => (
                      <li key={j} className="text-caption text-green-700">★ {a}</li>
                    ))}
                  </ul>
                )}
                {exp.technologies && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(Array.isArray(exp.technologies) ? exp.technologies : []).map((t: string) => (
                      <span key={t} className="px-1.5 py-0.5 bg-obsidian/5 text-obsidian rounded-xs text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {profile.projects?.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Projects</h2>
          <div className="space-y-4">
            {profile.projects.map((proj: any, i: number) => (
              <div key={i} className="border-l-2 border-green-300 pl-4">
                <div className="flex items-center gap-2">
                  <h3 className="text-body-medium text-obsidian">{proj.name}</h3>
                  {proj.link && <a href={proj.link} target="_blank" rel="noopener" className="text-[11px] text-blue-600 hover:underline">↗ Link</a>}
                </div>
                <p className="text-caption text-cinder mt-1">{proj.description}</p>
                {proj.outcomes && (
                  <ul className="mt-1 space-y-0.5">
                    {(Array.isArray(proj.outcomes) ? proj.outcomes : []).map((o: string, j: number) => (
                      <li key={j} className="text-caption text-green-700">→ {o}</li>
                    ))}
                  </ul>
                )}
                {proj.technologies && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(Array.isArray(proj.technologies) ? proj.technologies : []).map((t: string) => (
                      <span key={t} className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded-xs text-[10px]">{t}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Certifications */}
      {profile.certifications?.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Certifications</h2>
          {profile.certifications.map((cert: any, i: number) => (
            <div key={i} className="mb-2">
              <p className="text-caption text-obsidian">{typeof cert === 'string' ? cert : `${cert.name}${cert.issuer ? ` · ${cert.issuer}` : ''}${cert.date ? ` (${cert.date})` : ''}`}</p>
            </div>
          ))}
        </div>
      )}

      {/* Achievements */}
      {profile.achievements?.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Achievements</h2>
          <ul className="space-y-1">
            {profile.achievements.map((a: string, i: number) => (
              <li key={i} className="text-caption text-cinder">★ {a}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Education */}
      {profile.education?.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-body-medium text-obsidian mb-3">Education</h2>
          {profile.education.map((edu: any, i: number) => (
            <div key={i} className="mb-3">
              <p className="text-body-medium text-obsidian">{edu.degree} {edu.major && `in ${edu.major}`}</p>
              <p className="text-caption text-gravel">{edu.institution} {edu.graduation_year && `· ${edu.graduation_year}`}</p>
            </div>
          ))}
        </div>
      )}

      {/* Re-upload */}
      <label className="btn-secondary cursor-pointer inline-block mt-4">
        Re-upload Resume
        <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" disabled={uploading} />
      </label>
    </div>
  );
}
