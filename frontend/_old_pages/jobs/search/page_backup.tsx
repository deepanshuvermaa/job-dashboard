'use client'

import { useState } from 'react'
import { ArrowLeft, Search, MapPin, Briefcase, ExternalLink, Star, X } from 'lucide-react'
import Link from 'next/link'

export default function JobSearch() {
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('United States')
  const [searching, setSearching] = useState(false)
  const [jobs, setJobs] = useState<any[]>([])

  const handleSearch = async () => {
    setSearching(true)

    // Simulate API call
    setTimeout(() => {
      setJobs([
        {
          id: 1,
          title: 'Senior Full Stack Engineer',
          company: 'Microsoft',
          location: 'Redmond, WA',
          salary: '$140k - $180k',
          postedDays: 2,
          easyApply: true,
          relevanceScore: 0.92
        },
        {
          id: 2,
          title: 'React Developer',
          company: 'Amazon',
          location: 'Seattle, WA',
          salary: '$120k - $160k',
          postedDays: 1,
          easyApply: true,
          relevanceScore: 0.88
        },
        {
          id: 3,
          title: 'Software Engineer',
          company: 'Google',
          location: 'Mountain View, CA',
          salary: '$150k - $200k',
          postedDays: 3,
          easyApply: true,
          relevanceScore: 0.85
        }
      ])
      setSearching(false)
    }, 2000)
  }

  const handleApply = (jobId: number) => {
    alert('Application submitted!')
    setJobs(jobs.filter(j => j.id !== jobId))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-4">
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Job Search</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="card mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g. Full Stack Engineer, React Developer"
                  className="input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Location"
                  className="input pl-10"
                />
              </div>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={searching}
            className="btn-primary mt-4 w-full md:w-auto"
          >
            {searching ? 'Searching...' : 'Search Jobs'}
          </button>
        </div>

        {/* Results */}
        {jobs.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                {jobs.length} Jobs Found
              </h2>
              <p className="text-sm text-gray-600">Sorted by relevance</p>
            </div>

            <div className="space-y-4">
              {jobs.map(job => (
                <div key={job.id} className="card hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-bold text-gray-900">{job.title}</h3>
                        {job.easyApply && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                            Easy Apply
                          </span>
                        )}
                      </div>

                      <p className="text-gray-700 font-medium mb-2">{job.company}</p>

                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                        <span className="flex items-center">
                          <MapPin className="w-4 h-4 mr-1" />
                          {job.location}
                        </span>
                        <span className="flex items-center">
                          <Briefcase className="w-4 h-4 mr-1" />
                          {job.salary}
                        </span>
                        <span>{job.postedDays} days ago</span>
                      </div>

                      {/* Relevance Score */}
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-linkedin-500 h-2 rounded-full"
                            style={{ width: `${job.relevanceScore * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-linkedin-600">
                          {Math.round(job.relevanceScore * 100)}% match
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleApply(job.id)}
                        className="btn-primary"
                      >
                        Quick Apply
                      </button>
                      <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <ExternalLink className="w-5 h-5" />
                      </button>
                      <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {jobs.length === 0 && !searching && (
          <div className="card text-center py-12">
            <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">Enter keywords to search for jobs</p>
          </div>
        )}
      </main>
    </div>
  )
}
