"use client";
import { useRef, useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

/* ─── Feature Data ─── */
const FEATURES = [
  {
    tag: "Discovery",
    title: "696+ Job Sources,\nOne Dashboard",
    desc: "Scrape LinkedIn, Greenhouse, Lever, Ashby, Workable, and 600+ auto-detected career pages. Every job normalized, deduplicated, and scored — delivered to your Jobbo-style feed.",
    stats: ["14 ATS Types", "65 Curated Portals", "611 Auto-Detected", "19 Search Queries"],
    visual: "grid",
  },
  {
    tag: "Intelligence",
    title: "10-Dimension\nAI Evaluation",
    desc: "Every job is scored across Role Match, Skills Alignment, Seniority Fit, Compensation, Interview Likelihood, Growth Potential, Company Reputation, Location Fit, Tech Stack Match, and Culture Signals.",
    stats: ["A/B/C/D/F Grades", "Gate Pass System", "Weighted Scoring", "Adaptive Weights"],
    visual: "radar",
  },
  {
    tag: "Resume",
    title: "ATS-Optimized\nResume Tailoring",
    desc: "Paste a JD — get an ATS score, matched vs missing skills, and a tailored resume with injected keywords, reordered experience, and archetype-specific formatting. Six archetypes. PDF download.",
    stats: ["6 Archetypes", "Keyword Injection", "ATS Score", "PDF Export"],
    visual: "resume",
  },
  {
    tag: "Automation",
    title: "One-Click\nAuto Apply",
    desc: "Easy Apply bot with AI-powered question answering, human-like behavior simulation, and anti-detection. Pattern-matched answers for 50+ question types with AI fallback for unknowns.",
    stats: ["Easy Apply Bot", "AI Q&A", "Anti-Detection", "Session Persistence"],
    visual: "auto",
  },
];

const PLATFORM_FEATURES = [
  { d: "M11 3a8 8 0 100 16 8 8 0 000-16z M21 21l-4.35-4.35", title: "Smart Search", desc: "LinkedIn scraper with experience, time, type, and remote filters" },
  { d: "M18 20V10 M12 20V4 M6 20v-6", title: "Job Evaluations", desc: "10-dimension AI scoring with expandable detail views" },
  { d: "M12 2a10 10 0 100 20 10 10 0 000-20z M2 12h20", title: "Portal Scanner", desc: "Scan 696+ company career pages with ATS detection" },
  { d: "M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z M14 2v6h6 M16 13H8 M16 17H8", title: "Resume Builder", desc: "JD analysis, ATS scoring, keyword matching, PDF generation" },
  { d: "M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2 M12 3a4 4 0 100 8 4 4 0 000-8z", title: "AI Profile", desc: "Upload resume, AI extracts skills, experience, education" },
  { d: "M22 11.08V12a10 10 0 11-5.93-9.14 M22 4L12 14.01l-3-3", title: "Applications", desc: "Track pipeline: applied, interview, rejected, offer" },
  { d: "M13 2L3 14h9l-1 8 10-12h-9l1-8", title: "Auto-Apply", desc: "Easy Apply with intelligent form filling and anti-detection" },
  { d: "M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z M22 6l-10 7L2 6", title: "Outreach", desc: "AI-generated recruiter emails with template system" },
  { d: "M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9 M13.73 21a2 2 0 01-3.46 0", title: "Notifications", desc: "Telegram and Discord alerts for new A-grade matches" },
  { d: "M23 6l-9.5 9.5-5-5L1 18", title: "Analytics", desc: "Grade distribution, source breakdown, response rates" },
  { d: "M12 8v4l3 3 M3 12a9 9 0 1018 0 9 9 0 00-18 0", title: "Staleness Engine", desc: "Auto-archive stale jobs on 7, 14, 30, 60 day cycles" },
  { d: "M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2 M23 21v-2a4 4 0 00-3-3.87 M16 3.13a4 4 0 010 7.75", title: "Multi-User Ready", desc: "JWT auth, user-scoped data, PostgreSQL migration path" },
];

const FLOW_STEPS = [
  { num: "01", title: "Scrape", desc: "Run daily scan across LinkedIn + 696 career pages" },
  { num: "02", title: "Deduplicate", desc: "Normalized key matching across all sources" },
  { num: "03", title: "Classify", desc: "Auto-categorize: backend, frontend, devops, AI/ML..." },
  { num: "04", title: "Evaluate", desc: "10-dimension AI scoring with gate pass criteria" },
  { num: "05", title: "Tailor", desc: "Generate ATS-optimized resume per job description" },
  { num: "06", title: "Apply", desc: "Auto-apply with intelligent Q&A or manual review" },
];

/* ─── Intersection Observer Hook ─── */
function useInView(threshold = 0.15) {
  const ref = useRef<HTMLDivElement>(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setInView(true); }, { threshold });
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);
  return { ref, inView };
}

function Section({ children, className = "", dark = false, id }: { children: React.ReactNode; className?: string; dark?: boolean; id?: string }) {
  const { ref, inView } = useInView();
  return (
    <section
      ref={ref}
      id={id}
      className={`relative px-6 md:px-8 ${dark ? "bg-[hsl(201,100%,13%)] text-white" : "bg-white text-[#1d1d1f]"} ${className}`}
      style={{ opacity: inView ? 1 : 0, transform: inView ? "translateY(0)" : "translateY(40px)", transition: "opacity 0.8s ease, transform 0.8s ease" }}
    >
      {children}
    </section>
  );
}

/* ─── Page ─── */
export default function LandingPage() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-[hsl(201,100%,13%)] text-white overflow-x-hidden" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* ─── HERO ─── */}
      <div className="relative min-h-screen flex flex-col">
        {/* Video Background */}
        <video
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover z-0"
          style={{ filter: "brightness(0.4)" }}
        >
          <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260314_131748_f2ca2a28-fed7-44c8-b9a9-bd9acdd5ec31.mp4" type="video/mp4" />
        </video>

        {/* Nav */}
        <nav className="relative z-10 flex items-center justify-between px-6 md:px-8 py-6 max-w-7xl mx-auto w-full">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 liquid-glass rounded-lg flex items-center justify-center">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <span className="text-2xl md:text-3xl tracking-tight text-white" style={{ fontFamily: "'Instrument Serif', serif" }}>
              JobFlow<sup className="text-xs">®</sup>
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-white/60 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-white/60 hover:text-white transition-colors">How It Works</a>
            <a href="#platform" className="text-sm text-white/60 hover:text-white transition-colors">Platform</a>
          </div>

          <Link
            href={user ? "/dashboard" : "/login"}
            className="liquid-glass rounded-full px-6 py-2.5 text-sm text-white hover:scale-[1.03] transition-transform"
          >
            {user ? "Dashboard" : "Get Started"}
          </Link>
        </nav>

        {/* Hero Content */}
        <div className="relative z-10 flex-1 flex flex-col items-center justify-center text-center px-6 pb-32">
          <h1
            className="text-5xl sm:text-7xl md:text-8xl leading-[0.95] tracking-[-2.46px] max-w-7xl font-normal animate-fade-rise"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Where <em className="not-italic text-white/50">careers rise</em><br />
            through <em className="not-italic text-white/50">intelligent automation.</em>
          </h1>

          <p className="text-white/50 text-base sm:text-lg max-w-2xl mt-8 leading-relaxed animate-fade-rise-delay">
            AI-powered job discovery across 696+ sources. Resume tailoring that beats ATS.
            Auto-apply that thinks. Your entire job search — one platform, zero manual work.
          </p>

          <div className="flex gap-4 mt-12 animate-fade-rise-delay-2">
            <Link
              href={user ? "/dashboard" : "/register"}
              className="liquid-glass rounded-full px-14 py-5 text-base text-white hover:scale-[1.03] transition-transform cursor-pointer"
            >
              Begin Journey
            </Link>
            <a
              href="#features"
              className="rounded-full px-10 py-5 text-base text-white/60 border border-white/10 hover:border-white/30 hover:text-white transition-all cursor-pointer"
            >
              Learn More
            </a>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-fade-rise-delay-2">
            <span className="text-[10px] uppercase tracking-[3px] text-white/30">Scroll</span>
            <div className="w-px h-8 bg-gradient-to-b from-white/30 to-transparent" />
          </div>
        </div>
      </div>

      {/* ─── TRUST BAR ─── */}
      <Section dark className="py-16 border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {[
              { num: "696+", label: "Job Sources" },
              { num: "14", label: "ATS Integrations" },
              { num: "10", label: "Scoring Dimensions" },
              { num: "6", label: "Resume Archetypes" },
            ].map((s) => (
              <div key={s.label}>
                <p className="text-4xl md:text-5xl font-light tracking-tight" style={{ fontFamily: "'Instrument Serif', serif" }}>
                  {s.num}
                </p>
                <p className="text-sm text-white/40 mt-2 uppercase tracking-[2px]">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ─── FEATURE SECTIONS ─── */}
      <div id="features">
        {FEATURES.map((feature, i) => {
          const isDark = i % 2 === 0;
          return (
            <Section key={feature.tag} dark={isDark} className="py-24 md:py-32">
              <div className="max-w-7xl mx-auto">
                <div className={`grid grid-cols-1 lg:grid-cols-2 gap-16 items-center ${i % 2 === 1 ? "lg:grid-flow-dense" : ""}`}>
                  {/* Text */}
                  <div className={i % 2 === 1 ? "lg:col-start-2" : ""}>
                    <span className={`text-xs uppercase tracking-[3px] ${isDark ? "text-white/30" : "text-[#7a7a7a]"}`}>
                      {feature.tag}
                    </span>
                    <h2
                      className="text-4xl md:text-5xl lg:text-6xl leading-[1.05] tracking-tight mt-4 whitespace-pre-line font-normal"
                      style={{ fontFamily: "'Instrument Serif', serif" }}
                    >
                      {feature.title}
                    </h2>
                    <p className={`text-lg leading-relaxed mt-6 max-w-lg ${isDark ? "text-white/50" : "text-[#7a7a7a]"}`}>
                      {feature.desc}
                    </p>
                    <div className="flex flex-wrap gap-3 mt-8">
                      {feature.stats.map((stat) => (
                        <span
                          key={stat}
                          className={`px-4 py-2 rounded-full text-sm ${
                            isDark
                              ? "liquid-glass text-white/70"
                              : "bg-[#f5f5f7] text-[#1d1d1f] border border-[#e0e0e0]"
                          }`}
                        >
                          {stat}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Visual */}
                  <div className={`${i % 2 === 1 ? "lg:col-start-1 lg:row-start-1" : ""}`}>
                    <FeatureVisual type={feature.visual} isDark={isDark} />
                  </div>
                </div>
              </div>
            </Section>
          );
        })}
      </div>

      {/* ─── HOW IT WORKS ─── */}
      <Section dark className="py-24 md:py-32" id="how-it-works">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-xs uppercase tracking-[3px] text-white/30">Pipeline</span>
            <h2
              className="text-4xl md:text-6xl tracking-tight mt-4 font-normal"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              From scrape to <em className="not-italic text-white/50">applied</em>
            </h2>
            <p className="text-white/40 text-lg mt-4 max-w-xl mx-auto">The entire job hunting pipeline, automated end-to-end</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FLOW_STEPS.map((step) => (
              <div key={step.num} className="liquid-glass rounded-2xl p-8 group hover:scale-[1.02] transition-transform">
                <span className="text-5xl font-light text-white/10 block mb-4" style={{ fontFamily: "'Instrument Serif', serif" }}>
                  {step.num}
                </span>
                <h3 className="text-xl font-medium text-white mb-2">{step.title}</h3>
                <p className="text-white/40 text-sm leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ─── PLATFORM FEATURES GRID ─── */}
      <Section className="py-24 md:py-32" id="platform">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-2xl mb-16">
            <span className="text-[14px] text-[#777169]">Platform</span>
            <h2
              className="text-[36px] md:text-[48px] tracking-tight mt-3 font-normal text-[#000000] leading-[1.08]"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Twelve tools, one interface.
            </h2>
            <p className="text-[16px] text-[#777169] mt-4 leading-relaxed">Every stage of the job search — from discovery to offer — handled by purpose-built modules that work together.</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-px bg-[#e5e5e5] rounded-2xl overflow-hidden" style={{ boxShadow: 'rgba(0,0,0,0.4) 0px 0px 1px 0px, rgba(0,0,0,0.04) 0px 2px 4px' }}>
            {PLATFORM_FEATURES.map((f) => (
              <div key={f.title} className="bg-white p-7 hover:bg-[#fdfcfc] transition-colors">
                <div className="w-9 h-9 rounded-[10px] bg-[#f5f3f1] flex items-center justify-center mb-4">
                  <svg className="w-[18px] h-[18px] text-[#000000]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d={f.d} /></svg>
                </div>
                <h3 className="text-[15px] font-medium text-[#000000] mb-1.5">{f.title}</h3>
                <p className="text-[14px] text-[#777169] leading-[1.5]">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </Section>

      {/* ─── TECH STACK ─── */}
      <Section dark className="py-20 border-t border-white/5">
        <div className="max-w-7xl mx-auto text-center">
          <span className="text-xs uppercase tracking-[3px] text-white/30">Built With</span>
          <div className="flex flex-wrap justify-center gap-6 mt-8">
            {["Next.js 14", "FastAPI", "SQLAlchemy", "Tailwind CSS", "TypeScript", "Selenium", "GPT-4", "Gemini", "Claude", "PostgreSQL"].map((t) => (
              <span key={t} className="liquid-glass rounded-full px-5 py-2.5 text-sm text-white/50">
                {t}
              </span>
            ))}
          </div>
        </div>
      </Section>

      {/* ─── FINAL CTA ─── */}
      <Section dark className="py-32 md:py-40">
        <div className="max-w-4xl mx-auto text-center">
          <h2
            className="text-5xl md:text-7xl lg:text-8xl leading-[0.95] tracking-[-2px] font-normal"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Stop searching.<br />
            <em className="not-italic text-white/50">Start landing.</em>
          </h2>
          <p className="text-white/40 text-lg mt-8 max-w-lg mx-auto">
            Join the platform that turns job hunting from a full-time job into a one-click operation.
          </p>
          <div className="flex justify-center gap-4 mt-12">
            <Link
              href={user ? "/dashboard" : "/register"}
              className="liquid-glass rounded-full px-14 py-5 text-base text-white hover:scale-[1.03] transition-transform"
            >
              Get Started Free
            </Link>
            <Link
              href="/login"
              className="rounded-full px-10 py-5 text-base text-white/50 border border-white/10 hover:border-white/30 hover:text-white transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </Section>

      {/* ─── FOOTER ─── */}
      <footer className="bg-[hsl(201,100%,10%)] border-t border-white/5 px-6 md:px-8 py-12">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <span className="text-xl tracking-tight text-white/60" style={{ fontFamily: "'Instrument Serif', serif" }}>
              JobFlow<sup className="text-[8px]">®</sup>
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-white/30">
            <a href="#features" className="hover:text-white/60 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-white/60 transition-colors">Pipeline</a>
            <a href="#platform" className="hover:text-white/60 transition-colors">Platform</a>
            <Link href="/login" className="hover:text-white/60 transition-colors">Sign In</Link>
          </div>
          <p className="text-xs text-white/20">
            &copy; 2026 JobFlow. AI-powered job automation.
          </p>
        </div>
      </footer>
    </div>
  );
}

/* ─── Feature Visuals ─── */

function FeatureVisual({ type, isDark }: { type: string; isDark: boolean }) {
  const cardBg = isDark ? "rgba(255,255,255,0.03)" : "#f5f5f7";
  const cardBorder = isDark ? "rgba(255,255,255,0.06)" : "#e0e0e0";
  const textPrimary = isDark ? "#fff" : "#1d1d1f";
  const textMuted = isDark ? "rgba(255,255,255,0.4)" : "#7a7a7a";

  if (type === "grid") {
    // Mock job cards
    const jobs = [
      { title: "Senior Backend Engineer", company: "Stripe", grade: "A", score: 94, salary: "$180k-$220k" },
      { title: "ML Platform Engineer", company: "Anthropic", grade: "A", score: 96, salary: "$200k-$280k" },
      { title: "Full Stack Developer", company: "Vercel", grade: "A", score: 91, salary: "$150k-$190k" },
    ];
    return (
      <div className="space-y-3">
        {jobs.map((j) => (
          <div key={j.company} className="rounded-xl p-4 flex items-center gap-4" style={{ background: cardBg, border: `1px solid ${cardBorder}` }}>
            <div className="w-10 h-10 rounded-lg flex items-center justify-center text-sm font-semibold" style={{ background: isDark ? "rgba(255,255,255,0.06)" : "#e8e8ed", color: textMuted }}>
              {j.company[0]}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium" style={{ color: textPrimary }}>{j.title}</p>
              <p className="text-xs" style={{ color: textMuted }}>{j.company} · {j.salary}</p>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-6 h-6 rounded text-[10px] font-bold flex items-center justify-center bg-[#34c759] text-white">{j.grade}</span>
              <span className="text-xs" style={{ color: textMuted }}>{j.score}</span>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (type === "radar") {
    // Radar chart mock
    const dims = ["Role", "Skills", "Seniority", "Comp", "Interview", "Growth", "Rep", "Location", "Tech", "Culture"];
    const values = [92, 88, 96, 85, 90, 78, 82, 95, 91, 80];
    const size = 220;
    const cx = size / 2, cy = size / 2, maxR = 85;
    const pts = dims.map((_, i) => {
      const angle = (Math.PI * 2 * i) / dims.length - Math.PI / 2;
      const r = maxR * (values[i] / 100);
      return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`;
    });
    return (
      <div className="flex justify-center">
        <div className="rounded-2xl p-8 inline-block" style={{ background: cardBg, border: `1px solid ${cardBorder}` }}>
          <svg viewBox={`0 0 ${size} ${size}`} className="w-52 h-52 mx-auto">
            {[0.25, 0.5, 0.75, 1].map((s) => (
              <polygon key={s} points={dims.map((_, i) => { const a = (Math.PI * 2 * i) / dims.length - Math.PI / 2; return `${cx + maxR * s * Math.cos(a)},${cy + maxR * s * Math.sin(a)}`; }).join(" ")} fill="none" stroke={isDark ? "rgba(255,255,255,0.06)" : "#e0e0e0"} strokeWidth="0.5" />
            ))}
            <polygon points={pts.join(" ")} fill="rgba(0,102,204,0.15)" stroke="#0066cc" strokeWidth="1.5" />
            {dims.map((d, i) => { const a = (Math.PI * 2 * i) / dims.length - Math.PI / 2; const lr = maxR + 20; return <text key={d} x={cx + lr * Math.cos(a)} y={cy + lr * Math.sin(a)} textAnchor="middle" dominantBaseline="middle" fill={textMuted} fontSize="8">{d}</text>; })}
          </svg>
          <div className="flex items-center justify-center gap-2 mt-4">
            <span className="w-8 h-8 rounded bg-[#34c759] text-white text-sm font-bold flex items-center justify-center">A</span>
            <span className="text-2xl font-light" style={{ color: textPrimary, fontFamily: "'Instrument Serif', serif" }}>94</span>
            <span className="text-sm" style={{ color: textMuted }}>/ 100</span>
          </div>
        </div>
      </div>
    );
  }

  if (type === "resume") {
    return (
      <div className="rounded-2xl p-6 space-y-4" style={{ background: cardBg, border: `1px solid ${cardBorder}` }}>
        <div className="flex items-center gap-3">
          <div className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-light" style={{ background: isDark ? "rgba(0,102,204,0.15)" : "#e8f0fe", color: "#0066cc", fontFamily: "'Instrument Serif', serif" }}>87</div>
          <div>
            <p className="text-sm font-medium" style={{ color: textPrimary }}>ATS Match Score</p>
            <p className="text-xs" style={{ color: textMuted }}>72% keyword coverage</p>
          </div>
        </div>
        <div>
          <p className="text-xs mb-2" style={{ color: textMuted }}>Matched Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {["Python", "React", "PostgreSQL", "AWS"].map((s) => (
              <span key={s} className="px-2 py-0.5 rounded-full text-[10px] bg-[#34c759]/15 text-[#34c759]">{s}</span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs mb-2" style={{ color: textMuted }}>Missing Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {["Kubernetes", "Terraform"].map((s) => (
              <span key={s} className="px-2 py-0.5 rounded-full text-[10px] bg-[#ff9500]/15 text-[#ff9500]">{s}</span>
            ))}
          </div>
        </div>
        <div className="h-px" style={{ background: cardBorder }} />
        <div className="flex items-center justify-between">
          <span className="text-xs" style={{ color: textMuted }}>Resume_Stripe_Backend_2026.pdf</span>
          <span className="text-xs text-[#0066cc]">Download →</span>
        </div>
      </div>
    );
  }

  // Auto-apply visual
  return (
    <div className="rounded-2xl p-6 space-y-3" style={{ background: cardBg, border: `1px solid ${cardBorder}` }}>
      {[
        { q: "Years of experience with Python?", a: "5-7 years", status: "✓" },
        { q: "Are you authorized to work in the US?", a: "Yes", status: "✓" },
        { q: "Expected salary range?", a: "$150,000 - $200,000", status: "✓" },
        { q: "Describe your experience with distributed systems", a: "AI generating response...", status: "⟳" },
      ].map((item) => (
        <div key={item.q} className="rounded-lg p-3" style={{ background: isDark ? "rgba(255,255,255,0.02)" : "#fff", border: `1px solid ${cardBorder}` }}>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs" style={{ color: textMuted }}>{item.q}</p>
              <p className="text-sm mt-1" style={{ color: textPrimary }}>{item.a}</p>
            </div>
            <span className={`text-sm ${item.status === "✓" ? "text-[#34c759]" : "text-[#0066cc] animate-spin-slow"}`}>{item.status}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
