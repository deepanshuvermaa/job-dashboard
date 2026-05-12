"use client";
import { useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";

/* ─── Resume Data Structure ─── */
interface BulletItem { text: string; link?: { text: string; url: string } | null; }
interface ExpItem { company: string; dates: string; title: string; bullets: BulletItem[]; }
interface ProjItem { name: string; subtitle: string; tech: string; bullets: string[]; }
interface EduItem { school: string; dates: string; degree: string; detail: string; }
interface ContactLink { text: string; url: string; }
interface ResumeData {
  name: string;
  title: string;
  contact: { phone: string; email: ContactLink; linkedin: ContactLink; github: ContactLink; portfolio: ContactLink; };
  experience: ExpItem[];
  projects: ProjItem[];
  skills: Record<string, string>;
  education: EduItem[];
}

const DEFAULT_RESUME: ResumeData = {
  name: "Deepanshu Verma",
  title: "Software Engineer \u00b7 Cloud & Backend Engineer",
  contact: {
    phone: "8957678849",
    email: { text: "Email", url: "mailto:deepanshuverma966@gmail.com" },
    linkedin: { text: "LinkedIn", url: "https://linkedin.com/in/deepanshuverma" },
    github: { text: "GitHub", url: "https://github.com/deepanshuverma966" },
    portfolio: { text: "Portfolio", url: "https://deepanshu.dev" },
  },
  experience: [
    {
      company: "Pear Media",
      dates: "Mar 2025 \u2013 Present",
      title: "Software Engineer (Generative AI & Backend Systems)",
      bullets: [
        { text: "Built an end-to-end Ad Library platform that scrapes marketing creatives from multiple platforms, processes them into structured datasets, and enables users to search, filter, and reuse high-performing ads. Implemented using Python, Selenium, BeautifulSoup and deployed on GCP Cloud Run, with AI-driven tagging and insights to improve campaign decision-making speed.", link: { text: "Live Link", url: "#" } },
        { text: "Built a MERN-based SaaS platform for campaign automation that allows users to launch and manage marketing campaigns with minimal manual effort. Reduced daily manual work from 1.5 hours to under 6 minutes and improved business profit by 60%.", link: { text: "Live Link", url: "#" } },
        { text: "Created a cloud-based asset management system to store, organize, and retrieve creatives and media being edited and generated into structured data. Designed for fast access and reliability using AWS storage and backend services.", link: { text: "Live Link", url: "#" } },
        { text: "Built a one-click deployment system that allows internal teams to deploy and scale applications without manual setup. Automated build, deployment, and scaling workflows using CI/CD pipelines.", link: { text: "Live Link", url: "#" } },
        { text: "Developed an AI-driven automated engagement system that interacts with users (comments/messages) using NLP and prompt-based logic, generating approximately $600/day in revenue.", link: { text: "Live Link", url: "#" } },
      ],
    },
    {
      company: "RS Softgen Infotech",
      dates: "May 2024 \u2013 Feb 2025",
      title: "Software Developer Intern",
      bullets: [
        { text: "Worked on a business billing and invoicing system used by retail clients to manage transactions, invoices, and reports. Developed backend modules in an Agile team, improving deployment efficiency by 30%.", link: null },
        { text: "Collaborated with product and business teams to analyze user workflows and improve system usability, making the software adaptable across multiple business use cases.", link: null },
      ],
    },
  ],
  projects: [
    {
      name: "Go2Billing",
      subtitle: "SaaS Billing & Parking Management Platform",
      tech: "React, Node.js, Distributed Systems, RBAC",
      bullets: [
        "Built a production-grade SaaS platform with secure authentication, RBAC, and scalable backend services supporting concurrent users and real-time data synchronization.",
        "Designed system architecture focusing on scalability, fault tolerance, and performance optimization.",
      ],
    },
    {
      name: "Peripheral Services",
      subtitle: "E-Commerce Platform",
      tech: "React, APIs, Payments",
      bullets: [
        "Developed a full-stack e-commerce system with API-driven architecture, payment integration, and optimized backend workflows for reliability and scalability.",
      ],
    },
    {
      name: "Website Builder for SaaS Customers",
      subtitle: "",
      tech: "System Design, Templates",
      bullets: [
        "Designed a modular system for dynamic website generation with reusable components and efficient deployment workflows.",
      ],
    },
  ],
  skills: {
    "Languages": "Python, JavaScript, C++, SQL",
    "Backend & Frameworks": "Node.js, Express, REST APIs, Microservices Architecture",
    "Frontend": "React, React Native",
    "Cloud & DevOps": "AWS, GCP, Azure (basic), Docker, CI/CD",
    "Databases": "MongoDB, SQL",
    "Concepts": "Data Structures & Algorithms, Operating Systems, Computer Networks, Distributed Systems, System Design, Scalability, Load Balancing, Caching, Fault Tolerance",
    "AI/ML": "LLM Integration, RAG, NLP Pipelines",
  },
  education: [
    { school: "Chandigarh University", dates: "Aug 2020 \u2013 May 2024", degree: "B.E. Computer Science", detail: "CGPA: 7.7" },
    { school: "Lucknow Public School", dates: "Aug 2017 \u2013 May 2019", degree: "10th and 12th", detail: "87.5 \u2013 70.6" },
  ],
};

/* ═══════════════════════════════════════════
   A4 RESUME PREVIEW — pixel-matched to reference PDF
   ═══════════════════════════════════════════ */

function ResumePreview({ data, scale, hidden = new Set() }: { data: ResumeData; scale: number; hidden?: Set<string> }) {
  const S = (pt: number) => `${pt}pt`;

  return (
    <div style={{
      width: "816px",     /* 8.5in at 96dpi */
      minHeight: "1056px", /* 11in at 96dpi */
      padding: "43px 53px", /* ~0.45in and ~0.55in */
      fontFamily: "'Times New Roman', 'Georgia', serif",
      fontSize: S(10.5),
      lineHeight: "1.28",
      color: "#000",
      background: "#fff",
      transform: `scale(${scale})`,
      transformOrigin: "top left",
      boxSizing: "border-box",
    }}>
      {/* ── Name ── */}
      <h1 style={{
        fontSize: S(20), fontWeight: 700, textAlign: "center",
        margin: "0 0 1px", letterSpacing: "0.3px",
      }}>{data.name}</h1>

      {/* ── Title ── */}
      <p style={{
        textAlign: "center", fontSize: S(10), color: "#333",
        margin: "0 0 4px", fontStyle: "italic",
      }}>{data.title}</p>

      {/* ── Contact row ── */}
      <p style={{
        textAlign: "center", fontSize: S(9.5), color: "#333",
        margin: "0 0 8px",
      }}>
        {data.contact.phone}
        {" | "}<a href={data.contact.email.url} style={linkStyle}>{data.contact.email.text}</a>
        {" | "}<a href={data.contact.linkedin.url} style={linkStyle}>{data.contact.linkedin.text}</a>
        {" | "}<a href={data.contact.github.url} style={linkStyle}>{data.contact.github.text}</a>
        {data.contact.portfolio.url && <>{" | "}<a href={data.contact.portfolio.url} style={linkStyle}>{data.contact.portfolio.text}</a></>}
      </p>

      {/* ── Work Experience ── */}
      {!hidden.has("experience") && <>
      <SH title="Work Experience" />
      {data.experience.map((exp, i) => (
        <div key={i} style={{ marginBottom: "7px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <span style={{ fontWeight: 700, fontSize: S(11) }}>{exp.company}</span>
            <span style={{ fontSize: S(9.5), color: "#444", fontStyle: "italic" }}>{exp.dates}</span>
          </div>
          <p style={{ fontSize: S(10), fontStyle: "italic", color: "#222", margin: "0 0 3px" }}>{exp.title}</p>
          <ul style={{ margin: "0", paddingLeft: "15px", listStyleType: "disc" }}>
            {exp.bullets.map((b, j) => (
              <li key={j} style={{ fontSize: S(9.5), color: "#111", marginBottom: "1.5px", lineHeight: "1.3", textAlign: "justify" }}>
                {b.text}
                {b.link && b.link.text && <>{" "}<a href={b.link.url} style={{ ...linkStyle, fontWeight: 500 }}>{b.link.text}</a></>}
              </li>
            ))}
          </ul>
        </div>
      ))}

      </>}

      {/* ── Projects ── */}
      {!hidden.has("projects") && <>
      <SHWithLink title="Projects & SaaS Products" linkText="More Projects" linkUrl="#" />
      {data.projects.map((p, i) => (
        <div key={i} style={{ marginBottom: "5px" }}>
          <span style={{ fontWeight: 700, fontSize: S(10.5) }}>{p.name}</span>
          {p.subtitle && <span style={{ color: "#444", fontSize: S(9.5) }}> \u2013 {p.subtitle}</span>}
          <span style={{ color: "#666", fontSize: S(9) }}> | {p.tech}</span>
          <ul style={{ margin: "1px 0 0", paddingLeft: "15px", listStyleType: "disc" }}>
            {p.bullets.map((b, j) => (
              <li key={j} style={{ fontSize: S(9.5), color: "#111", lineHeight: "1.3", marginBottom: "1px" }}>{b}</li>
            ))}
          </ul>
        </div>
      ))}
      </>}

      {/* ── Technical Skills ── */}
      {!hidden.has("skills") && <>
      <SH title="Technical Skills" />
      <div style={{ fontSize: S(9.5), color: "#111" }}>
        {Object.entries(data.skills).map(([cat, val]) => (
          <p key={cat} style={{ margin: "1px 0", lineHeight: "1.3" }}>
            <span style={{ fontWeight: 700 }}>{cat}:</span> {val}
          </p>
        ))}
      </div>
      </>}

      {/* ── Education ── */}
      {!hidden.has("education") && <>
      <SH title="Education" />
      {data.education.map((edu, i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between", marginBottom: "3px" }}>
          <div>
            <span style={{ fontWeight: 700, fontSize: S(10.5) }}>{edu.school}</span>
            <p style={{ fontSize: S(9.5), color: "#222", margin: "0" }}>
              {edu.degree}
              <span style={{ color: "#555" }}> | {edu.detail}</span>
            </p>
          </div>
          <span style={{ fontSize: S(9), color: "#444", fontStyle: "italic", whiteSpace: "nowrap", alignSelf: "flex-start", marginTop: "1px" }}>{edu.dates}</span>
        </div>
      ))}
      </>}
    </div>
  );
}

const linkStyle: React.CSSProperties = { color: "#0066cc", textDecoration: "none" };

function SH({ title }: { title: string }) {
  return (
    <div style={{ borderBottom: "1.5px solid #000", paddingBottom: "1px", marginBottom: "5px", marginTop: "9px" }}>
      <h2 style={{ fontSize: "11.5pt", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px", margin: 0 }}>{title}</h2>
    </div>
  );
}

function SHWithLink({ title, linkText, linkUrl }: { title: string; linkText: string; linkUrl: string }) {
  return (
    <div style={{ borderBottom: "1.5px solid #000", paddingBottom: "1px", marginBottom: "5px", marginTop: "9px", display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
      <h2 style={{ fontSize: "11.5pt", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.5px", margin: 0 }}>{title}</h2>
      <a href={linkUrl} style={{ fontSize: "9pt", color: "#0066cc", textDecoration: "none" }}>{linkText}</a>
    </div>
  );
}

/* ═══════════════════════════════════════════
   PRINT FUNCTION — full scale A4 output
   ═══════════════════════════════════════════ */

function buildPrintHTML(data: ResumeData, hidden: Set<string> = new Set()): string {
  const c = data.contact;
  const lnk = (l: ContactLink) => `<a href="${l.url}" style="color:#0066cc;text-decoration:none">${l.text}</a>`;

  const secHead = (t: string) => `<div style="border-bottom:1.5px solid #000;padding-bottom:1px;margin-bottom:5px;margin-top:9px"><h2 style="font-size:11.5pt;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin:0">${t}</h2></div>`;

  const expHTML = data.experience.map(exp => `
    <div style="margin-bottom:7px">
      <div style="display:flex;justify-content:space-between;align-items:baseline">
        <span style="font-weight:700;font-size:11pt">${exp.company}</span>
        <span style="font-size:9.5pt;color:#444;font-style:italic">${exp.dates}</span>
      </div>
      <p style="font-size:10pt;font-style:italic;color:#222;margin:0 0 3px">${exp.title}</p>
      <ul style="margin:0;padding-left:15px;list-style-type:disc">
        ${exp.bullets.map(b => `<li style="font-size:9.5pt;color:#111;margin-bottom:1.5px;line-height:1.3;text-align:justify">${b.text}${b.link?.text ? ` <a href="${b.link.url}" style="color:#0066cc;text-decoration:none;font-weight:500">${b.link.text}</a>` : ''}</li>`).join('')}
      </ul>
    </div>`).join('');

  const projHTML = data.projects.map(p => `
    <div style="margin-bottom:5px">
      <span style="font-weight:700;font-size:10.5pt">${p.name}</span>
      ${p.subtitle ? `<span style="color:#444;font-size:9.5pt"> \u2013 ${p.subtitle}</span>` : ''}
      <span style="color:#666;font-size:9pt"> | ${p.tech}</span>
      <ul style="margin:1px 0 0;padding-left:15px;list-style-type:disc">
        ${p.bullets.map(b => `<li style="font-size:9.5pt;color:#111;line-height:1.3;margin-bottom:1px">${b}</li>`).join('')}
      </ul>
    </div>`).join('');

  const skillsHTML = Object.entries(data.skills).map(([cat, val]) =>
    `<p style="margin:1px 0;font-size:9.5pt;color:#111;line-height:1.3"><span style="font-weight:700">${cat}:</span> ${val}</p>`
  ).join('');

  const eduHTML = data.education.map(edu => `
    <div style="display:flex;justify-content:space-between;margin-bottom:3px">
      <div>
        <span style="font-weight:700;font-size:10.5pt">${edu.school}</span>
        <p style="font-size:9.5pt;color:#222;margin:0">${edu.degree}<span style="color:#555"> | ${edu.detail}</span></p>
      </div>
      <span style="font-size:9pt;color:#444;font-style:italic;white-space:nowrap">${edu.dates}</span>
    </div>`).join('');

  return `<html><head><title>${data.name} Resume</title>
    <style>
      @page { size: letter; margin: 0; }
      body { margin: 0; padding: 0; }
      * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    </style>
  </head><body>
    <div style="width:8.5in;min-height:11in;padding:0.45in 0.55in;font-family:'Times New Roman','Georgia',serif;font-size:10.5pt;line-height:1.28;color:#000;background:#fff;box-sizing:border-box">
      <h1 style="font-size:20pt;font-weight:700;text-align:center;margin:0 0 1px;letter-spacing:0.3px">${data.name}</h1>
      <p style="text-align:center;font-size:10pt;color:#333;margin:0 0 4px;font-style:italic">${data.title}</p>
      <p style="text-align:center;font-size:9.5pt;color:#333;margin:0 0 8px">
        ${c.phone} | ${lnk(c.email)} | ${lnk(c.linkedin)} | ${lnk(c.github)}${c.portfolio.url ? ` | ${lnk(c.portfolio)}` : ''}
      </p>
      ${!hidden.has("experience") ? `${secHead('Work Experience')}${expHTML}` : ''}
      ${!hidden.has("projects") ? `${secHead('Projects & SaaS Products')}${projHTML}` : ''}
      ${!hidden.has("skills") ? `${secHead('Technical Skills')}${skillsHTML}` : ''}
      ${!hidden.has("education") ? `${secHead('Education')}${eduHTML}` : ''}
    </div>
    <script>setTimeout(()=>{window.print();window.close()},600)<\/script>
  </body></html>`;
}

/* ═══════════════════════════════════════════
   EDITOR FIELD
   ═══════════════════════════════════════════ */

function F({ label, value, onChange, multi, placeholder }: { label: string; value: string; onChange: (v: string) => void; multi?: boolean; placeholder?: string }) {
  return (
    <div className="mb-2.5">
      <label className="block text-[11px] text-gravel mb-1 font-medium">{label}</label>
      {multi ? (
        <textarea value={value} onChange={(e) => { onChange(e.target.value); e.target.style.height = "auto"; e.target.style.height = e.target.scrollHeight + "px"; }}
          placeholder={placeholder} className="input-el !rounded-lg resize-none text-[12px]" style={{ minHeight: "60px", overflow: "hidden" }} />
      ) : (
        <input value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="input-el text-[12px]" />
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════ */

export default function ResumePage() {
  const [resume, setResume] = useState<ResumeData>(DEFAULT_RESUME);
  const [section, setSection] = useState("personal");
  const [jd, setJd] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [hiddenSections, setHiddenSections] = useState<Set<string>>(new Set());

  const set = useCallback((key: string, val: any) => setResume((p) => ({ ...p, [key]: val })), []);
  const setExp = useCallback((idx: number, key: string, val: any) => {
    setResume(p => { const e = [...p.experience]; e[idx] = { ...e[idx], [key]: val }; return { ...p, experience: e }; });
  }, []);

  const toggleSection = (name: string) => {
    setHiddenSections(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name); else next.add(name);
      return next;
    });
  };

  const handleRestore = () => {
    setResume(DEFAULT_RESUME);
    setHiddenSections(new Set());
    setAnalysis(null);
    setJd("");
  };

  const handlePrint = () => {
    const w = window.open("", "_blank");
    if (!w) return;
    w.document.write(buildPrintHTML(resume, hiddenSections));
    w.document.close();
  };

  const handleAnalyze = async () => {
    if (!jd.trim()) return;
    setAnalyzing(true);
    try {
      const skills = Object.values(resume.skills).join(", ");
      setAnalysis(await api.analyzeJD({ job_description: jd, user_skills: skills }));
    } catch (e: any) { alert(e.message); }
    finally { setAnalyzing(false); }
  };

  const TABS = [
    { key: "personal", label: "Personal" }, { key: "experience", label: "Experience" },
    { key: "projects", label: "Projects" }, { key: "skills", label: "Skills" },
    { key: "education", label: "Education" }, { key: "jd", label: "JD Match" },
  ];

  return (
    <div className="flex gap-0 -mx-10 -my-8" style={{ height: "100vh" }}>
      {/* ── Left: Editor ── */}
      <div className="w-[400px] flex-shrink-0 border-r border-chalk bg-white overflow-y-auto">
        <div className="sticky top-0 z-10 bg-white border-b border-chalk px-3 py-2.5 flex items-center justify-between">
          <div className="flex gap-1 flex-wrap">
            {TABS.map(t => (
              <button key={t.key} onClick={() => setSection(t.key)}
                className={`${section === t.key ? "tag-active" : "tag"} !text-[10px] !px-2 !py-0.5`}>{t.label}</button>
            ))}
          </div>
          <button onClick={handleRestore} className="text-[9px] text-gravel hover:text-obsidian underline whitespace-nowrap ml-2">
            Restore
          </button>
        </div>

        <div className="p-4">
          {section === "personal" && (
            <>
              <h3 className="text-[13px] font-medium text-obsidian mb-3">Personal Info</h3>
              <F label="Full Name" value={resume.name} onChange={v => set("name", v)} />
              <F label="Title / Headline" value={resume.title} onChange={v => set("title", v)} />
              <F label="Phone" value={resume.contact.phone} onChange={v => set("contact", { ...resume.contact, phone: v })} />
              <div className="grid grid-cols-2 gap-2">
                <F label="Email Display" value={resume.contact.email.text} onChange={v => set("contact", { ...resume.contact, email: { ...resume.contact.email, text: v } })} />
                <F label="Email URL" value={resume.contact.email.url} onChange={v => set("contact", { ...resume.contact, email: { ...resume.contact.email, url: v } })} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <F label="LinkedIn Display" value={resume.contact.linkedin.text} onChange={v => set("contact", { ...resume.contact, linkedin: { ...resume.contact.linkedin, text: v } })} />
                <F label="LinkedIn URL" value={resume.contact.linkedin.url} onChange={v => set("contact", { ...resume.contact, linkedin: { ...resume.contact.linkedin, url: v } })} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <F label="GitHub Display" value={resume.contact.github.text} onChange={v => set("contact", { ...resume.contact, github: { ...resume.contact.github, text: v } })} />
                <F label="GitHub URL" value={resume.contact.github.url} onChange={v => set("contact", { ...resume.contact, github: { ...resume.contact.github, url: v } })} />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <F label="Portfolio Display" value={resume.contact.portfolio.text} onChange={v => set("contact", { ...resume.contact, portfolio: { ...resume.contact.portfolio, text: v } })} />
                <F label="Portfolio URL" value={resume.contact.portfolio.url} onChange={v => set("contact", { ...resume.contact, portfolio: { ...resume.contact.portfolio, url: v } })} />
              </div>
            </>
          )}

          {section === "experience" && (
            <>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-[13px] font-medium text-obsidian">Work Experience</h3>
                <button onClick={() => set("experience", [...resume.experience, { company: "", dates: "", title: "", bullets: [{ text: "", link: null }] }])} className="btn-ghost text-[11px]">+ Add Role</button>
              </div>
              {resume.experience.map((exp, i) => (
                <div key={i} className="mb-4 p-3 bg-powder rounded-card relative group">
                  <button onClick={() => set("experience", resume.experience.filter((_, k) => k !== i))}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-grade-d text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity" title="Remove this role">-</button>
                  <div className="grid grid-cols-2 gap-2">
                    <F label="Company" value={exp.company} onChange={v => setExp(i, "company", v)} />
                    <F label="Dates" value={exp.dates} onChange={v => setExp(i, "dates", v)} />
                  </div>
                  <F label="Title" value={exp.title} onChange={v => setExp(i, "title", v)} />
                  <p className="text-[10px] text-gravel mb-1 font-medium">Bullet Points</p>
                  {exp.bullets.map((b, j) => (
                    <div key={j} className="mb-1.5 flex gap-1">
                      <div className="flex-1">
                        <textarea value={b.text} onChange={e => {
                          const ex = [...resume.experience]; const bul = [...ex[i].bullets];
                          bul[j] = { ...bul[j], text: e.target.value }; ex[i] = { ...ex[i], bullets: bul }; set("experience", ex);
                          e.target.style.height = "auto"; e.target.style.height = e.target.scrollHeight + "px";
                        }} className="input-el text-[11px] resize-none !rounded-lg w-full" style={{ minHeight: "50px", overflow: "hidden" }} />
                        <div className="flex gap-1 mt-0.5">
                          <input value={b.link?.text || ""} placeholder="Link label" onChange={e => {
                            const ex = [...resume.experience]; const bul = [...ex[i].bullets];
                            bul[j] = { ...bul[j], link: { text: e.target.value, url: bul[j].link?.url || "#" } };
                            ex[i] = { ...ex[i], bullets: bul }; set("experience", ex);
                          }} className="input-el text-[10px] !py-1 !px-1.5 flex-1" />
                          <input value={b.link?.url || ""} placeholder="Link URL" onChange={e => {
                            const ex = [...resume.experience]; const bul = [...ex[i].bullets];
                            bul[j] = { ...bul[j], link: { text: bul[j].link?.text || "Link", url: e.target.value } };
                            ex[i] = { ...ex[i], bullets: bul }; set("experience", ex);
                          }} className="input-el text-[10px] !py-1 !px-1.5 flex-1" />
                        </div>
                      </div>
                      <button onClick={() => {
                        const ex = [...resume.experience]; const bul = ex[i].bullets.filter((_, k) => k !== j);
                        ex[i] = { ...ex[i], bullets: bul }; set("experience", ex);
                      }} className="text-fog hover:text-grade-d text-[11px] px-1 self-start mt-1">x</button>
                    </div>
                  ))}
                  <button onClick={() => {
                    const ex = [...resume.experience]; ex[i] = { ...ex[i], bullets: [...ex[i].bullets, { text: "", link: null }] }; set("experience", ex);
                  }} className="text-[10px] text-gravel hover:text-obsidian mt-1">+ Add bullet</button>
                </div>
              ))}
            </>
          )}

          {section === "projects" && (
            <>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-[13px] font-medium text-obsidian">Projects</h3>
                <button onClick={() => set("projects", [...resume.projects, { name: "", subtitle: "", tech: "", bullets: [""] }])} className="btn-ghost text-[11px]">+ Add</button>
              </div>
              {resume.projects.map((p, i) => (
                <div key={i} className="mb-3 p-3 bg-powder rounded-card relative group">
                  <button onClick={() => set("projects", resume.projects.filter((_, k) => k !== i))}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-grade-d text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity" title="Remove this project">-</button>
                  <F label="Name" value={p.name} onChange={v => { const ps = [...resume.projects]; ps[i] = { ...ps[i], name: v }; set("projects", ps); }} />
                  <F label="Subtitle" value={p.subtitle} onChange={v => { const ps = [...resume.projects]; ps[i] = { ...ps[i], subtitle: v }; set("projects", ps); }} />
                  <F label="Tech Stack" value={p.tech} onChange={v => { const ps = [...resume.projects]; ps[i] = { ...ps[i], tech: v }; set("projects", ps); }} />
                  <p className="text-[10px] text-gravel mb-1 font-medium">Bullets</p>
                  {p.bullets.map((b, j) => (
                    <div key={j} className="flex gap-1 mb-1">
                      <input value={b} onChange={e => { const ps = [...resume.projects]; const bul = [...ps[i].bullets]; bul[j] = e.target.value; ps[i] = { ...ps[i], bullets: bul }; set("projects", ps); }}
                        className="input-el text-[11px] flex-1" />
                      <button onClick={() => { const ps = [...resume.projects]; ps[i] = { ...ps[i], bullets: ps[i].bullets.filter((_, k) => k !== j) }; set("projects", ps); }}
                        className="text-fog hover:text-grade-d text-[11px] px-1">x</button>
                    </div>
                  ))}
                  <button onClick={() => { const ps = [...resume.projects]; ps[i] = { ...ps[i], bullets: [...ps[i].bullets, ""] }; set("projects", ps); }}
                    className="text-[10px] text-gravel hover:text-obsidian">+ bullet</button>
                </div>
              ))}
            </>
          )}

          {section === "skills" && (
            <>
              <h3 className="text-[13px] font-medium text-obsidian mb-3">Technical Skills</h3>
              {Object.entries(resume.skills).map(([cat, val]) => (
                <div key={cat} className="relative group">
                  <button onClick={() => { const s = { ...resume.skills }; delete s[cat]; set("skills", s); }}
                    className="absolute -top-0.5 -right-1 w-4 h-4 rounded-full bg-grade-d text-white text-[9px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity" title={`Remove ${cat}`}>-</button>
                  <F label={cat} value={val} onChange={v => set("skills", { ...resume.skills, [cat]: v })} />
                </div>
              ))}
              <button onClick={() => {
                const name = prompt("Skill category name (e.g. 'DevOps'):");
                if (name) set("skills", { ...resume.skills, [name]: "" });
              }} className="text-[10px] text-gravel hover:text-obsidian mt-1">+ Add skill category</button>
            </>
          )}

          {section === "education" && (
            <>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-[13px] font-medium text-obsidian">Education</h3>
                <button onClick={() => set("education", [...resume.education, { school: "", dates: "", degree: "", detail: "" }])} className="btn-ghost text-[11px]">+ Add</button>
              </div>
              {resume.education.map((edu, i) => (
                <div key={i} className="mb-3 p-3 bg-powder rounded-card relative group">
                  <button onClick={() => set("education", resume.education.filter((_, k) => k !== i))}
                    className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-grade-d text-white text-[10px] flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity" title="Remove">-</button>
                  <div className="grid grid-cols-2 gap-2">
                    <F label="School" value={edu.school} onChange={v => { const eds = [...resume.education]; eds[i] = { ...eds[i], school: v }; set("education", eds); }} />
                    <F label="Dates" value={edu.dates} onChange={v => { const eds = [...resume.education]; eds[i] = { ...eds[i], dates: v }; set("education", eds); }} />
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <F label="Degree" value={edu.degree} onChange={v => { const eds = [...resume.education]; eds[i] = { ...eds[i], degree: v }; set("education", eds); }} />
                    <F label="GPA / Marks" value={edu.detail} onChange={v => { const eds = [...resume.education]; eds[i] = { ...eds[i], detail: v }; set("education", eds); }} />
                  </div>
                </div>
              ))}
            </>
          )}

          {section === "jd" && (
            <>
              <h3 className="text-[13px] font-medium text-obsidian mb-3">JD Analysis & Resume Tailoring</h3>
              <F label="Paste Job Description" value={jd} onChange={setJd} multi placeholder="Paste the full job description here..." />

              <div className="flex gap-2 mb-4">
                <button onClick={handleAnalyze} disabled={analyzing || !jd.trim()} className="btn-secondary flex-1 disabled:opacity-50 text-[12px]">
                  {analyzing ? "Analyzing..." : "Analyze Match"}
                </button>
                <button onClick={() => {
                  if (!analysis) { alert("Analyze the JD first"); return; }
                  // Auto-inject missing keywords into skills section
                  const missing = analysis.missing_skills || [];
                  if (missing.length > 0) {
                    const currentSkills = Object.values(resume.skills).join(", ").toLowerCase();
                    const toAdd = missing.filter((s: string) => !currentSkills.includes(s.toLowerCase()));
                    if (toAdd.length > 0) {
                      const skills = { ...resume.skills };
                      // Add to the most relevant category or create new
                      const lastKey = Object.keys(skills).pop() || "Other";
                      skills[lastKey] = skills[lastKey] + ", " + toAdd.join(", ");
                      set("skills", skills);
                    }
                  }
                  // Update title to match JD if possible
                  alert(`Injected ${missing.length} missing keywords into your skills section. Review the preview.`);
                }} disabled={!analysis} className="btn-primary flex-1 disabled:opacity-50 text-[12px]">
                  Inject Keywords
                </button>
              </div>

              {analysis && (
                <div className="space-y-4">
                  {/* Score */}
                  <div className="flex items-center gap-3 p-3 bg-powder rounded-card">
                    <div className="w-14 h-14 rounded-full border-[3px] border-obsidian flex items-center justify-center">
                      <span className="text-[20px] font-bold text-obsidian">{analysis.ats_score}</span>
                    </div>
                    <div>
                      <p className="text-[13px] font-medium text-obsidian">ATS Match Score</p>
                      <p className="text-[11px] text-gravel">{analysis.keyword_coverage}% keyword coverage</p>
                    </div>
                  </div>

                  {/* Matched */}
                  {analysis.matched_skills?.length > 0 && (
                    <div>
                      <p className="text-[10px] text-gravel mb-1.5 font-medium uppercase tracking-wider">Matched Keywords</p>
                      <div className="flex flex-wrap gap-1">{analysis.matched_skills.map((s: string) => <span key={s} className="px-2.5 py-1 bg-green-50 text-green-700 rounded-pill text-[10px] border border-green-200">{s}</span>)}</div>
                    </div>
                  )}

                  {/* Missing */}
                  {analysis.missing_skills?.length > 0 && (
                    <div>
                      <p className="text-[10px] text-gravel mb-1.5 font-medium uppercase tracking-wider">Missing Keywords</p>
                      <div className="flex flex-wrap gap-1">{analysis.missing_skills.map((s: string) => <span key={s} className="px-2.5 py-1 bg-amber-50 text-amber-700 rounded-pill text-[10px] border border-amber-200">{s}</span>)}</div>
                    </div>
                  )}

                  {/* Suggestions */}
                  {analysis.suggestions?.length > 0 && (
                    <div>
                      <p className="text-[10px] text-gravel mb-1.5 font-medium uppercase tracking-wider">Suggestions</p>
                      <ul className="space-y-1">
                        {analysis.suggestions.map((s: string, i: number) => (
                          <li key={i} className="text-[11px] text-cinder flex items-start gap-1.5">
                            <span className="text-obsidian mt-px">-</span> {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* ── Right: Live Preview ── */}
      <div className="flex-1 bg-[#d4d4d4] overflow-auto">
        <div className="sticky top-0 z-10 bg-eggshell border-b border-chalk px-6 py-2.5 flex items-center justify-between">
          <p className="text-[12px] text-gravel">Live Preview</p>
          <button onClick={handlePrint} className="btn-primary text-[13px]">
            <svg className="w-4 h-4 inline mr-1.5 -mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9V2h12v7 M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2 M6 14h12v8H6z" /></svg>
            Export PDF
          </button>
        </div>
        <div className="py-8 flex justify-center">
          {/* Wrapper: sets the VISUAL size, clips overflow from the scaled inner div */}
          <div style={{
            width: `${8.5 * 0.6 * 96}px`,   /* 8.5in * 0.6 scale * 96dpi */
            height: `${11 * 0.6 * 96}px`,    /* 11in * 0.6 scale * 96dpi */
            overflow: "hidden",
            boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
            borderRadius: "4px",
            position: "relative",
          }}>
            <ResumePreview data={resume} scale={0.6} hidden={hiddenSections} />
          </div>
        </div>
      </div>
    </div>
  );
}
