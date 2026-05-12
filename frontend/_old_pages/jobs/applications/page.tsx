'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Briefcase, CheckCircle2, Clock, XCircle, ExternalLink } from 'lucide-react'

interface Application {
  id: number
  job_title: string
  company: string
  location: string
  status: string
  applied_at: string
  job_url: string
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchApplications()
  }, [])

  const fetchApplications = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs/applications')
      if (response.ok) {
        const data = await response.json()
        setApplications(data.applications || [])
      }
    } catch (error) {
      console.error('Error fetching applications:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'applied':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'pending':
        return <Clock className="w-5 h-5 text-orange-500" />
      case 'rejected':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'pending':
        return 'bg-orange-50 text-orange-700 border-orange-200'
      case 'rejected':
        return 'bg-red-50 text-red-700 border-red-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const filteredApplications = applications.filter(app => {
    if (filter === 'all') return true
    return app.status === filter
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-gray-600">Loading applications...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="btn-secondary">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-3">
                <Briefcase className="w-8 h-8 text-green-600" />
                <h1 className="text-2xl font-bold text-gray-900">My Applications</h1>
              </div>
            </div>
            <Link href="/jobs/search" className="btn-primary">
              Search More Jobs
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <p className="text-sm text-gray-600">Total Applications</p>
            <p className="text-3xl font-bold text-gray-900">{applications.length}</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Applied</p>
            <p className="text-3xl font-bold text-green-600">
              {applications.filter(a => a.status === 'applied').length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Pending</p>
            <p className="text-3xl font-bold text-orange-600">
              {applications.filter(a => a.status === 'pending').length}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600">Response Rate</p>
            <p className="text-3xl font-bold text-purple-600">
              {applications.length > 0
                ? Math.round((applications.filter(a => a.status === 'applied').length / applications.length) * 100)
                : 0}%
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-2">
              {['all', 'applied', 'pending', 'rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === status
                      ? 'bg-linkedin-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="space-y-4">
          {filteredApplications.length === 0 ? (
            <div className="card text-center py-12">
              <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
              <p className="text-gray-600 mb-6">
                {filter === 'all'
                  ? 'Start applying to jobs to see them here'
                  : `No ${filter} applications yet`}
              </p>
              <Link href="/jobs/search" className="btn-primary inline-block">
                Search Jobs
              </Link>
            </div>
          ) : (
            filteredApplications.map((application) => (
              <div key={application.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(application.status)}
                      <h3 className="text-lg font-bold text-gray-900">
                        {application.job_title}
                      </h3>
                    </div>
                    <p className="text-gray-700 mb-2">{application.company}</p>
                    <p className="text-sm text-gray-600 mb-4">{application.location}</p>
                    <div className="flex items-center space-x-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(application.status)}`}>
                        {application.status.charAt(0).toUpperCase() + application.status.slice(1)}
                      </span>
                      <span className="text-sm text-gray-600">
                        Applied {new Date(application.applied_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <a
                    href={application.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary ml-4"
                  >
                    <ExternalLink className="w-5 h-5" />
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
