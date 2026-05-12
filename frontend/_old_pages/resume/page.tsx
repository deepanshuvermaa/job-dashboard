'use client'

import { useState, useMemo } from 'react'
import {
  ArrowLeft, FileText, Download, Loader2, Wand2, Zap,
  Search, CheckCircle2, XCircle, BarChart3, Target,
  Lightbulb, Clock, Tag, ChevronDown, ChevronUp
} from 'lucide-react'
import Link from 'next/link'

const ARCHETYPES = [
  { id: 'general', name: 'General / Balanced', desc: 'Well-rounded profile' },
  { id: 'full_stack', name: 'Full Stack Developer', desc: 'Frontend + Backend emphasis' },
  { id: 'backend', name: 'Backend Engineer', desc: 'APIs, databases, infrastructure' },
  { id: 'frontend', name: 'Frontend Developer', desc: 'UI/UX, React, styling' },
  { id: 'data', name: 'Data Engineer / Scientist', desc: 'Data pipelines, ML, analytics' },
  { id: 'devops', name: 'DevOps / SRE', desc: 'CI/CD, cloud, infrastructure' },
]

interface JDAnalysis {
  ats_score: number
  keyword_coverage: { matched: number; total: number; percentage: number }
  matched_skills: string[]
  missing_skills: string[]
  keyword_categories: Record<string, string[]>
  suggestions: string[]
  experience_required?: string
}

function AtsScoreRing({ score }: { score: number }) {
  const radius = 54
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  const color = score >= 70 ? '#22c55e' : score >= 50 ? '#eab308' : '#ef4444'
  const bgColor = score >= 70 ? 'text-green-500' : score >= 50 ? 'text-yellow-500' : 'text-red-500'

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="10" />
          <circle
            cx="60" cy="60" r={radius} fill="none"
            stroke={color} strokeWidth="10" strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${bgColor}`}>{score}%</span>
          <span className="text-xs text-gray-600">ATS Score</span>
        </div>
      </div>
    </div>
  )
}

function SkillPill({ skill, variant }: { skill: string; variant: 'matched' | 'missing' }) {
  const styles = variant === 'matched'
    ? 'bg-green-500/15 text-green-400 border-green-500/30'
    : 'bg-orange-500/15 text-orange-400 border-orange-500/30'
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${styles}`}>
      {variant === 'matched' ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
      {skill}
    </span>
  )
}

function ProgressBar({ percentage, label }: { percentage: number; label: string }) {
  const color = percentage >= 70 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="text-gray-600">{percentage}%</span>
      </div>
      <div className="h-2.5 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

export default function ResumeGenerator() {
  const [jobUrl, setJobUrl] = useState('')
  const [archetype, setArchetype] = useState('general')
  const [format, setFormat] = useState('Letter')
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState<{ pdf_path?: string; keywords?: string[] } | null>(null)
  const [error, setError] = useState('')

  // JD Analysis state
  const [jobDescription, setJobDescription] = useState('')
  const [userSkillsInput, setUserSkillsInput] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<JDAnalysis | null>(null)
  const [analysisError, setAnalysisError] = useState('')
  const [showCategories, setShowCategories] = useState(false)

  // Auto-load user skills from uploaded resume profile
  useState(() => {
    fetch('http://localhost:8000/api/profile/get')
      .then(r => r.json())
      .then(data => {
        const skills = data?.profile?.skills || data?.skills || []
        if (skills.length > 0 && !userSkillsInput) {
          setUserSkillsInput(skills.join(', '))
        }
      })
      .catch(() => {})
  })

  const userSkillsList = useMemo(() =>
    userSkillsInput.split(',').map(s => s.trim()).filter(Boolean),
    [userSkillsInput]
  )

  const keywordsToInject = useMemo(() => {
    if (!analysis) return []
    return [...analysis.matched_skills, ...analysis.missing_skills]
  }, [analysis])

  const analyzeJD = async () => {
    if (!jobDescription.trim()) {
      setAnalysisError('Please paste a job description')
      return
    }
    setAnalyzing(true)
    setAnalysisError('')
    setAnalysis(null)

    try {
      const res = await fetch('http://localhost:8000/api/resume/analyze-jd', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          user_skills: userSkillsList.length > 0 ? userSkillsList : undefined,
        }),
      })

      const data = await res.json()
      if (res.ok) {
        setAnalysis(data)
      } else {
        setAnalysisError(data.detail || 'Failed to analyze job description')
      }
    } catch {
      setAnalysisError('Failed to connect to backend')
    } finally {
      setAnalyzing(false)
    }
  }

  const generateResume = async () => {
    if (!jobUrl.trim()) {
      setError('Please enter a job URL')
      return
    }
    setGenerating(true)
    setError('')
    setResult(null)

    try {
      const body: Record<string, unknown> = {
        job_url: jobUrl || undefined,
        job_description: jobDescription || undefined,
        archetype: archetype,
        format: format,
      }
      if (analysis && keywordsToInject.length > 0) {
        body.inject_keywords = keywordsToInject
      }

      const res = await fetch('http://localhost:8000/api/resume/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await res.json()
      if (data.success) {
        setResult(data)
      } else {
        setError(data.detail || 'Failed to generate resume')
      }
    } catch {
      setError('Failed to connect to backend')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 -mx-6 -mt-6 mb-8 px-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold">ATS Resume Generator</h1>
            <p className="text-gray-600 text-sm">Generate tailored, ATS-optimized resumes for specific jobs</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Configuration */}
        <div className="space-y-6">
          {/* Job URL */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Target Job</h2>
            <input
              type="text"
              placeholder="Paste job URL (LinkedIn, Greenhouse, Lever, etc.)"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
              className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* JD Analysis Panel */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <div className="flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-purple-400" />
              <h2 className="text-lg font-semibold">JD Analysis</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-600 mb-1.5 block">Job Description</label>
                <textarea
                  placeholder="Paste the full job description text here for keyword analysis..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={6}
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-purple-500 resize-y text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-gray-600 mb-1.5 block">Your Skills (comma-separated)</label>
                <input
                  type="text"
                  placeholder="Python, React, TypeScript, AWS, Docker..."
                  value={userSkillsInput}
                  onChange={(e) => setUserSkillsInput(e.target.value)}
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-purple-500 text-sm"
                />
                {userSkillsList.length > 0 && (
                  <p className="text-xs text-gray-500 mt-1">{userSkillsList.length} skill(s) entered</p>
                )}
              </div>

              <button
                onClick={analyzeJD}
                disabled={analyzing}
                className="w-full flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-500 text-white px-4 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    Analyze JD
                  </>
                )}
              </button>

              {analysisError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                  {analysisError}
                </div>
              )}
            </div>
          </div>

          {/* Archetype Selection */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Resume Archetype</h2>
            <div className="grid grid-cols-2 gap-2">
              {ARCHETYPES.map(arch => (
                <button
                  key={arch.id}
                  onClick={() => setArchetype(arch.id)}
                  className={`p-3 rounded-lg border text-left transition-all ${
                    archetype === arch.id
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-300 bg-gray-100 hover:border-gray-400'
                  }`}
                >
                  <div className="font-medium text-sm">{arch.name}</div>
                  <div className="text-xs text-gray-600">{arch.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Format */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4">Page Format</h2>
            <div className="flex gap-3">
              {['Letter', 'A4'].map(fmt => (
                <button
                  key={fmt}
                  onClick={() => setFormat(fmt)}
                  className={`px-6 py-2 rounded-lg border transition-all ${
                    format === fmt
                      ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                      : 'border-gray-300 bg-gray-100 hover:border-gray-400'
                  }`}
                >
                  {fmt}
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateResume}
            disabled={generating}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-4 rounded-xl font-semibold text-lg hover:opacity-90 disabled:opacity-50"
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating Resume...
              </>
            ) : (
              <>
                <Wand2 className="w-5 h-5" />
                Generate Tailored Resume
                {analysis && keywordsToInject.length > 0 && (
                  <span className="ml-2 px-2 py-0.5 bg-white/20 rounded-full text-xs">
                    {keywordsToInject.length} keywords to inject
                  </span>
                )}
              </>
            )}
          </button>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Right: Analysis Results + Generation Results */}
        <div className="space-y-6">
          {/* Analysis Results */}
          {analysis && (
            <div className="space-y-4">
              {/* ATS Score + Keyword Coverage */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <div className="flex items-center gap-2 mb-5">
                  <Target className="w-5 h-5 text-purple-400" />
                  <h2 className="text-lg font-semibold">Analysis Results</h2>
                </div>

                <div className="flex items-start gap-6">
                  <AtsScoreRing score={analysis.ats_score} />
                  <div className="flex-1 space-y-4 pt-2">
                    <ProgressBar
                      percentage={analysis.keyword_coverage.percentage}
                      label={`Keyword Coverage (${analysis.keyword_coverage.matched}/${analysis.keyword_coverage.total})`}
                    />
                    {analysis.experience_required && (
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-yellow-400" />
                        <span className="text-gray-700">
                          Requires <span className="text-yellow-400 font-medium">{analysis.experience_required}</span>
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Matched Skills */}
              {analysis.matched_skills.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <h3 className="text-sm font-semibold text-gray-700">Matched Skills ({analysis.matched_skills.length})</h3>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.matched_skills.map((skill, i) => (
                      <SkillPill key={i} skill={skill} variant="matched" />
                    ))}
                  </div>
                </div>
              )}

              {/* Missing Skills */}
              {analysis.missing_skills.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <XCircle className="w-4 h-4 text-orange-400" />
                    <h3 className="text-sm font-semibold text-gray-700">Missing Skills ({analysis.missing_skills.length})</h3>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.missing_skills.map((skill, i) => (
                      <SkillPill key={i} skill={skill} variant="missing" />
                    ))}
                  </div>
                </div>
              )}

              {/* Keyword Categories */}
              {Object.keys(analysis.keyword_categories).length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <button
                    onClick={() => setShowCategories(!showCategories)}
                    className="flex items-center justify-between w-full"
                  >
                    <div className="flex items-center gap-2">
                      <Tag className="w-4 h-4 text-blue-400" />
                      <h3 className="text-sm font-semibold text-gray-700">
                        Keyword Categories ({Object.keys(analysis.keyword_categories).length})
                      </h3>

                    </div>
                    {showCategories ? (
                      <ChevronUp className="w-4 h-4 text-gray-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-gray-500" />
                    )}
                  </button>

                  {showCategories && (
                    <div className="mt-4 space-y-3">
                      {Object.entries(analysis.keyword_categories).map(([category, keywords]) => (
                        <div key={category}>
                          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1.5">{category}</p>
                          <div className="flex flex-wrap gap-1">
                            {keywords.map((kw, i) => (
                              <span
                                key={i}
                                className={`px-2 py-0.5 rounded text-xs ${
                                  analysis.matched_skills.includes(kw)
                                    ? 'bg-green-500/15 text-green-400'
                                    : 'bg-gray-100 text-gray-600'
                                }`}
                              >
                                {kw}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Improvement Suggestions */}
              {analysis.suggestions.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                    <h3 className="text-sm font-semibold text-gray-700">Improvement Suggestions</h3>
                  </div>
                  <ul className="space-y-2">
                    {analysis.suggestions.map((suggestion, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <span className="text-yellow-500 mt-0.5 shrink-0">&#8226;</span>
                        {suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Resume Generation Result */}
          {result ? (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 space-y-4">
              <div className="flex items-center gap-2 text-green-400">
                <FileText className="w-5 h-5" />
                <h2 className="text-lg font-semibold">Resume Generated!</h2>
              </div>

              {/* Keywords */}
              {result.keywords && result.keywords.length > 0 && (
                <div>
                  <h3 className="text-sm text-gray-600 mb-2">Injected Keywords ({result.keywords.length})</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {result.keywords.map((kw, i) => (
                      <span key={i} className="px-2 py-1 bg-blue-500/10 text-blue-300 rounded text-xs">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Download */}
              {result.pdf_path && (() => {
                const filename = result.pdf_path.replace(/\\/g, '/').split('/').pop()
                return (
                  <div className="space-y-3 pt-4">
                    <a
                      href={`http://localhost:8000/api/resume/download/${filename}`}
                      target="_blank"
                      className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-3 rounded-lg font-medium hover:bg-green-500"
                    >
                      <Download className="w-4 h-4" />
                      Download PDF
                    </a>
                    <p className="text-xs text-gray-500 text-center">
                      File: {filename}
                    </p>
                  </div>
                )
              })()}
            </div>
          ) : !analysis ? (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-12 text-center">
              <Zap className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-semibold text-gray-500 mb-2">No Resume Generated Yet</h3>
              <p className="text-gray-600 text-sm">
                Enter a job URL, select an archetype, and click Generate.
                <br />
                Optionally, paste a JD to analyze keywords first.
              </p>
            </div>
          ) : null}

          {/* Resume Comparison — shown after both analysis and generation */}
          {analysis && result && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <div className="flex items-center gap-2 mb-5">
                <BarChart3 className="w-5 h-5 text-blue-400" />
                <h2 className="text-lg font-semibold">Skills vs JD Requirements</h2>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2 text-center">Your Skills</p>
                  <div className="bg-gray-100 rounded-lg p-3 min-h-[80px]">
                    <div className="flex flex-wrap gap-1">
                      {analysis.matched_skills.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 bg-green-500/15 text-green-400 rounded text-xs">{s}</span>
                      ))}
                    </div>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-2 text-center">JD Requirements</p>
                  <div className="bg-gray-100 rounded-lg p-3 min-h-[80px]">
                    <div className="flex flex-wrap gap-1">
                      {[...analysis.matched_skills, ...analysis.missing_skills].map((s, i) => (
                        <span
                          key={i}
                          className={`px-2 py-0.5 rounded text-xs ${
                            analysis.matched_skills.includes(s)
                              ? 'bg-green-500/15 text-green-400'
                              : 'bg-orange-500/15 text-orange-400'
                          }`}
                        >
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Per-category overlap bars */}
              {Object.keys(analysis.keyword_categories).length > 0 && (
                <div className="space-y-3">
                  <p className="text-xs text-gray-500 uppercase tracking-wide">Overlap per Category</p>
                  {Object.entries(analysis.keyword_categories).map(([category, keywords]) => {
                    const matched = keywords.filter(k => analysis.matched_skills.includes(k)).length
                    const pct = keywords.length > 0 ? Math.round((matched / keywords.length) * 100) : 0
                    return (
                      <div key={category}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-600">{category}</span>
                          <span className="text-gray-500">{matched}/{keywords.length}</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              pct >= 70 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
