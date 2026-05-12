'use client'

import { useState } from 'react'
import {
  FileText,
  Briefcase,
  TrendingUp,
  Settings,
  Github,
  Sparkles,
  CheckCircle2,
  Clock,
  Users
} from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [stats] = useState({
    posts_this_week: 3,
    applications_this_week: 25,
    avg_engagement: 5.2,
    interviews_scheduled: 1
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-linkedin-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">
                LinkedIn Automation Suite
              </h1>
            </div>
            <Link href="/settings" className="btn-primary">
              <Settings className="w-5 h-5 inline mr-2" />
              Settings
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Posts This Week</p>
                <p className="text-3xl font-bold text-linkedin-600">{stats.posts_this_week}</p>
              </div>
              <FileText className="w-12 h-12 text-linkedin-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Applications</p>
                <p className="text-3xl font-bold text-green-600">{stats.applications_this_week}</p>
              </div>
              <Briefcase className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Engagement</p>
                <p className="text-3xl font-bold text-purple-600">{stats.avg_engagement}%</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Interviews</p>
                <p className="text-3xl font-bold text-orange-600">{stats.interviews_scheduled}</p>
              </div>
              <Users className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Content Engine */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Content Engine</h2>
              <FileText className="w-6 h-6 text-linkedin-500" />
            </div>

            <p className="text-gray-600 mb-6">
              AI-powered LinkedIn content generation from your GitHub activity
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-center p-3 bg-blue-50 rounded-lg">
                <Github className="w-5 h-5 text-blue-600 mr-3" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">GitHub Monitor</p>
                  <p className="text-sm text-gray-600">Tracking commits & PRs</p>
                </div>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>

              <div className="flex items-center p-3 bg-purple-50 rounded-lg">
                <Sparkles className="w-5 h-5 text-purple-600 mr-3" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">AI Generation</p>
                  <p className="text-sm text-gray-600">3 posts ready</p>
                </div>
                <Clock className="w-5 h-5 text-orange-500" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Link href="/content/queue" className="btn-primary text-center">
                Review Posts
              </Link>
              <Link href="/content/published" className="btn-secondary text-center">
                Analytics
              </Link>
            </div>
          </div>

          {/* Job Applier */}
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Job Applier</h2>
              <Briefcase className="w-6 h-6 text-green-600" />
            </div>

            <p className="text-gray-600 mb-6">
              Smart job search and automated Easy Apply applications
            </p>

            <div className="space-y-4 mb-6">
              <div className="flex items-center p-3 bg-green-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600 mr-3" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">25 Applications</p>
                  <p className="text-sm text-gray-600">This week</p>
                </div>
                <span className="text-sm font-medium text-green-600">+12%</span>
              </div>

              <div className="flex items-center p-3 bg-orange-50 rounded-lg">
                <Users className="w-5 h-5 text-orange-600 mr-3" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">3 Responses</p>
                  <p className="text-sm text-gray-600">12% response rate</p>
                </div>
                <CheckCircle2 className="w-5 h-5 text-green-500" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Link href="/jobs/search" className="btn-primary text-center">
                Search Jobs
              </Link>
              <Link href="/jobs/applications" className="btn-secondary text-center">
                Applications
              </Link>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            <div className="flex items-center p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Applied to Senior React Developer at Microsoft</p>
                <p className="text-sm text-gray-600">2 hours ago</p>
              </div>
            </div>

            <div className="flex items-center p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Posted "Why I switched from REST to GraphQL"</p>
                <p className="text-sm text-gray-600">5 hours ago</p>
              </div>
            </div>

            <div className="flex items-center p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">Generated 3 new post ideas from GitHub commits</p>
                <p className="text-sm text-gray-600">1 day ago</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
