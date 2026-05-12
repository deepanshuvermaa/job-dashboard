'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import {
  ArrowLeft,
  Mail,
  Send,
  FileText,
  Users,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  Pencil,
  BarChart3,
  RefreshCw,
} from 'lucide-react'

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

interface Template {
  id: string
  name: string
  preview: string
}

interface OutreachLogEntry {
  id: string
  status: 'queued' | 'sent' | 'failed'
  recruiter_name: string
  recruiter_email: string
  company: string
  job_title: string
  template: string
  created_at: string
}

interface GeneratedEmail {
  subject: string
  body: string
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function OutreachPage() {
  // Templates
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [loadingTemplates, setLoadingTemplates] = useState(true)

  // Composer form
  const [recruiterName, setRecruiterName] = useState('')
  const [recruiterEmail, setRecruiterEmail] = useState('')
  const [company, setCompany] = useState('')
  const [jobTitle, setJobTitle] = useState('')

  // Generated email
  const [generatedEmail, setGeneratedEmail] = useState<GeneratedEmail | null>(null)
  const [editSubject, setEditSubject] = useState('')
  const [editBody, setEditBody] = useState('')
  const [generating, setGenerating] = useState(false)
  const [sending, setSending] = useState(false)
  const [bulkSending, setBulkSending] = useState(false)

  // Log
  const [log, setLog] = useState<OutreachLogEntry[]>([])
  const [loadingLog, setLoadingLog] = useState(true)
  const [statusFilter, setStatusFilter] = useState<'all' | 'queued' | 'sent'>('all')

  // Feedback
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  /* ---------------------------------------------------------------- */
  /*  Data fetching                                                    */
  /* ---------------------------------------------------------------- */

  const fetchTemplates = useCallback(async () => {
    setLoadingTemplates(true)
    try {
      const res = await fetch('http://localhost:8000/api/outreach/templates')
      if (res.ok) {
        const data = await res.json()
        const list: Template[] = data.templates ?? data
        setTemplates(list)
        if (list.length > 0 && !selectedTemplate) {
          setSelectedTemplate(list[0].id)
        }
      }
    } catch (err) {
      console.error('Failed to load templates', err)
    } finally {
      setLoadingTemplates(false)
    }
  }, [selectedTemplate])

  const fetchLog = useCallback(async () => {
    setLoadingLog(true)
    try {
      const res = await fetch('http://localhost:8000/api/outreach/log')
      if (res.ok) {
        const data = await res.json()
        setLog(data.log ?? data)
      }
    } catch (err) {
      console.error('Failed to load outreach log', err)
    } finally {
      setLoadingLog(false)
    }
  }, [])

  useEffect(() => {
    fetchTemplates()
    fetchLog()
  }, [fetchTemplates, fetchLog])

  /* ---------------------------------------------------------------- */
  /*  Actions                                                          */
  /* ---------------------------------------------------------------- */

  const showToast = (message: string, type: 'success' | 'error') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }

  const handleGenerate = async () => {
    if (!selectedTemplate) {
      showToast('Please select a template first.', 'error')
      return
    }
    if (!recruiterName.trim() || !recruiterEmail.trim()) {
      showToast('Recruiter name and email are required.', 'error')
      return
    }

    setGenerating(true)
    try {
      const res = await fetch('http://localhost:8000/api/outreach/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: selectedTemplate,
          recruiter_name: recruiterName,
          recruiter_email: recruiterEmail,
          company,
          job_title: jobTitle,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        const email: GeneratedEmail = { subject: data.subject, body: data.body }
        setGeneratedEmail(email)
        setEditSubject(email.subject)
        setEditBody(email.body)
        showToast('Email generated successfully.', 'success')
      } else {
        const err = await res.json().catch(() => null)
        showToast(err?.detail ?? 'Failed to generate email.', 'error')
      }
    } catch {
      showToast('Could not connect to backend.', 'error')
    } finally {
      setGenerating(false)
    }
  }

  const handleQueueEmail = async () => {
    if (!editSubject.trim() || !editBody.trim()) {
      showToast('Subject and body cannot be empty.', 'error')
      return
    }

    setSending(true)
    try {
      const res = await fetch('http://localhost:8000/api/outreach/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recruiter_name: recruiterName,
          recruiter_email: recruiterEmail,
          company,
          job_title: jobTitle,
          template_id: selectedTemplate,
          subject: editSubject,
          body: editBody,
        }),
      })

      if (res.ok) {
        showToast('Email queued successfully.', 'success')
        setGeneratedEmail(null)
        setEditSubject('')
        setEditBody('')
        setRecruiterName('')
        setRecruiterEmail('')
        setCompany('')
        setJobTitle('')
        fetchLog()
      } else {
        const err = await res.json().catch(() => null)
        showToast(err?.detail ?? 'Failed to queue email.', 'error')
      }
    } catch {
      showToast('Could not connect to backend.', 'error')
    } finally {
      setSending(false)
    }
  }

  const handleBulkSend = async () => {
    setBulkSending(true)
    try {
      const res = await fetch('http://localhost:8000/api/outreach/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          template_id: selectedTemplate,
        }),
      })

      if (res.ok) {
        const data = await res.json()
        showToast(data.message ?? 'Bulk emails queued successfully.', 'success')
        fetchLog()
      } else {
        const err = await res.json().catch(() => null)
        showToast(err?.detail ?? 'Bulk send failed.', 'error')
      }
    } catch {
      showToast('Could not connect to backend.', 'error')
    } finally {
      setBulkSending(false)
    }
  }

  const [importing, setImporting] = useState(false)

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('template', selectedTemplate || 'introduction')
      const res = await fetch('http://localhost:8000/api/outreach/import', {
        method: 'POST',
        body: formData,
      })
      if (res.ok) {
        const data = await res.json()
        showToast(data.message || `Imported ${data.queued} emails`, 'success')
        fetchLog()
      } else {
        const err = await res.json().catch(() => null)
        showToast(err?.detail || 'Import failed', 'error')
      }
    } catch {
      showToast('Could not connect to backend.', 'error')
    } finally {
      setImporting(false)
      e.target.value = ''
    }
  }

  /* ---------------------------------------------------------------- */
  /*  Derived data                                                     */
  /* ---------------------------------------------------------------- */

  const totalQueued = log.filter((e) => e.status === 'queued').length
  const totalSent = log.filter((e) => e.status === 'sent').length
  const responseRate = totalSent > 0 ? '—' : '—' // placeholder

  const filteredLog =
    statusFilter === 'all' ? log : log.filter((e) => e.status === statusFilter)

  /* ---------------------------------------------------------------- */
  /*  Render helpers                                                   */
  /* ---------------------------------------------------------------- */

  const statusBadge = (status: string) => {
    switch (status) {
      case 'queued':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
            <Clock className="w-3 h-3" />
            Queued
          </span>
        )
      case 'sent':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/30">
            <CheckCircle2 className="w-3 h-3" />
            Sent
          </span>
        )
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500/20 text-red-400 border border-red-500/30">
            <XCircle className="w-3 h-3" />
            Failed
          </span>
        )
      default:
        return null
    }
  }

  /* ---------------------------------------------------------------- */
  /*  JSX                                                              */
  /* ---------------------------------------------------------------- */

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      {/* Toast */}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-50 px-5 py-3 rounded-lg shadow-lg text-sm font-medium transition-all ${
            toast.type === 'success'
              ? 'bg-green-600/90 text-white'
              : 'bg-red-600/90 text-white'
          }`}
        >
          {toast.message}
        </div>
      )}

      {/* Header */}
      <header className="bg-white border-b border-gray-200 -mx-6 -mt-6 mb-8 px-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center gap-4">
          <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Email Outreach</h1>
            <p className="text-gray-600 text-sm">
              Generate and send personalized outreach emails to recruiters
            </p>
          </div>
        </div>
      </header>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-yellow-500/10">
            <Clock className="w-5 h-5 text-yellow-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">{totalQueued}</p>
            <p className="text-gray-600 text-sm">Emails Queued</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-green-500/10">
            <Send className="w-5 h-5 text-green-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">{totalSent}</p>
            <p className="text-gray-600 text-sm">Emails Sent</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 flex items-center gap-4">
          <div className="p-3 rounded-lg bg-blue-500/10">
            <BarChart3 className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">{responseRate}</p>
            <p className="text-gray-600 text-sm">Response Rate</p>
          </div>
        </div>
      </div>

      {/* Two-column: Templates | Composer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Template Selector (left panel) */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Templates
            </h2>

            {loadingTemplates ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-gray-500" />
              </div>
            ) : templates.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">
                No templates available.
              </p>
            ) : (
              <div className="space-y-3">
                {templates.map((tpl) => (
                  <button
                    key={tpl.id}
                    onClick={() => setSelectedTemplate(tpl.id)}
                    className={`w-full text-left p-4 rounded-lg border transition-all ${
                      selectedTemplate === tpl.id
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-gray-300 bg-gray-50 hover:border-gray-400'
                    }`}
                  >
                    <p className="font-medium text-sm">{tpl.name}</p>
                    <p className="text-gray-600 text-xs mt-1 line-clamp-2">
                      {tpl.preview}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Email Composer (center/right panel) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Form fields */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Pencil className="w-5 h-5 text-purple-400" />
              Compose Email
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
              <div>
                <label className="block text-sm text-gray-600 mb-1.5">
                  Recruiter Name
                </label>
                <input
                  type="text"
                  value={recruiterName}
                  onChange={(e) => setRecruiterName(e.target.value)}
                  placeholder="Jane Smith"
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1.5">
                  Recruiter Email
                </label>
                <input
                  type="email"
                  value={recruiterEmail}
                  onChange={(e) => setRecruiterEmail(e.target.value)}
                  placeholder="jane@company.com"
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1.5">
                  Company
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="Acme Corp"
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1.5">
                  Job Title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="Senior Software Engineer"
                  className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500 transition-colors"
                />
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
              >
                {generating ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Mail className="w-4 h-4" />
                )}
                Generate Email
              </button>

              <button
                onClick={handleBulkSend}
                disabled={bulkSending || !selectedTemplate}
                className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
              >
                {bulkSending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Users className="w-4 h-4" />
                )}
                Send to All with Recruiters
              </button>

              {/* Import Excel/CSV */}
              <label className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-500 rounded-lg text-sm font-medium cursor-pointer transition-colors">
                {importing ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <FileText className="w-4 h-4" />
                )}
                {importing ? 'Importing...' : 'Import Excel/CSV'}
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleImportFile}
                  className="hidden"
                  disabled={importing}
                />
              </label>
            </div>

            <p className="text-xs text-gray-500 mt-3">
              Excel/CSV format: columns named <strong>name</strong>, <strong>email</strong>, <strong>company</strong>, <strong>job_title</strong>. Emails will be generated using the selected template.
            </p>
          </div>

          {/* Generated Email Preview / Editor */}
          {generatedEmail && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Mail className="w-5 h-5 text-green-400" />
                Email Preview
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1.5">
                    Subject
                  </label>
                  <input
                    type="text"
                    value={editSubject}
                    onChange={(e) => setEditSubject(e.target.value)}
                    className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-1.5">
                    Body
                  </label>
                  <textarea
                    value={editBody}
                    onChange={(e) => setEditBody(e.target.value)}
                    rows={10}
                    className="w-full bg-gray-100 border border-gray-300 rounded-lg px-4 py-3 text-sm text-gray-900 focus:outline-none focus:border-blue-500 transition-colors resize-y leading-relaxed"
                  />
                </div>

                <button
                  onClick={handleQueueEmail}
                  disabled={sending}
                  className="flex items-center gap-2 px-5 py-2.5 bg-green-600 hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-colors"
                >
                  {sending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  Queue Email
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Outreach Log */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <FileText className="w-5 h-5 text-orange-400" />
            Outreach Log
          </h2>

          <div className="flex items-center gap-2">
            {/* Status filter tabs */}
            {(['all', 'queued', 'sent'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setStatusFilter(tab)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors capitalize ${
                  statusFilter === tab
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}

            <button
              onClick={fetchLog}
              className="ml-2 p-2 rounded-lg bg-gray-100 text-gray-600 hover:text-gray-900 transition-colors"
              title="Refresh log"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {loadingLog ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-gray-500" />
          </div>
        ) : filteredLog.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">
            No outreach emails found.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-gray-600 text-left">
                  <th className="pb-3 pr-4 font-medium">Status</th>
                  <th className="pb-3 pr-4 font-medium">Recruiter</th>
                  <th className="pb-3 pr-4 font-medium">Company</th>
                  <th className="pb-3 pr-4 font-medium">Job Title</th>
                  <th className="pb-3 pr-4 font-medium">Template</th>
                  <th className="pb-3 font-medium">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200/50">
                {filteredLog.map((entry) => (
                  <tr key={entry.id} className="hover:bg-gray-50 transition-colors">
                    <td className="py-3 pr-4">{statusBadge(entry.status)}</td>
                    <td className="py-3 pr-4 text-gray-900">{entry.recruiter_name}</td>
                    <td className="py-3 pr-4 text-gray-700">{entry.company}</td>
                    <td className="py-3 pr-4 text-gray-700">{entry.job_title}</td>
                    <td className="py-3 pr-4 text-gray-600">{entry.template}</td>
                    <td className="py-3 text-gray-500 whitespace-nowrap">
                      {new Date(entry.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
