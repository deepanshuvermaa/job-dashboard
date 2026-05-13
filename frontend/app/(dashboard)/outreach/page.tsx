"use client";
import { useState } from "react";
import { api } from "@/lib/api";

export default function OutreachPage() {
  const [emails, setEmails] = useState("");
  const [role, setRole] = useState("");
  const [resume, setResume] = useState<File | null>(null);
  const [senderEmail, setSenderEmail] = useState("");
  const [generated, setGenerated] = useState<any[]>([]);
  const [sending, setSending] = useState(false);
  const [log, setLog] = useState<any[]>([]);
  const [tab, setTab] = useState<"compose" | "log">("compose");

  const handleGenerate = async () => {
    if (!emails.trim()) return;
    setSending(true);
    try {
      const emailList = emails.split(/[\n,;]+/).map(e => e.trim()).filter(e => e.includes("@"));
      const results: any[] = [];
      for (const email of emailList) {
        const namePart = email.split("@")[0].replace(/[._-]/g, " ");
        const res = await api.generateOutreach({
          recruiter_email: email,
          recruiter_name: namePart,
          job_title: role || "Software Engineer",
          company: email.split("@")[1]?.split(".")[0] || "your company",
        });
        results.push({ ...res, recruiter_email: email });
      }
      setGenerated(results);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleSendAll = async () => {
    setSending(true);
    try {
      for (const email of generated) {
        await api.sendOutreach({
          recruiter_email: email.recruiter_email,
          recruiter_name: email.recruiter_name,
          company: email.company,
          job_title: role,
          subject: email.subject,
          body: email.body,
        });
      }
      setGenerated([]);
      const logData = await api.getOutreachLog();
      setLog(logData.log || []);
      setTab("log");
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  const handleFileImport = async (file: File) => {
    setSending(true);
    try {
      const res = await api.importOutreachContacts(file, "introduction");
      const logData = await api.getOutreachLog();
      setLog(logData.log || []);
      setTab("log");
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-heading text-obsidian font-display">Cold Outreach</h1>
        <p className="text-body text-gravel mt-1">AI-curated personalized emails to recruiters & hiring managers</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-chalk">
        <button onClick={() => setTab("compose")} className={`pb-2 text-[13px] font-medium border-b-2 transition-colors ${tab === "compose" ? "border-obsidian text-obsidian" : "border-transparent text-gravel hover:text-obsidian"}`}>Compose</button>
        <button onClick={() => { setTab("log"); api.getOutreachLog().then(d => setLog(d.log || [])); }} className={`pb-2 text-[13px] font-medium border-b-2 transition-colors ${tab === "log" ? "border-obsidian text-obsidian" : "border-transparent text-gravel hover:text-obsidian"}`}>Sent Log</button>
      </div>

      {tab === "compose" ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Input */}
          <div className="space-y-4">
            <div className="card">
              <h3 className="text-body-medium text-obsidian mb-3">Target Emails</h3>
              <textarea
                value={emails}
                onChange={(e) => setEmails(e.target.value)}
                placeholder="Paste emails (one per line, comma or semicolon separated)&#10;e.g. recruiter@company.com&#10;hr@startup.io"
                className="w-full h-32 px-3 py-2 border border-chalk rounded-lg text-[13px] text-obsidian bg-eggshell focus:outline-none focus:border-obsidian resize-none"
              />
              <p className="text-[11px] text-fog mt-1">{emails.split(/[\n,;]+/).filter(e => e.trim().includes("@")).length} emails detected</p>
            </div>

            <div className="card">
              <h3 className="text-body-medium text-obsidian mb-3">Your Details</h3>
              <input
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                placeholder="Your email (sender)"
                className="w-full px-3 py-2 border border-chalk rounded-lg text-[13px] text-obsidian bg-eggshell focus:outline-none focus:border-obsidian mb-3"
              />
              <input
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="Target role (e.g. Full Stack Developer, Cloud Engineer)"
                className="w-full px-3 py-2 border border-chalk rounded-lg text-[13px] text-obsidian bg-eggshell focus:outline-none focus:border-obsidian mb-3"
              />
              <label className="flex items-center gap-2 px-3 py-2 border border-chalk rounded-lg cursor-pointer hover:bg-powder transition-colors">
                <svg className="w-4 h-4 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M12 18v-6M9 15h6"/></svg>
                <span className="text-[13px] text-gravel">{resume ? resume.name : "Attach Resume (PDF)"}</span>
                <input type="file" accept=".pdf,.docx" className="hidden" onChange={(e) => setResume(e.target.files?.[0] || null)} />
              </label>
            </div>

            <div className="card">
              <h3 className="text-body-medium text-obsidian mb-3">Import from File</h3>
              <label className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-chalk rounded-lg cursor-pointer hover:bg-powder transition-colors">
                <svg className="w-5 h-5 text-gravel" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                <span className="text-[13px] text-gravel">Upload CSV/Excel with contacts</span>
                <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={(e) => { if (e.target.files?.[0]) handleFileImport(e.target.files[0]); }} />
              </label>
              <p className="text-[11px] text-fog mt-2">Columns: name, email, company, job_title</p>
            </div>

            <button onClick={handleGenerate} disabled={sending || !emails.trim()} className="btn-primary w-full disabled:opacity-50">
              {sending ? "Generating..." : "Generate Personalized Emails"}
            </button>
          </div>

          {/* Right: Preview */}
          <div className="space-y-4">
            {generated.length > 0 ? (
              <>
                <div className="flex items-center justify-between">
                  <h3 className="text-body-medium text-obsidian">{generated.length} emails ready</h3>
                  <button onClick={handleSendAll} disabled={sending} className="btn-primary disabled:opacity-50">
                    {sending ? "Sending..." : "Send All"}
                  </button>
                </div>
                {generated.map((email, i) => (
                  <div key={i} className="card">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-[11px] font-medium text-gravel px-2 py-0.5 rounded-pill border border-chalk">To: {email.recruiter_email}</span>
                      <span className="text-[11px] text-fog">{email.company}</span>
                    </div>
                    <p className="text-[12px] font-medium text-obsidian mb-1">{email.subject}</p>
                    <p className="text-[11px] text-gravel leading-relaxed whitespace-pre-wrap">{email.body?.substring(0, 300)}...</p>
                  </div>
                ))}
              </>
            ) : (
              <div className="card text-center py-12">
                <svg className="w-12 h-12 text-chalk mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="M22 6l-10 7L2 6"/></svg>
                <p className="text-body text-gravel">Paste emails and generate personalized outreach</p>
                <p className="text-caption text-fog mt-1">Each email is AI-curated with your resume highlights & projects</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Log Tab */
        <div className="space-y-3">
          {log.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-body text-gravel">No emails sent yet</p>
            </div>
          ) : log.map((entry, i) => (
            <div key={i} className="card flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-[13px] text-obsidian font-medium truncate">{entry.recruiter_name} · {entry.company}</p>
                <p className="text-[11px] text-gravel truncate">{entry.subject}</p>
              </div>
              <span className={`text-[10px] font-medium px-2 py-0.5 rounded-pill ${entry.status === "sent" ? "bg-green-50 text-green-700" : "bg-amber-50 text-amber-700"}`}>{entry.status}</span>
              <span className="text-[10px] text-fog">{new Date(entry.created_at).toLocaleDateString()}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
