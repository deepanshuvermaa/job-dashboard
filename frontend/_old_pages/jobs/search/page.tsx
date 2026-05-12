'use client'

import { useState } from 'react'
import { ArrowLeft, Search, MapPin, Briefcase, ExternalLink, X, Download, MessageCircle, Users, Bot, Zap, Filter, Clock, Globe } from 'lucide-react'
import Link from 'next/link'

const SOURCE_COLORS: Record<string, string> = {
  linkedin: 'bg-blue-600 text-white',
  greenhouse: 'bg-green-600 text-white',
  lever: 'bg-purple-600 text-white',
  ashby: 'bg-orange-500 text-white',
  wellfound: 'bg-pink-600 text-white',
  workable: 'bg-cyan-600 text-white',
  dailyremote: 'bg-yellow-600 text-black',
  remotefront: 'bg-teal-600 text-white',
  portal_scan: 'bg-indigo-600 text-white',
}

function timeAgo(dateStr: string): string {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return `${Math.floor(diff / 86400)}d ago`
}

export default function JobSearch() {
  // Basic search state
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('United States')
  const [searching, setSearching] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])

  // Advanced filter state
  const [showFilters, setShowFilters] = useState(false)
  const [experienceLevel, setExperienceLevel] = useState('')
  const [jobType, setJobType] = useState('')
  const [postedWithin, setPostedWithin] = useState('')
  const [maxJobs, setMaxJobs] = useState(100)
  const [searchMode, setSearchMode] = useState('info') // 'info' or 'auto_apply'

  // Source filter state
  const [activeSource, setActiveSource] = useState('all')
  const [sourceCounts, setSourceCounts] = useState<Record<string, number>>({})

  // AI features state
  const [generatingMessages, setGeneratingMessages] = useState(false)
  const [sendingMessages, setSendingMessages] = useState(false)
  const [aiMessages, setAiMessages] = useState<any[]>([])

  // Message preview modal state
  const [showMessagePreview, setShowMessagePreview] = useState(false)
  const [previewMessages, setPreviewMessages] = useState<any[]>([])
  const [selectedMessages, setSelectedMessages] = useState<Set<number>>(new Set())

  const handleSearch = async () => {
    if (!keywords.trim()) {
      alert('Please enter job keywords')
      return
    }

    setSearching(true)

    try {
      // Check if Auto-Apply mode is selected
      if (searchMode === 'auto_apply') {
        // Use Easy Apply automation endpoint
        const response = await fetch('http://localhost:8000/api/jobs/easy-apply/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            keywords: keywords,
            location: location,
            max_applications: maxJobs,
            easy_apply_only: true,
            use_advanced_bot: true
          })
        })

        const data = await response.json()

        if (response.ok) {
          if (data.success) {
            alert(`🚀 Auto-Apply Started!\n\n✅ Found ${data.jobs_found} jobs\n🎯 Easy Apply jobs: ${data.easy_apply_jobs}\n\n Applications running in background...`)
          } else {
            alert(`❌ Auto-Apply Failed:\n${data.error}\n\nIssues: ${JSON.stringify(data.issues || {})}`)
          }
        } else {
          alert('Error: ' + (data.detail || 'Unknown error'))
        }
      } else {
        // Info Only mode - just search for jobs
        const params = new URLSearchParams({
          keywords: keywords,
          location: location,
          easy_apply: 'true',
          max_results: maxJobs.toString()
        })

        if (experienceLevel) params.append('experience_level', experienceLevel)
        if (jobType) params.append('job_type', jobType)
        if (postedWithin) params.append('posted_within', postedWithin)

        const response = await fetch(`http://localhost:8000/api/jobs/search?${params}`)
        const data = await response.json()

        if (response.ok) {
          const fetchedJobs = (data.jobs || []).map((j: any) => ({
            ...j,
            source: j.source || 'linkedin',
            scraped_at: j.scraped_at || new Date().toISOString()
          }))
          setJobs(fetchedJobs)
          // Count sources
          const counts: Record<string, number> = {}
          fetchedJobs.forEach((j: any) => {
            const s = j.source || 'linkedin'
            counts[s] = (counts[s] || 0) + 1
          })
          setSourceCounts(counts)
          alert(`Found ${fetchedJobs.length} jobs!`)
        } else {
          alert('Error: ' + (data.detail || 'Unknown error'))
        }
      }
    } catch (error) {
      console.error('Search error:', error)
      alert('Failed to search. Make sure backend is running on port 8000.')
    } finally {
      setSearching(false)
    }
  }

  const handleApply = async (job: any) => {
    if (!job.job_url || job.job_url === '#') {
      alert('No job URL available')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/jobs/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_url: job.job_url })
      })

      if (response.ok) {
        alert('✅ Application submitted!')
        setJobs(jobs.filter(j => j.id !== job.id))
      } else {
        alert('Failed to apply')
      }
    } catch (error) {
      alert('Error applying to job')
    }
  }

  const handleExportToExcel = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/export')

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `linkedin_jobs_${new Date().toISOString().split('T')[0]}.xlsx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        alert('✅ Excel file downloaded!')
      } else {
        alert('No jobs to export. Search first.')
      }
    } catch (error) {
      alert('Failed to export')
    }
  }

  const handleGenerateMessages = async () => {
    if (jobs.length === 0) {
      alert('Search for jobs first')
      return
    }

    setGeneratingMessages(true)
    try {
      const response = await fetch('http://localhost:8000/api/messages/generate', {
        method: 'POST'
      })
      const data = await response.json()

      if (response.ok) {
        const messages = data.messages || []
        setAiMessages(messages)
        setPreviewMessages(messages)

        // Select all messages by default
        const allIndexes = new Set<number>(messages.map((_: any, idx: number) => idx))
        setSelectedMessages(allIndexes)

        // Show preview modal
        setShowMessagePreview(true)
      } else {
        alert('Error generating messages')
      }
    } catch (error) {
      alert('Failed to generate messages')
    } finally {
      setGeneratingMessages(false)
    }
  }

  const handleToggleMessage = (index: number) => {
    const newSelected = new Set(selectedMessages)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedMessages(newSelected)
  }

  const handleSendSelectedMessages = async () => {
    const messagesToSend = previewMessages.filter((_: any, idx: number) => selectedMessages.has(idx))

    if (messagesToSend.length === 0) {
      alert('Please select at least one message to send')
      return
    }

    if (!confirm(`Send ${messagesToSend.length} personalized messages to recruiters?`)) return

    setSendingMessages(true)
    setShowMessagePreview(false)

    try {
      const response = await fetch('http://localhost:8000/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ max_messages: messagesToSend.length, delay_seconds: 30 })
      })

      if (response.ok) {
        alert(`✅ Sending ${messagesToSend.length} messages in background! Check console for progress.`)
      } else {
        alert('Error sending messages')
      }
    } catch (error) {
      alert('Error sending messages')
    } finally {
      setSendingMessages(false)
    }
  }

  const handleSendMessages = async () => {
    if (aiMessages.length === 0) {
      alert('Generate messages first')
      return
    }

    // Open preview modal
    setPreviewMessages(aiMessages)
    const allIndexes = new Set(aiMessages.map((_: any, idx: number) => idx))
    setSelectedMessages(allIndexes)
    setShowMessagePreview(true)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">🔍 Smart Job Search</h1>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords *
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g. Full Stack Engineer, React Developer"
                  className="input pl-10"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location *
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Location"
                  className="input pl-10"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">🎯 Advanced Filters</h3>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)}
                        className="input text-sm">
                  <option value="">Any Experience</option>
                  <option value="entry">Entry (0-2 years)</option>
                  <option value="mid">Mid (3-5 years)</option>
                  <option value="senior">Senior (5+ years)</option>
                  <option value="director">Director</option>
                </select>

                <select value={postedWithin} onChange={(e) => setPostedWithin(e.target.value)}
                        className="input text-sm">
                  <option value="">Any Time</option>
                  <option value="1h">Past 1 Hour</option>
                  <option value="6h">Past 6 Hours</option>
                  <option value="10h">Past 10 Hours</option>
                  <option value="12h">Past 12 Hours</option>
                  <option value="24h">Past 24 Hours</option>
                  <option value="week">Past Week</option>
                  <option value="month">Past Month</option>
                </select>

                <select value={jobType} onChange={(e) => setJobType(e.target.value)}
                        className="input text-sm">
                  <option value="">Any Job Type</option>
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>

                <input type="number" value={maxJobs} onChange={(e) => setMaxJobs(Number(e.target.value))}
                       min="10" max="500" step="25" placeholder="Max jobs (up to 500)"
                       className="input text-sm" />
              </div>

              <div className="flex items-center space-x-6">
                <label className="text-sm font-medium text-gray-700">Search Mode:</label>
                <label className="flex items-center cursor-pointer">
                  <input type="radio" value="info" checked={searchMode === 'info'}
                         onChange={(e) => setSearchMode(e.target.value)}
                         className="mr-2" />
                  <span className="text-sm">📊 Info Only</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input type="radio" value="auto_apply" checked={searchMode === 'auto_apply'}
                         onChange={(e) => setSearchMode(e.target.value)}
                         className="mr-2" />
                  <span className="text-sm">🤖 Auto-Apply</span>
                </label>
              </div>
            </div>
          )}

          <button
            onClick={handleSearch}
            disabled={searching}
            className="btn-primary mt-4 w-full md:w-auto text-lg px-8 py-3"
          >
            {searching ? '🔄 Searching LinkedIn...' : '🚀 Search Jobs'}
          </button>
        </div>

        {/* Results Header */}
        {jobs.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
              <h2 className="text-xl font-bold text-gray-900">
                {jobs.length} Jobs Found
              </h2>

              <div className="flex flex-wrap gap-2">
                <Link href="/jobs/feed" className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                  <Globe className="w-4 h-4" />
                  <span>All Sources Feed</span>
                </Link>
                <button onClick={handleExportToExcel}
                        className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  <Download className="w-4 h-4" />
                  <span>Export Excel</span>
                </button>

                <button onClick={handleGenerateMessages} disabled={generatingMessages}
                        className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50">
                  <Bot className="w-4 h-4" />
                  <span>{generatingMessages ? 'Generating...' : 'AI Messages'}</span>
                </button>

                <button onClick={handleSendMessages} disabled={sendingMessages || aiMessages.length === 0}
                        className="flex items-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50">
                  <Zap className="w-4 h-4" />
                  <span>{sendingMessages ? 'Sending...' : 'Auto-Message'}</span>
                </button>
              </div>
            </div>

            {/* Source Filter Tabs */}
            {Object.keys(sourceCounts).length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                <button
                  onClick={() => setActiveSource('all')}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                    activeSource === 'all'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  All Sources ({jobs.length})
                </button>
                {Object.entries(sourceCounts).map(([src, count]) => (
                  <button
                    key={src}
                    onClick={() => setActiveSource(activeSource === src ? 'all' : src)}
                    className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      activeSource === src
                        ? (SOURCE_COLORS[src] || 'bg-gray-900 text-white')
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {src.charAt(0).toUpperCase() + src.slice(1)} ({count})
                  </button>
                ))}
              </div>
            )}

            {/* Job Cards */}
            <div className="space-y-4">
              {jobs
                .filter(job => activeSource === 'all' || (job.source || 'linkedin') === activeSource)
                .map((job, index) => (
                <div key={index} className="card hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Job Title & Company + Source Badge */}
                      <div className="mb-3">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-lg font-bold text-gray-900">{job.title || 'N/A'}</h3>
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                            SOURCE_COLORS[job.source || 'linkedin'] || 'bg-gray-500 text-white'
                          }`}>
                            {(job.source || 'linkedin').toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-700 font-medium">{job.company || 'N/A'}</p>
                      </div>

                      {/* Metadata */}
                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mb-3">
                        <span className="flex items-center">
                          <MapPin className="w-4 h-4 mr-1" />
                          {job.location || 'N/A'}
                        </span>
                        {job.salary && (
                          <span className="flex items-center">
                            <Briefcase className="w-4 h-4 mr-1" />
                            {job.salary}
                          </span>
                        )}
                        <span className="flex items-center">
                          <Clock className="w-4 h-4 mr-1" />
                          {job.scraped_at ? timeAgo(job.scraped_at) : (
                            job.posted_days_ago !== undefined && job.posted_days_ago !== null
                              ? `${job.posted_days_ago}d ago`
                              : (job.posted_date || 'recently')
                          )}
                        </span>
                        {job.applicant_count && (
                          <span>Applicants: {job.applicant_count}</span>
                        )}
                        {job.easy_apply && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                            Easy Apply
                          </span>
                        )}
                      </div>

                      {/* Relevance Score */}
                      {job.relevance_score && (
                        <div className="flex items-center space-x-2 mb-3">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-xs">
                            <div className="bg-blue-600 h-2 rounded-full"
                                 style={{ width: `${job.relevance_score * 100}%` }}></div>
                          </div>
                          <span className="text-sm font-medium text-blue-600">
                            {Math.round(job.relevance_score * 100)}% match
                          </span>
                        </div>
                      )}

                      {/* RECRUITER SECTION */}
                      {job.recruiter_info && job.recruiter_info.name && (
                        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                          <p className="text-sm font-semibold text-gray-800 mb-2">
                            👤 Recruiter: {job.recruiter_info.name}
                          </p>
                          {job.recruiter_info.title && (
                            <p className="text-xs text-gray-600 mb-2">{job.recruiter_info.title}</p>
                          )}
                          <div className="flex gap-2">
                            {job.recruiter_info.dm_link && (
                              <a href={job.recruiter_info.dm_link} target="_blank" rel="noopener noreferrer"
                                 className="text-xs px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                                📧 Send DM
                              </a>
                            )}
                            {job.recruiter_info.profile_url && (
                              <a href={job.recruiter_info.profile_url} target="_blank" rel="noopener noreferrer"
                                 className="text-xs px-3 py-1 border border-blue-600 text-blue-600 rounded hover:bg-blue-50">
                                View Profile
                              </a>
                            )}
                          </div>
                        </div>
                      )}

                      {/* PEOPLE WHO CAN HELP SECTION */}
                      {job.people_who_can_help && job.people_who_can_help.length > 0 && (
                        <div className="mt-3 p-3 bg-green-50 rounded-lg">
                          <p className="text-sm font-semibold text-gray-800 mb-2">
                            🤝 People Who Can Help ({job.people_who_can_help.length})
                          </p>
                          <div className="space-y-2">
                            {job.people_who_can_help.slice(0, 3).map((person: any, idx: number) => (
                              <div key={idx} className="flex justify-between items-center text-xs">
                                <div className="flex-1">
                                  <span className="font-medium">{person.name}</span>
                                  {person.title && <span className="text-gray-600"> - {person.title}</span>}
                                  {person.connection_degree && (
                                    <span className="ml-2 text-gray-500">({person.connection_degree})</span>
                                  )}
                                </div>
                                <div className="flex gap-1">
                                  {person.dm_link && (
                                    <a href={person.dm_link} target="_blank" rel="noopener noreferrer"
                                       className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">
                                      DM
                                    </a>
                                  )}
                                  {person.profile_url && (
                                    <a href={person.profile_url} target="_blank" rel="noopener noreferrer"
                                       className="px-2 py-1 text-xs border border-green-600 text-green-600 rounded hover:bg-green-50">
                                      Profile
                                    </a>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2 ml-4">
                      <button onClick={() => handleApply(job)}
                              className="btn-primary whitespace-nowrap">
                        Quick Apply
                      </button>
                      {job.job_url && job.job_url !== '#' && (
                        <a href={job.job_url} target="_blank" rel="noopener noreferrer"
                           className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-center">
                          <ExternalLink className="w-5 h-5 inline" />
                        </a>
                      )}
                      <button onClick={() => setJobs(jobs.filter((_, i) => i !== index))}
                              className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {jobs.length === 0 && !searching && (
          <div className="card text-center py-16">
            <Search className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">Ready to find your dream job?</h3>
            <p className="text-gray-600 mb-4">Enter keywords and click Search to get started</p>
            <div className="flex justify-center gap-4 text-sm text-gray-500">
              <span>✅ Real LinkedIn jobs</span>
              <span>✅ Recruiter contacts</span>
              <span>✅ AI-powered messaging</span>
            </div>
          </div>
        )}
      </main>

      {/* Message Preview Modal */}
      {showMessagePreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">
                  📨 Preview AI-Generated Messages
                </h2>
                <button
                  onClick={() => setShowMessagePreview(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Review and select which messages to send. All messages are selected by default.
              </p>
            </div>

            <div className="p-6 overflow-y-auto max-h-[60vh] space-y-4">
              {previewMessages.length === 0 ? (
                <div className="text-center py-12 text-gray-600">
                  No messages generated. Try searching for jobs first.
                </div>
              ) : (
                previewMessages.map((msg: any, idx: number) => (
                  <div
                    key={idx}
                    className={`border rounded-lg p-4 transition-all ${
                      selectedMessages.has(idx)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-white'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedMessages.has(idx)}
                        onChange={() => handleToggleMessage(idx)}
                        className="mt-1 w-5 h-5 text-blue-600"
                      />
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h3 className="font-bold text-gray-900">
                              {msg.recruiter_name || 'Recruiter'}
                            </h3>
                            <p className="text-sm text-gray-600">
                              {msg.recruiter_title || ''} • {msg.company || ''}
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                              Job: {msg.job_title || 'Position'}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                              AI Generated
                            </span>
                          </div>
                        </div>

                        <div className="mt-3 p-3 bg-white rounded-lg border border-gray-200">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap">
                            {msg.message}
                          </p>
                        </div>

                        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                          <span>{msg.message?.length || 0} characters</span>
                          {msg.dm_link && (
                            <a
                              href={msg.dm_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800"
                            >
                              View LinkedIn Profile →
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  <strong>{selectedMessages.size}</strong> of {previewMessages.length} messages selected
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowMessagePreview(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => {
                      const allIndexes = new Set(previewMessages.map((_: any, idx: number) => idx))
                      if (selectedMessages.size === previewMessages.length) {
                        setSelectedMessages(new Set())
                      } else {
                        setSelectedMessages(allIndexes)
                      }
                    }}
                    className="btn-secondary"
                  >
                    {selectedMessages.size === previewMessages.length ? 'Deselect All' : 'Select All'}
                  </button>
                  <button
                    onClick={handleSendSelectedMessages}
                    disabled={selectedMessages.size === 0 || sendingMessages}
                    className="btn-primary"
                  >
                    {sendingMessages
                      ? 'Sending...'
                      : `Send ${selectedMessages.size} Message${selectedMessages.size !== 1 ? 's' : ''}`}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
