'use client'

import { useState, useEffect, useCallback } from 'react'
import {
  ArrowLeft, ExternalLink, Loader2, CheckCircle, FileText,
  ClipboardCheck, ChevronDown, Rss, Clock, ArrowUpDown,
  BarChart3, Download, ThumbsDown, Bookmark, Search, Wand2,
  X, RefreshCw, Eye, Send,
} from 'lucide-react'
import Link from 'next/link'

// ─── Types ───────────────────────────────────────────────
interface FeedJob {
  job_url: string; title: string; company: string; source: string
  first_seen_at: string; applied: boolean; evaluated: boolean
  evaluation_grade?: string | null; evaluation_score?: number | null
}
interface SourceCount { name: string; count: number }
interface FeedResponse { success: boolean; jobs: FeedJob[]; total: number; sources: SourceCount[] }

// ─── Color Maps ──────────────────────────────────────────
const SRC: Record<string, { bg: string; text: string; border: string }> = {
  linkedin:    { bg: 'bg-blue-100',   text: 'text-blue-700',   border: 'border-blue-300' },
  greenhouse:  { bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-300' },
  lever:       { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-300' },
  ashby:       { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-300' },
  wellfound:   { bg: 'bg-pink-100',   text: 'text-pink-700',   border: 'border-pink-300' },
  workable:    { bg: 'bg-cyan-100',   text: 'text-cyan-700',   border: 'border-cyan-300' },
  dailyremote: { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-300' },
  remotefront: { bg: 'bg-teal-100',   text: 'text-teal-700',   border: 'border-teal-300' },
}
const GRADE: Record<string, string> = {
  A: 'bg-green-100 text-green-800 border-green-300',
  B: 'bg-blue-100 text-blue-800 border-blue-300',
  C: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  D: 'bg-orange-100 text-orange-800 border-orange-300',
  F: 'bg-red-100 text-red-800 border-red-300',
}
const TIME_FILTERS = [
  { label: 'All Time', hours: null as number | null },
  { label: 'Last Hour', hours: 1 },
  { label: '6 Hours', hours: 6 },
  { label: '24 Hours', hours: 24 },
  { label: 'This Week', hours: 168 },
]
const SORT_OPTIONS = [
  { label: 'Newest First', value: 'newest' },
  { label: 'Best Score', value: 'score' },
  { label: 'Company A-Z', value: 'company' },
]

function srcStyle(name: string) { return SRC[name.toLowerCase()] || { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' } }
function timeAgo(d: string) { const s = Math.floor((Date.now() - new Date(d).getTime()) / 1000); return s < 60 ? 'just now' : s < 3600 ? `${Math.floor(s/60)}m ago` : s < 86400 ? `${Math.floor(s/3600)}h ago` : `${Math.floor(s/86400)}d ago` }

// ─── Component ───────────────────────────────────────────
export default function JobFeed() {
  const [jobs, setJobs] = useState<FeedJob[]>([])
  const [total, setTotal] = useState(0)
  const [sources, setSources] = useState<SourceCount[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filters
  const [activeSource, setActiveSource] = useState('all')
  const [activeHours, setActiveHours] = useState<number | null>(null)
  const [sortBy, setSortBy] = useState('newest')
  const [sortOpen, setSortOpen] = useState(false)
  const [searchInput, setSearchInput] = useState('')
  const [keyword, setKeyword] = useState('')

  // Tracking
  const [tracked, setTracked] = useState<Record<string, string>>({})

  // Pipeline modal
  const [pipelineUrl, setPipelineUrl] = useState<string | null>(null)
  const [pipelineData, setPipelineData] = useState<any>(null)
  const [pipelineLoading, setPipelineLoading] = useState(false)

  // ─── API calls ─────────────────────────────────────────
  const fetchFeed = useCallback(async () => {
    setLoading(true); setError(null)
    try {
      const p = new URLSearchParams()
      if (activeSource !== 'all') p.set('source', activeSource)
      if (activeHours !== null) p.set('hours', String(activeHours))
      if (keyword) p.set('keyword', keyword)
      p.set('sort_by', sortBy)
      const res = await fetch(`http://localhost:8000/api/jobs/feed?${p}`)
      if (!res.ok) throw new Error(`API ${res.status}`)
      const data: FeedResponse = await res.json()
      setJobs(data.jobs ?? []); setTotal(data.total ?? 0); setSources(data.sources ?? [])
    } catch (e: any) { setError(e.message) } finally { setLoading(false) }
  }, [activeSource, activeHours, sortBy, keyword])

  useEffect(() => { fetchFeed() }, [fetchFeed])

  const trackJob = async (url: string, status: string) => {
    setTracked(p => ({ ...p, [url]: status }))
    fetch('http://localhost:8000/api/jobs/track', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_url: url, status }) }).catch(() => {})
  }

  const runPipeline = async (url: string) => {
    setPipelineUrl(url); setPipelineLoading(true); setPipelineData(null)
    try {
      const res = await fetch('http://localhost:8000/api/jobs/auto-apply-pipeline', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ job_url: url, auto_generate_resume: true }) })
      const d = await res.json()
      setPipelineData(d.success ? d : { error: d.detail || 'Failed' })
    } catch { setPipelineData({ error: 'Connection failed' }) } finally { setPipelineLoading(false) }
  }

  const exportExcel = async () => {
    const p = new URLSearchParams()
    if (activeSource !== 'all') p.set('source', activeSource)
    const res = await fetch(`http://localhost:8000/api/jobs/export-feed?${p}`)
    if (!res.ok) return
    const blob = await res.blob()
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
    a.download = `jobs_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a); a.click(); a.remove()
  }

  const doSearch = () => { setKeyword(searchInput); }

  // Source tabs
  const tabs = [{ label: 'All', key: 'all', count: total }, ...sources.map(s => ({ label: s.name, key: s.name.toLowerCase(), count: s.count }))]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* ═══ HEADER ═══ */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-900 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Rss className="w-6 h-6 text-indigo-600" />
                Job Feed
              </h1>
              <p className="text-sm text-gray-500">All jobs from all sources in one place</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={exportExcel} className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors">
              <Download className="w-4 h-4" /> Export Excel
            </button>
            <button onClick={fetchFeed} disabled={loading} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />} Refresh
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* ═══ SEARCH BAR ═══ */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 mb-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input type="text" value={searchInput} onChange={e => setSearchInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && doSearch()}
                placeholder="Search by job title or company (e.g. Software Developer, India...)"
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" />
            </div>
            <button onClick={doSearch} className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors">
              Search
            </button>
            {keyword && (
              <button onClick={() => { setKeyword(''); setSearchInput('') }} className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm text-gray-600 hover:bg-gray-50">
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* ═══ STATS ROW ═══ */}
        <div className="flex flex-wrap items-center gap-3 mb-5">
          <div className="flex items-center gap-2 bg-white border border-gray-200 rounded-lg px-4 py-2.5 shadow-sm">
            <BarChart3 className="w-4 h-4 text-indigo-600" />
            <span className="text-sm"><strong className="text-gray-900">{total}</strong> <span className="text-gray-500">total jobs</span></span>
          </div>
          {sources.map(s => {
            const c = srcStyle(s.name)
            return (
              <span key={s.name} className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}>
                {s.name}: {s.count}
              </span>
            )
          })}
        </div>

        {/* ═══ SOURCE TABS ═══ */}
        <div className="flex flex-wrap gap-2 mb-4">
          {tabs.map(t => (
            <button key={t.key} onClick={() => setActiveSource(t.key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                activeSource === t.key
                  ? 'bg-indigo-600 border-indigo-600 text-white shadow-sm'
                  : 'bg-white border-gray-200 text-gray-700 hover:border-indigo-300 hover:text-indigo-700'
              }`}>
              {t.label} <span className="ml-1 opacity-70">({t.count})</span>
            </button>
          ))}
        </div>

        {/* ═══ TIME FILTERS + SORT ═══ */}
        <div className="flex flex-wrap items-center gap-4 mb-6">
          <div className="flex bg-white border border-gray-200 rounded-lg p-1 shadow-sm">
            {TIME_FILTERS.map(tf => (
              <button key={tf.label} onClick={() => setActiveHours(tf.hours)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  activeHours === tf.hours ? 'bg-indigo-600 text-white shadow-sm' : 'text-gray-600 hover:bg-gray-100'
                }`}>
                {tf.label}
              </button>
            ))}
          </div>
          <div className="relative">
            <button onClick={() => setSortOpen(!sortOpen)}
              className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-gray-400 shadow-sm">
              <ArrowUpDown className="w-3.5 h-3.5" />
              {SORT_OPTIONS.find(o => o.value === sortBy)?.label}
              <ChevronDown className="w-3.5 h-3.5" />
            </button>
            {sortOpen && (
              <div className="absolute z-20 mt-1 w-44 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
                {SORT_OPTIONS.map(o => (
                  <button key={o.value} onClick={() => { setSortBy(o.value); setSortOpen(false) }}
                    className={`w-full text-left px-4 py-2.5 text-sm ${sortBy === o.value ? 'bg-indigo-50 text-indigo-700 font-medium' : 'text-gray-700 hover:bg-gray-50'}`}>
                    {o.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ═══ JOB LIST ═══ */}
        {loading ? (
          <div className="flex flex-col items-center py-24">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-3" />
            <p className="text-gray-500">Loading jobs...</p>
          </div>
        ) : error ? (
          <div className="text-center py-24">
            <p className="text-red-600 font-medium mb-1">Failed to load feed</p>
            <p className="text-gray-500 text-sm">{error}</p>
            <button onClick={fetchFeed} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm">Retry</button>
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-24">
            <Rss className="w-12 h-12 mx-auto text-gray-300 mb-4" />
            <p className="text-lg font-semibold text-gray-600">No jobs found</p>
            <p className="text-sm text-gray-400 mt-1">Try different filters or run a portal scan.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {jobs.map(job => {
              const s = srcStyle(job.source)
              const status = tracked[job.job_url]
              return (
                <div key={job.job_url}
                  className={`bg-white rounded-xl border shadow-sm p-5 transition-all hover:shadow-md ${
                    status === 'applied' ? 'border-green-300 bg-green-50/30' :
                    status === 'ignored' ? 'border-gray-200 opacity-50' :
                    status === 'saved' ? 'border-indigo-300 bg-indigo-50/20' :
                    'border-gray-200'
                  }`}>
                  <div className="flex items-start gap-4">
                    {/* Left: Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className={`px-2.5 py-0.5 rounded text-xs font-bold border ${s.bg} ${s.text} ${s.border}`}>
                          {job.source.toUpperCase()}
                        </span>
                        {job.evaluation_grade && (
                          <span className={`px-2 py-0.5 rounded text-xs font-bold border ${GRADE[job.evaluation_grade] || ''}`}>
                            Grade {job.evaluation_grade} {job.evaluation_score != null && `(${Math.round(job.evaluation_score)}%)`}
                          </span>
                        )}
                        {(status === 'applied' || job.applied) && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-700 border border-green-300">
                            <CheckCircle className="w-3 h-3" /> Applied
                          </span>
                        )}
                        {status === 'saved' && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold bg-indigo-100 text-indigo-700 border border-indigo-300">
                            <Bookmark className="w-3 h-3" /> Saved
                          </span>
                        )}
                      </div>
                      <h3 className="text-base font-bold text-gray-900 leading-snug">{job.title}</h3>
                      <p className="text-sm text-gray-600 mt-0.5">{job.company}</p>
                      <p className="text-xs text-gray-400 mt-1.5 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {timeAgo(job.first_seen_at)}
                      </p>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex flex-col gap-1.5 shrink-0">
                      <a href={job.job_url} target="_blank" rel="noopener noreferrer"
                        className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-medium transition-colors">
                        <ExternalLink className="w-3.5 h-3.5" /> View Job
                      </a>
                      <button onClick={() => runPipeline(job.job_url)}
                        className="flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-medium transition-colors">
                        <Wand2 className="w-3.5 h-3.5" /> Auto Resume
                      </button>
                      <div className="flex gap-1">
                        <button onClick={() => trackJob(job.job_url, 'applied')} title="Mark Applied"
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg text-xs font-medium transition-colors border border-green-200">
                          <CheckCircle className="w-3 h-3" />
                        </button>
                        <button onClick={() => trackJob(job.job_url, 'saved')} title="Save"
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-lg text-xs font-medium transition-colors border border-indigo-200">
                          <Bookmark className="w-3 h-3" />
                        </button>
                        <button onClick={() => trackJob(job.job_url, 'ignored')} title="Ignore"
                          className="flex-1 flex items-center justify-center gap-1 px-2 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-500 rounded-lg text-xs font-medium transition-colors border border-gray-200">
                          <ThumbsDown className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </main>

      {/* ═══ PIPELINE MODAL ═══ */}
      {pipelineUrl && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Auto-Apply Pipeline</h2>
              <button onClick={() => { setPipelineUrl(null); setPipelineData(null) }} className="p-2 hover:bg-gray-100 rounded-lg"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6">
              {pipelineLoading ? (
                <div className="text-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mx-auto mb-3" />
                  <p className="text-gray-600">Analyzing JD and generating tailored resume...</p>
                </div>
              ) : pipelineData?.error ? (
                <div className="text-center py-8">
                  <p className="text-red-600 font-medium">{pipelineData.error}</p>
                </div>
              ) : pipelineData ? (
                <div className="space-y-6">
                  {/* Job Info */}
                  <div>
                    <h3 className="font-semibold text-gray-900 text-lg">{pipelineData.job?.title}</h3>
                    <p className="text-gray-600">{pipelineData.job?.company}</p>
                  </div>

                  {/* ATS Score */}
                  <div className="flex items-center gap-4 bg-gray-50 rounded-xl p-4">
                    <div className={`text-3xl font-bold ${pipelineData.analysis?.ats_score >= 70 ? 'text-green-600' : pipelineData.analysis?.ats_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {pipelineData.analysis?.ats_score}%
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">ATS Match Score</p>
                      <p className="text-sm text-gray-500">{pipelineData.analysis?.keywords_found} keywords found, {pipelineData.analysis?.coverage_percent}% coverage</p>
                    </div>
                  </div>

                  {/* Skills */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-semibold text-green-700 mb-2">Matched Skills ({pipelineData.analysis?.matched_skills?.length})</p>
                      <div className="flex flex-wrap gap-1">
                        {pipelineData.analysis?.matched_skills?.map((s: string, i: number) => (
                          <span key={i} className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs">{s}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-red-700 mb-2">Missing Skills ({pipelineData.analysis?.missing_skills?.length})</p>
                      <div className="flex flex-wrap gap-1">
                        {pipelineData.analysis?.missing_skills?.map((s: string, i: number) => (
                          <span key={i} className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">{s}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Resume Download */}
                  {pipelineData.resume?.generated && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                      <p className="font-semibold text-green-800 mb-2">Tailored Resume Generated</p>
                      <div className="flex gap-3">
                        <a href={`http://localhost:8000${pipelineData.resume.download_url}`} target="_blank"
                          className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium">
                          <Download className="w-4 h-4" /> Download Resume
                        </a>
                        <a href={pipelineUrl} target="_blank" rel="noopener noreferrer"
                          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium">
                          <Send className="w-4 h-4" /> Apply Manually
                        </a>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">Download the resume, open the job link, fill in the application form and submit.</p>
                    </div>
                  )}

                  {/* Mark as Applied */}
                  <button onClick={() => { trackJob(pipelineUrl, 'applied'); setPipelineUrl(null); setPipelineData(null) }}
                    className="w-full py-3 bg-gray-700 hover:bg-gray-800 text-white rounded-xl font-medium text-sm">
                    Mark as Applied
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
