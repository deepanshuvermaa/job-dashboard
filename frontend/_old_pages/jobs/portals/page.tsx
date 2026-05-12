'use client'

import { useState, useEffect, useRef } from 'react'
import {
  ArrowLeft, Search, Play, Globe, Building2, CheckCircle, XCircle,
  Loader2, Download, Filter, Clock, MapPin, Briefcase, ExternalLink,
  FileText, Wand2, X, RefreshCw,
} from 'lucide-react'
import Link from 'next/link'

interface Portal { name: string; ats: string; url: string; enabled: boolean }
interface ScanStatus {
  running: boolean
  progress: { status?: string; completed?: number; total?: number; current?: string; jobs_found?: number }
  results: any
}

const ATS_COLORS: Record<string, string> = {
  greenhouse: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  ashby: 'bg-orange-100 text-orange-700 border-orange-200',
  lever: 'bg-purple-100 text-purple-700 border-purple-200',
  wellfound: 'bg-pink-100 text-pink-700 border-pink-200',
  workable: 'bg-cyan-100 text-cyan-700 border-cyan-200',
}

export default function PortalScanner() {
  const [config, setConfig] = useState<{ portals: Portal[]; search_queries: any[] }>({ portals: [], search_queries: [] })
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [scanStatus, setScanStatus] = useState<ScanStatus | null>(null)
  const pollRef = useRef<NodeJS.Timeout | null>(null)

  // Scan filters
  const [keywordFilter, setKeywordFilter] = useState('')
  const [locationFilter, setLocationFilter] = useState('')
  const [showFilters, setShowFilters] = useState(false)

  // ATS detection state
  const [detecting, setDetecting] = useState(false)
  const [detectionStatus, setDetectionStatus] = useState<any>(null)
  const [detectedCount, setDetectedCount] = useState<any>(null)
  const detPollRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    fetchConfig()
    fetchDetectedCount()
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
      if (detPollRef.current) clearInterval(detPollRef.current)
    }
  }, [])

  const fetchConfig = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/portals/config')
      const data = await res.json()
      if (data.config) setConfig(data.config)
    } catch (err) { console.error('Failed to load portal config:', err) }
    finally { setLoading(false) }
  }

  const startScan = async () => {
    setScanning(true)
    try {
      await fetch('http://localhost:8000/api/portals/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword_filter: keywordFilter || null,
          location_filter: locationFilter || null,
        }),
      })

      const interval = setInterval(async () => {
        try {
          const res = await fetch('http://localhost:8000/api/portals/scan/status')
          const status = await res.json()
          setScanStatus(status)
          if (!status.running && status.progress?.status !== 'starting') {
            clearInterval(interval); pollRef.current = null; setScanning(false)
          }
        } catch { clearInterval(interval); pollRef.current = null; setScanning(false) }
      }, 2000)
      pollRef.current = interval
    } catch { setScanning(false) }
  }

  const fetchDetectedCount = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/portals/detected')
      const data = await res.json()
      if (data.success) setDetectedCount(data)
    } catch { /* silent */ }
  }

  const startATSDetection = async () => {
    setDetecting(true)
    setDetectionStatus(null)
    try {
      await fetch('http://localhost:8000/api/portals/detect-ats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_workers: 15 }),
      })

      const interval = setInterval(async () => {
        try {
          const res = await fetch('http://localhost:8000/api/portals/detect-ats/status')
          const status = await res.json()
          setDetectionStatus(status)
          if (!status.running && status.progress?.status !== 'starting') {
            clearInterval(interval); detPollRef.current = null; setDetecting(false)
            fetchDetectedCount()
          }
        } catch { clearInterval(interval); detPollRef.current = null; setDetecting(false) }
      }, 3000)
      detPollRef.current = interval
    } catch { setDetecting(false) }
  }

  const startExtendedScan = async () => {
    setScanning(true)
    try {
      await fetch('http://localhost:8000/api/portals/scan-extended', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword_filter: keywordFilter || null,
          location_filter: locationFilter || null,
          include_detected: true,
        }),
      })

      const interval = setInterval(async () => {
        try {
          const res = await fetch('http://localhost:8000/api/portals/scan/status')
          const status = await res.json()
          setScanStatus(status)
          if (!status.running && status.progress?.status !== 'starting') {
            clearInterval(interval); pollRef.current = null; setScanning(false)
          }
        } catch { clearInterval(interval); pollRef.current = null; setScanning(false) }
      }, 2000)
      pollRef.current = interval
    } catch { setScanning(false) }
  }

  const exportToExcel = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/jobs/export-feed')
      if (!res.ok) return
      const blob = await res.blob()
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob)
      a.download = `portal_scan_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a); a.click(); a.remove()
    } catch (err) { console.error('Export failed:', err) }
  }

  const togglePortal = (i: number) => {
    const updated = { ...config }
    updated.portals[i].enabled = !updated.portals[i].enabled
    setConfig(updated)
  }

  const enabled = config.portals.filter(p => p.enabled).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* ═══ HEADER ═══ */}
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="p-2 rounded-lg hover:bg-gray-100 text-gray-500 hover:text-gray-900">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Globe className="w-6 h-6 text-indigo-600" />
                Portal Scanner
              </h1>
              <p className="text-sm text-gray-500">Scan {enabled} career pages + {config.search_queries?.length || 0} search queries</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={exportToExcel} className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium">
              <Download className="w-4 h-4" /> Export Excel
            </button>
            <Link href="/jobs/feed" className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 bg-white hover:bg-gray-50 rounded-lg text-sm font-medium text-gray-700">
              <Briefcase className="w-4 h-4" /> View All Jobs
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-6">
        {/* ═══ SCAN CONTROLS ═══ */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">Scan Configuration</h2>
            <button onClick={() => setShowFilters(!showFilters)} className="flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800">
              <Filter className="w-4 h-4" /> {showFilters ? 'Hide' : 'Show'} Filters
            </button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 p-4 bg-indigo-50 rounded-lg border border-indigo-100">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Keyword Filter</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input type="text" value={keywordFilter} onChange={e => setKeywordFilter(e.target.value)}
                    placeholder="e.g. Software Developer, React, Python..."
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" />
                </div>
                <p className="text-xs text-gray-500 mt-1">Filters scraped jobs by title/description match</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location Filter</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input type="text" value={locationFilter} onChange={e => setLocationFilter(e.target.value)}
                    placeholder="e.g. India, Remote, Bangalore..."
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" />
                </div>
                <p className="text-xs text-gray-500 mt-1">Filters scraped jobs by location match</p>
              </div>
            </div>
          )}

          <button onClick={startScan} disabled={scanning}
            className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-6 py-3.5 rounded-xl font-semibold text-base transition-colors">
            {scanning ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Scanning Portals...</>
            ) : (
              <><Play className="w-5 h-5" /> Scan All Portals {keywordFilter && `(filter: "${keywordFilter}")`} {locationFilter && `(location: "${locationFilter}")`}</>
            )}
          </button>
        </div>

        {/* ═══ AWESOME CAREER PAGES IMPORT ═══ */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Globe className="w-5 h-5 text-indigo-600" />
                Awesome Career Pages (1,054 Companies)
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Auto-detect ATS from 1,054 company career pages, then scan all detected portals for jobs
              </p>
            </div>
            {detectedCount && (
              <div className="text-right">
                <div className="text-2xl font-bold text-indigo-600">{detectedCount.total}</div>
                <div className="text-xs text-gray-500">companies detected</div>
              </div>
            )}
          </div>

          {/* ATS Breakdown badges */}
          {detectedCount?.ats_breakdown && (
            <div className="flex flex-wrap gap-2 mb-4">
              {Object.entries(detectedCount.ats_breakdown).map(([ats, count]) => (
                <span key={ats} className={`px-3 py-1 rounded-lg text-xs font-semibold border ${
                  ATS_COLORS[ats] || 'bg-gray-100 text-gray-600 border-gray-200'
                }`}>
                  {ats}: {count as number}
                </span>
              ))}
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={startATSDetection} disabled={detecting}
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium">
              {detecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              {detecting ? 'Detecting ATS...' : 'Detect ATS (1,054 companies)'}
            </button>
            {detectedCount?.total > 0 && (
              <button onClick={startExtendedScan} disabled={scanning}
                className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium">
                {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                Scan All ({detectedCount.total} + {enabled} portals)
              </button>
            )}
          </div>

          {/* Detection progress */}
          {detectionStatus?.running && (
            <div className="mt-4 p-4 bg-indigo-50 rounded-lg border border-indigo-100">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-700">
                  Detecting: <strong>{detectionStatus.progress?.current}</strong> ({detectionStatus.progress?.current_ats})
                </span>
                <span className="text-indigo-600 font-medium">
                  {detectionStatus.progress?.completed || 0} / {detectionStatus.progress?.total || '?'}
                </span>
              </div>
              <div className="w-full bg-indigo-200 rounded-full h-2">
                <div className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${((detectionStatus.progress?.completed || 0) / Math.max(detectionStatus.progress?.total || 1, 1)) * 100}%` }} />
              </div>
            </div>
          )}

          {/* Detection results */}
          {detectionStatus?.results?.total_companies && !detectionStatus?.running && (
            <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-100">
              <p className="text-sm font-semibold text-green-800 mb-2">
                Detection Complete: {detectionStatus.results.total_companies} companies analyzed
              </p>
              <p className="text-sm text-green-700">
                Directly scrapeable: <strong>{detectionStatus.results.scrapeable}</strong> companies
              </p>
            </div>
          )}
        </div>

        {/* ═══ SCAN PROGRESS ═══ */}
        {scanStatus && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Scan Progress</h2>
            {scanStatus.running ? (
              <div>
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-gray-600">
                    {scanStatus.progress?.current ? `Scanning: ${scanStatus.progress.current}` : 'Starting...'}
                  </span>
                  <span className="font-medium text-indigo-600">
                    {scanStatus.progress?.completed || 0} / {scanStatus.progress?.total || '?'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${((scanStatus.progress?.completed || 0) / Math.max(scanStatus.progress?.total || 1, 1)) * 100}%` }} />
                </div>
                <p className="text-sm text-gray-500 mt-2">Jobs found: <strong className="text-indigo-600">{scanStatus.progress?.jobs_found || 0}</strong></p>
              </div>
            ) : scanStatus.results ? (
              <div>
                <div className="grid grid-cols-4 gap-4 mb-4">
                  {[
                    { label: 'Total Scraped', value: scanStatus.results.total_scraped, color: 'text-indigo-600' },
                    { label: 'New Jobs', value: scanStatus.results.new_jobs, color: 'text-green-600' },
                    { label: 'Duplicates', value: scanStatus.results.duplicates_skipped, color: 'text-yellow-600' },
                    { label: 'Saved to DB', value: scanStatus.results.saved_to_db, color: 'text-purple-600' },
                  ].map(s => (
                    <div key={s.label} className="bg-gray-50 rounded-lg p-4 text-center border border-gray-100">
                      <div className={`text-2xl font-bold ${s.color}`}>{s.value || 0}</div>
                      <div className="text-xs text-gray-500 mt-1">{s.label}</div>
                    </div>
                  ))}
                </div>
                <div className="flex gap-3">
                  <Link href="/jobs/feed" className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium">
                    <Briefcase className="w-4 h-4" /> View Jobs in Feed
                  </Link>
                  <button onClick={exportToExcel} className="flex items-center gap-2 px-4 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium">
                    <Download className="w-4 h-4" /> Export to Excel
                  </button>
                  <Link href="/resume" className="flex items-center gap-2 px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium">
                    <FileText className="w-4 h-4" /> Generate Resumes
                  </Link>
                </div>
              </div>
            ) : null}
          </div>
        )}

        {/* ═══ PORTAL LIST ═══ */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Configured Portals ({config.portals.length})</h2>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {config.portals.map((portal, i) => (
                <div key={i} onClick={() => togglePortal(i)}
                  className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
                    portal.enabled ? 'bg-white border-gray-200 hover:border-indigo-400 hover:shadow-sm' : 'bg-gray-50 border-gray-100 opacity-40'
                  }`}>
                  <div className="flex items-center gap-3">
                    <Building2 className="w-4 h-4 text-gray-400" />
                    <div>
                      <div className="font-medium text-sm text-gray-900">{portal.name}</div>
                      <span className={`text-xs px-2 py-0.5 rounded border ${ATS_COLORS[portal.ats] || 'bg-gray-100 text-gray-600 border-gray-200'}`}>
                        {portal.ats}
                      </span>
                    </div>
                  </div>
                  {portal.enabled ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-gray-300" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ═══ SEARCH QUERIES ═══ */}
        {config.search_queries?.length > 0 && (
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Search Queries ({config.search_queries.length})</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {config.search_queries.map((q: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
                  <div>
                    <div className="font-medium text-sm text-gray-900">{q.keywords}</div>
                    <div className="flex gap-1 mt-1">
                      {q.boards?.map((b: string) => (
                        <span key={b} className="text-xs px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-600 border border-indigo-100">{b}</span>
                      ))}
                    </div>
                  </div>
                  <Search className="w-4 h-4 text-gray-400" />
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
