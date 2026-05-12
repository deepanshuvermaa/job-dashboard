'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  MessageCircle,
  Bookmark,
  Search,
  Target,
  Clock,
  Copy,
  ExternalLink,
  Trash2,
  Loader2,
  Check,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GroupMessageResult {
  steps: string[]
  recommended_groups: string[]
  sample_message: string
}

interface SavedSearch {
  id: string
  name: string
  url: string
  keywords: string
  notes: string
  created_at: string
}

interface GoogleDorkResult {
  queries: string[]
  tip: string
}

interface RecruiterEngageResult {
  action: string
  steps: string[]
  sample_comments: string[]
  sample_posts: string[]
  tips: string[]
}

interface JobFreshnessResult {
  how_it_works: string[]
  for_job_seekers: string[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const API = 'http://localhost:8000/api/hacks'

const colorMap: Record<number, string> = {
  0: 'blue',
  1: 'green',
  2: 'purple',
  3: 'orange',
  4: 'yellow',
}

function badgeColor(color: string) {
  const map: Record<string, string> = {
    blue: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    green: 'bg-green-500/20 text-green-400 border-green-500/30',
    purple: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    orange: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  }
  return map[color] ?? map.blue
}

function iconColor(color: string) {
  const map: Record<string, string> = {
    blue: 'text-blue-500',
    green: 'text-green-500',
    purple: 'text-purple-500',
    orange: 'text-orange-500',
    yellow: 'text-yellow-500',
  }
  return map[color] ?? map.blue
}

function borderColor(color: string) {
  const map: Record<string, string> = {
    blue: 'border-blue-500/30',
    green: 'border-green-500/30',
    purple: 'border-purple-500/30',
    orange: 'border-orange-500/30',
    yellow: 'border-yellow-500/30',
  }
  return map[color] ?? map.blue
}

function btnColor(color: string) {
  const map: Record<string, string> = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    green: 'bg-green-600 hover:bg-green-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    orange: 'bg-orange-600 hover:bg-orange-700',
    yellow: 'bg-yellow-600 hover:bg-yellow-700',
  }
  return map[color] ?? map.blue
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function HacksPage() {
  const [expandedCard, setExpandedCard] = useState<number | null>(null)

  // Tool 1 state
  const [gmTargetName, setGmTargetName] = useState('')
  const [gmMessage, setGmMessage] = useState('')
  const [gmResult, setGmResult] = useState<GroupMessageResult | null>(null)
  const [gmLoading, setGmLoading] = useState(false)

  // Tool 2 state
  const [ssName, setSsName] = useState('')
  const [ssUrl, setSsUrl] = useState('')
  const [ssKeywords, setSsKeywords] = useState('')
  const [ssNotes, setSsNotes] = useState('')
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [ssLoading, setSsLoading] = useState(false)
  const [ssListLoading, setSsListLoading] = useState(false)

  // Tool 3 state
  const [gdCompany, setGdCompany] = useState('')
  const [gdTitle, setGdTitle] = useState('')
  const [gdLocation, setGdLocation] = useState('')
  const [gdResult, setGdResult] = useState<GoogleDorkResult | null>(null)
  const [gdLoading, setGdLoading] = useState(false)
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null)

  // Tool 4 state
  const [reUrl, setReUrl] = useState('')
  const [reStrategy, setReStrategy] = useState<'comment' | 'tag' | 'share'>('comment')
  const [reResult, setReResult] = useState<RecruiterEngageResult | null>(null)
  const [reLoading, setReLoading] = useState(false)

  // Tool 5 state
  const [jfResult, setJfResult] = useState<JobFreshnessResult | null>(null)
  const [jfLoading, setJfLoading] = useState(false)

  // ------- Fetch saved searches when Tool 2 is expanded -------
  const fetchSavedSearches = useCallback(async () => {
    setSsListLoading(true)
    try {
      const res = await fetch(`${API}/saved-searches`)
      if (res.ok) {
        const data = await res.json()
        setSavedSearches(Array.isArray(data) ? data : data.searches ?? [])
      }
    } catch (err) {
      console.error('Failed to load saved searches', err)
    } finally {
      setSsListLoading(false)
    }
  }, [])

  // ------- Auto-load data when a card is expanded -------
  useEffect(() => {
    if (expandedCard === 1) fetchSavedSearches()
    if (expandedCard === 4) loadJobFreshness()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [expandedCard])

  // ------- Tool 1: Group Message -------
  const handleGroupMessage = async () => {
    if (!gmTargetName.trim()) return
    setGmLoading(true)
    try {
      const res = await fetch(`${API}/group-message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_name: gmTargetName, message: gmMessage }),
      })
      if (res.ok) setGmResult(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setGmLoading(false)
    }
  }

  // ------- Tool 2: Save Search -------
  const handleSaveSearch = async () => {
    if (!ssName.trim() || !ssUrl.trim()) return
    setSsLoading(true)
    try {
      const res = await fetch(`${API}/saved-searches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: ssName, url: ssUrl, keywords: ssKeywords, notes: ssNotes }),
      })
      if (res.ok) {
        setSsName('')
        setSsUrl('')
        setSsKeywords('')
        setSsNotes('')
        fetchSavedSearches()
      }
    } catch (err) {
      console.error(err)
    } finally {
      setSsLoading(false)
    }
  }

  const handleDeleteSearch = async (id: string) => {
    try {
      await fetch(`${API}/saved-searches/${id}`, { method: 'DELETE' })
      setSavedSearches((prev) => prev.filter((s) => s.id !== id))
    } catch (err) {
      console.error(err)
    }
  }

  // ------- Tool 3: Google Dork -------
  const handleGoogleDork = async () => {
    if (!gdCompany.trim() && !gdTitle.trim()) return
    setGdLoading(true)
    try {
      const res = await fetch(`${API}/google-dork`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: gdCompany, job_title: gdTitle, location: gdLocation }),
      })
      if (res.ok) setGdResult(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setGdLoading(false)
    }
  }

  const copyToClipboard = (text: string, idx: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIdx(idx)
    setTimeout(() => setCopiedIdx(null), 1500)
  }

  // ------- Tool 4: Recruiter Engage -------
  const handleRecruiterEngage = async () => {
    if (!reUrl.trim()) return
    setReLoading(true)
    try {
      const res = await fetch(`${API}/recruiter-engage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recruiter_url: reUrl, strategy: reStrategy }),
      })
      if (res.ok) setReResult(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setReLoading(false)
    }
  }

  // ------- Tool 5: Job Freshness -------
  const loadJobFreshness = async () => {
    if (jfResult) return
    setJfLoading(true)
    try {
      const res = await fetch(`${API}/refresh-job-post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      })
      if (res.ok) setJfResult(await res.json())
    } catch (err) {
      console.error(err)
    } finally {
      setJfLoading(false)
    }
  }

  // ------- Card definitions -------
  const cards = [
    {
      title: 'Group Message Hack',
      subtitle: 'Message Non-Connections',
      description: 'Message anyone via shared LinkedIn Groups — no InMail needed',
      icon: MessageCircle,
    },
    {
      title: 'Saved Search Bank',
      subtitle: 'Unlimited Alerts',
      description: 'Save unlimited LinkedIn search URLs — bypass the alert limit',
      icon: Bookmark,
    },
    {
      title: 'Google Dork Profile Finder',
      subtitle: 'Hidden Profiles',
      description: 'Find hidden LinkedIn profiles using Google search operators',
      icon: Search,
    },
    {
      title: 'Recruiter Engagement Planner',
      subtitle: 'Get Noticed',
      description: 'Get noticed by recruiters without cold DMs',
      icon: Target,
    },
    {
      title: 'Job Freshness Hack',
      subtitle: '86400',
      description: 'Apply to the freshest job posts for 3x higher response rate',
      icon: Clock,
    },
  ]

  const toggle = (idx: number) => setExpandedCard(expandedCard === idx ? null : idx)

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------

  const inputClass =
    'w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition'

  const renderExpanded = (idx: number) => {
    const color = colorMap[idx]

    // ---- Tool 1 ----
    if (idx === 0) {
      return (
        <div className="space-y-4 pt-4">
          <input
            className={inputClass}
            placeholder="Target person name"
            value={gmTargetName}
            onChange={(e) => setGmTargetName(e.target.value)}
          />
          <textarea
            className={`${inputClass} min-h-[80px] resize-y`}
            placeholder="Custom message (optional)"
            value={gmMessage}
            onChange={(e) => setGmMessage(e.target.value)}
          />
          <button
            onClick={handleGroupMessage}
            disabled={gmLoading || !gmTargetName.trim()}
            className={`${btnColor(color)} text-white px-5 py-2.5 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 transition`}
          >
            {gmLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            Generate Strategy
          </button>

          {gmResult && (
            <div className="space-y-4 mt-2">
              <div>
                <h4 className="text-sm font-semibold text-gray-300 mb-2">Steps</h4>
                <ol className="list-decimal list-inside space-y-1 text-sm text-gray-400">
                  {gmResult.steps?.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ol>
              </div>
              {gmResult.recommended_groups?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Recommended Groups</h4>
                  <div className="flex flex-wrap gap-2">
                    {gmResult.recommended_groups.map((g, i) => (
                      <span
                        key={i}
                        className={`text-xs px-3 py-1 rounded-full border ${badgeColor(color)}`}
                      >
                        {g}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {gmResult.sample_message && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Sample Message</h4>
                  <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap">
                    {gmResult.sample_message}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )
    }

    // ---- Tool 2 ----
    if (idx === 1) {
      return (
        <div className="space-y-4 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <input
              className={inputClass}
              placeholder="Search Name"
              value={ssName}
              onChange={(e) => setSsName(e.target.value)}
            />
            <input
              className={inputClass}
              placeholder="Search URL"
              value={ssUrl}
              onChange={(e) => setSsUrl(e.target.value)}
            />
            <input
              className={inputClass}
              placeholder="Keywords"
              value={ssKeywords}
              onChange={(e) => setSsKeywords(e.target.value)}
            />
            <input
              className={inputClass}
              placeholder="Notes"
              value={ssNotes}
              onChange={(e) => setSsNotes(e.target.value)}
            />
          </div>
          <button
            onClick={handleSaveSearch}
            disabled={ssLoading || !ssName.trim() || !ssUrl.trim()}
            className={`${btnColor(color)} text-white px-5 py-2.5 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 transition`}
          >
            {ssLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            Save Search
          </button>

          {/* Saved searches list */}
          <div className="mt-2">
            <h4 className="text-sm font-semibold text-gray-300 mb-3">Saved Searches</h4>
            {ssListLoading ? (
              <div className="flex items-center gap-2 text-gray-500 text-sm">
                <Loader2 className="w-4 h-4 animate-spin" /> Loading...
              </div>
            ) : savedSearches.length === 0 ? (
              <p className="text-sm text-gray-500">No saved searches yet.</p>
            ) : (
              <div className="space-y-2">
                {savedSearches.map((s) => (
                  <div
                    key={s.id}
                    className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 flex items-start justify-between gap-3"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-white truncate">{s.name}</p>
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-green-400 hover:underline truncate block"
                      >
                        {s.url}
                      </a>
                      {s.keywords && (
                        <p className="text-xs text-gray-500 mt-1">Keywords: {s.keywords}</p>
                      )}
                      {s.created_at && (
                        <p className="text-xs text-gray-600 mt-0.5">
                          {new Date(s.created_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleDeleteSearch(s.id)}
                      className="text-gray-500 hover:text-red-400 transition p-1"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )
    }

    // ---- Tool 3 ----
    if (idx === 2) {
      return (
        <div className="space-y-4 pt-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <input
              className={inputClass}
              placeholder="Company"
              value={gdCompany}
              onChange={(e) => setGdCompany(e.target.value)}
            />
            <input
              className={inputClass}
              placeholder="Job Title"
              value={gdTitle}
              onChange={(e) => setGdTitle(e.target.value)}
            />
            <input
              className={inputClass}
              placeholder="Location"
              value={gdLocation}
              onChange={(e) => setGdLocation(e.target.value)}
            />
          </div>
          <button
            onClick={handleGoogleDork}
            disabled={gdLoading || (!gdCompany.trim() && !gdTitle.trim())}
            className={`${btnColor(color)} text-white px-5 py-2.5 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 transition`}
          >
            {gdLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            Generate Queries
          </button>

          {gdResult && (
            <div className="space-y-3 mt-2">
              {gdResult.queries?.map((q, i) => (
                <div
                  key={i}
                  className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 flex items-center justify-between gap-2"
                >
                  <code className="text-sm text-purple-300 break-all flex-1">{q}</code>
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => copyToClipboard(q, i)}
                      className="text-gray-400 hover:text-white transition p-1.5"
                      title="Copy"
                    >
                      {copiedIdx === i ? (
                        <Check className="w-4 h-4 text-green-400" />
                      ) : (
                        <Copy className="w-4 h-4" />
                      )}
                    </button>
                    <a
                      href={`https://www.google.com/search?q=${encodeURIComponent(q)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition p-1.5"
                      title="Open in Google"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
              {gdResult.tip && (
                <p className="text-xs text-gray-500 italic mt-2">Tip: {gdResult.tip}</p>
              )}
            </div>
          )}
        </div>
      )
    }

    // ---- Tool 4 ----
    if (idx === 3) {
      return (
        <div className="space-y-4 pt-4">
          <input
            className={inputClass}
            placeholder="Recruiter Profile URL"
            value={reUrl}
            onChange={(e) => setReUrl(e.target.value)}
          />
          <div className="flex items-center gap-4">
            {(['comment', 'tag', 'share'] as const).map((opt) => (
              <label
                key={opt}
                className={`flex items-center gap-2 cursor-pointer text-sm px-4 py-2 rounded-lg border transition ${
                  reStrategy === opt
                    ? 'border-orange-500 bg-orange-500/10 text-orange-400'
                    : 'border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600'
                }`}
              >
                <input
                  type="radio"
                  name="strategy"
                  value={opt}
                  checked={reStrategy === opt}
                  onChange={() => setReStrategy(opt)}
                  className="sr-only"
                />
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </label>
            ))}
          </div>
          <button
            onClick={handleRecruiterEngage}
            disabled={reLoading || !reUrl.trim()}
            className={`${btnColor(color)} text-white px-5 py-2.5 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 transition`}
          >
            {reLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            Plan Engagement
          </button>

          {reResult && (
            <div className="space-y-4 mt-2">
              {reResult.action && (
                <p className="text-sm text-orange-300 font-medium">{reResult.action}</p>
              )}
              {reResult.steps?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Steps</h4>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-gray-400">
                    {reResult.steps.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ol>
                </div>
              )}
              {reResult.sample_comments?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Sample Comments</h4>
                  {reResult.sample_comments.map((c, i) => (
                    <div
                      key={i}
                      className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 text-sm text-gray-300 mb-2"
                    >
                      {c}
                    </div>
                  ))}
                </div>
              )}
              {reResult.sample_posts?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Sample Posts</h4>
                  {reResult.sample_posts.map((p, i) => (
                    <div
                      key={i}
                      className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 text-sm text-gray-300 mb-2 whitespace-pre-wrap"
                    >
                      {p}
                    </div>
                  ))}
                </div>
              )}
              {reResult.tips?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">General Tips</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                    {reResult.tips.map((t, i) => (
                      <li key={i}>{t}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )
    }

    // ---- Tool 5 ----
    if (idx === 4) {
      return (
        <div className="space-y-4 pt-4">
          <div className="bg-gray-800/60 border border-yellow-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-yellow-400 mb-2">What is the 86400 Hack?</h4>
            <p className="text-sm text-gray-400">
              86,400 is the number of seconds in a day. LinkedIn&apos;s algorithm heavily favours
              applications submitted within the first 24 hours of a job posting. Applying early can
              increase your response rate by up to 3x compared to later applicants.
            </p>
          </div>

          {jfLoading ? (
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading insights...
            </div>
          ) : jfResult ? (
            <div className="space-y-4">
              {jfResult.how_it_works?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">How It Works</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                    {jfResult.how_it_works.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
              {jfResult.for_job_seekers?.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Tips for Job Seekers</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-400">
                    {jfResult.for_job_seekers.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : null}
        </div>
      )
    }

    return null
  }

  // ---------------------------------------------------------------------------
  // Main render
  // ---------------------------------------------------------------------------

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back</span>
        </Link>
        <h1 className="text-3xl font-bold tracking-tight">LinkedIn Hacks &amp; Tricks</h1>
        <p className="text-gray-400 mt-1">
          5 proven strategies to get noticed by recruiters
        </p>
      </div>

      {/* Cards */}
      <div className="max-w-4xl mx-auto space-y-4">
        {cards.map((card, idx) => {
          const color = colorMap[idx]
          const Icon = card.icon
          const isOpen = expandedCard === idx

          return (
            <div
              key={idx}
              className={`bg-gray-900 border rounded-xl transition-all duration-200 ${
                isOpen ? borderColor(color) : 'border-gray-800'
              }`}
            >
              {/* Card header */}
              <button
                onClick={() => toggle(idx)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${badgeColor(color)}`}
                  >
                    <Icon className={`w-5 h-5 ${iconColor(color)}`} />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-white leading-tight">
                      {card.title}{' '}
                      <span className="text-xs font-normal text-gray-500">
                        ({card.subtitle})
                      </span>
                    </h3>
                    <p className="text-sm text-gray-400 mt-0.5">{card.description}</p>
                  </div>
                </div>
                {isOpen ? (
                  <ChevronUp className="w-5 h-5 text-gray-500 shrink-0" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500 shrink-0" />
                )}
              </button>

              {/* Expanded content */}
              {isOpen && (
                <div className="px-5 pb-5 border-t border-gray-800">
                  {renderExpanded(idx)}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
