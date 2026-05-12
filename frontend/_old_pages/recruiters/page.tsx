'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Send, User, MessageCircle, Briefcase, ExternalLink } from 'lucide-react'

interface Recruiter {
  name: string
  title: string
  profile_url: string
  dm_link: string
  connection_degree: string | null
  job_title?: string
  company?: string
}

export default function RecruitersPage() {
  const [applications, setApplications] = useState<any[]>([])
  const [recruiters, setRecruiters] = useState<Recruiter[]>([])
  const [loading, setLoading] = useState(true)
  const [sendingMessage, setSendingMessage] = useState(false)

  useEffect(() => {
    fetchApplicationsWithRecruiters()
  }, [])

  const fetchApplicationsWithRecruiters = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/applications')
      if (response.ok) {
        const data = await response.json()
        const apps = data.applications || []

        // Extract recruiters from applications
        const recruiterList: Recruiter[] = []
        apps.forEach((app: any) => {
          if (app.hr_name && app.hr_profile_url) {
            // Generate DM link from profile URL
            let dmLink = app.hr_profile_url
            if (app.hr_profile_url.includes('/in/')) {
              const profileId = app.hr_profile_url.split('/in/')[1].split('/')[0].split('?')[0]
              dmLink = `https://www.linkedin.com/messaging/compose/?recipient=${profileId}`
            }

            recruiterList.push({
              name: app.hr_name,
              title: 'Recruiter', // Can be enhanced with actual title
              profile_url: app.hr_profile_url,
              dm_link: dmLink,
              connection_degree: null,
              job_title: app.job_title,
              company: app.company
            })
          }
        })

        setApplications(apps)
        setRecruiters(recruiterList)
      }
    } catch (error) {
      console.error('Error fetching recruiters:', error)
    } finally {
      setLoading(false)
    }
  }

  const openDM = (dmLink: string) => {
    // Open LinkedIn DM in new tab
    window.open(dmLink, '_blank', 'noopener,noreferrer')
  }

  const sendBulkMessages = async () => {
    setSendingMessage(true)
    try {
      const response = await fetch('http://localhost:8000/api/messages/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_messages: recruiters.length,
          delay_seconds: 30
        })
      })

      const data = await response.json()
      if (data.success) {
        alert(`✅ Sending ${recruiters.length} personalized messages!\n\nMessages will be sent automatically.`)
      } else {
        alert(`❌ Failed to send messages: ${data.message || 'Unknown error'}`)
      }
    } catch (error) {
      alert('❌ Error sending messages: ' + error)
    } finally {
      setSendingMessage(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-gray-600">Loading recruiters...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-600 hover:text-linkedin-700">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <MessageCircle className="w-6 h-6 text-linkedin-700" />
                  Recruiter Connections
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                  {recruiters.length} recruiters available for outreach
                </p>
              </div>
            </div>

            {recruiters.length > 0 && (
              <button
                onClick={sendBulkMessages}
                disabled={sendingMessage}
                className="bg-linkedin-700 hover:bg-linkedin-800 text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
                {sendingMessage ? 'Sending...' : `Send AI Messages to All (${recruiters.length})`}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {recruiters.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm border p-12 text-center">
            <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Recruiters Found
            </h3>
            <p className="text-gray-500 mb-6">
              Search for jobs first to discover recruiters and hiring managers
            </p>
            <Link
              href="/jobs/search"
              className="inline-flex items-center gap-2 bg-linkedin-700 hover:bg-linkedin-800 text-white px-6 py-2 rounded-lg transition-all"
            >
              <Briefcase className="w-4 h-4" />
              Search Jobs
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recruiters.map((recruiter, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-sm border hover:shadow-md transition-all p-6"
              >
                {/* Recruiter Info */}
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-12 h-12 bg-linkedin-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-6 h-6 text-linkedin-700" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {recruiter.name}
                    </h3>
                    <p className="text-sm text-gray-500 truncate">
                      {recruiter.title}
                    </p>
                    {recruiter.connection_degree && (
                      <span className="inline-block mt-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded">
                        {recruiter.connection_degree}
                      </span>
                    )}
                  </div>
                </div>

                {/* Job Info */}
                {recruiter.job_title && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 mb-1">Hiring for:</p>
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {recruiter.job_title}
                    </p>
                    <p className="text-xs text-gray-600 truncate">
                      at {recruiter.company}
                    </p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => openDM(recruiter.dm_link)}
                    className="flex-1 bg-linkedin-700 hover:bg-linkedin-800 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 text-sm transition-all"
                  >
                    <MessageCircle className="w-4 h-4" />
                    Send DM
                  </button>
                  <a
                    href={recruiter.profile_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 border border-gray-300 hover:border-linkedin-700 hover:bg-linkedin-50 text-gray-700 rounded-lg flex items-center justify-center transition-all"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Text */}
        {recruiters.length > 0 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Tips for Messaging Recruiters</h4>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
              <li>Click "Send DM" to open LinkedIn messaging with the recruiter</li>
              <li>Use "Send AI Messages to All" to automatically generate and send personalized messages</li>
              <li>Keep messages concise, professional, and reference specific job postings</li>
              <li>Follow up within 3-5 days if no response</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
