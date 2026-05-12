'use client'

import { useState, useEffect, Fragment } from 'react'
import { ArrowLeft, Star, TrendingUp, Filter, ExternalLink, Loader2, BarChart3, Award } from 'lucide-react'
import Link from 'next/link'

interface Evaluation {
  job_url: string
  job_title: string
  company: string
  overall_score: number
  grade: string
  gate_pass: boolean
  dimensions: Record<string, number>
  reasoning: string
  evaluated_at: string
}

const GRADE_COLORS: Record<string, string> = {
  A: 'bg-green-500 text-white',
  B: 'bg-blue-500 text-white',
  C: 'bg-yellow-500 text-black',
  D: 'bg-orange-500 text-white',
  F: 'bg-red-500 text-white',
}

const DIMENSION_LABELS: Record<string, string> = {
  role_match: 'Role Match',
  skills_alignment: 'Skills Alignment',
  seniority_fit: 'Seniority Fit',
  compensation: 'Compensation',
  interview_likelihood: 'Interview Likelihood',
  growth_potential: 'Growth Potential',
  company_reputation: 'Company Reputation',
  location_fit: 'Location Fit',
  tech_stack_match: 'Tech Stack Match',
  culture_signals: 'Culture Signals',
}

export default function JobEvaluations() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([])
  const [loading, setLoading] = useState(true)
  const [filterGrade, setFilterGrade] = useState('')
  const [expandedJob, setExpandedJob] = useState<string | null>(null)

  useEffect(() => {
    fetchEvaluations()
  }, [filterGrade])

  const fetchEvaluations = async () => {
    setLoading(true)
    try {
      const url = filterGrade
        ? `http://localhost:8000/api/jobs/evaluations?min_grade=${filterGrade}`
        : 'http://localhost:8000/api/jobs/evaluations'
      const res = await fetch(url)
      const data = await res.json()
      if (data.evaluations) setEvaluations(data.evaluations)
    } catch (err) {
      console.error('Failed to load evaluations:', err)
    } finally {
      setLoading(false)
    }
  }

  const gradeCounts = evaluations.reduce((acc, ev) => {
    acc[ev.grade] = (acc[ev.grade] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-6">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 -mx-6 -mt-6 mb-8 px-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-600 hover:text-gray-900">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold">Job Evaluations</h1>
              <p className="text-gray-600 text-sm">{evaluations.length} jobs scored on 10 dimensions</p>
            </div>
          </div>
        </div>
      </header>

      {/* Grade Summary Cards */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        {['A', 'B', 'C', 'D', 'F'].map(grade => (
          <button
            key={grade}
            onClick={() => setFilterGrade(filterGrade === grade ? '' : grade)}
            className={`p-4 rounded-xl border text-center transition-all ${
              filterGrade === grade ? 'border-blue-500 ring-2 ring-blue-500/30' : 'border-gray-200'
            } bg-white shadow-sm hover:bg-gray-50`}
          >
            <div className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-lg font-bold mb-2 ${GRADE_COLORS[grade]}`}>
              {grade}
            </div>
            <div className="text-2xl font-bold">{gradeCounts[grade] || 0}</div>
            <div className="text-xs text-gray-600">
              {grade === 'A' ? 'Excellent' : grade === 'B' ? 'Good' : grade === 'C' ? 'Fair' : grade === 'D' ? 'Poor' : 'Reject'}
            </div>
          </button>
        ))}
      </div>

      {/* Evaluations Table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-gray-500" />
          </div>
        ) : evaluations.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No evaluations yet. Run a portal scan or search first.</p>
          </div>
        ) : (
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-gray-200 text-gray-600 text-xs uppercase">
                <th className="p-4">Grade</th>
                <th className="p-4">Score</th>
                <th className="p-4">Job Title</th>
                <th className="p-4">Company</th>
                <th className="p-4">Gate Pass</th>
                <th className="p-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {evaluations.map((ev, i) => (
                <Fragment key={ev.job_url || i}>
                  <tr
                    className="border-b border-gray-200/50 hover:bg-gray-50 cursor-pointer"
                    onClick={() => setExpandedJob(expandedJob === ev.job_url ? null : ev.job_url)}
                  >
                    <td className="p-4">
                      <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${GRADE_COLORS[ev.grade]}`}>
                        {ev.grade}
                      </span>
                    </td>
                    <td className="p-4 font-mono">{ev.overall_score?.toFixed(1)}</td>
                    <td className="p-4 font-medium">{ev.job_title || 'Unknown'}</td>
                    <td className="p-4 text-gray-600">{ev.company || 'Unknown'}</td>
                    <td className="p-4">
                      {ev.gate_pass ? (
                        <span className="text-green-400 text-sm">Pass</span>
                      ) : (
                        <span className="text-red-400 text-sm">Fail</span>
                      )}
                    </td>
                    <td className="p-4">
                      {ev.job_url && (
                        <a
                          href={ev.job_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300"
                          onClick={e => e.stopPropagation()}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </td>
                  </tr>
                  {/* Expanded Dimension Scores */}
                  {expandedJob === ev.job_url && (
                    <tr key={`${ev.job_url}-expanded`}>
                      <td colSpan={6} className="p-4 bg-gray-50">
                        <div className="grid grid-cols-5 gap-3">
                          {Object.entries(ev.dimensions || {}).map(([dim, score]) => (
                            <div key={dim} className="text-center">
                              <div className="text-xs text-gray-600 mb-1">{DIMENSION_LABELS[dim] || dim}</div>
                              <div className="w-full bg-gray-200 rounded-full h-2 mb-1">
                                <div
                                  className={`h-2 rounded-full ${
                                    score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-blue-500' : score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${score}%` }}
                                />
                              </div>
                              <div className="text-sm font-mono">{typeof score === 'number' ? score.toFixed(0) : score}</div>
                            </div>
                          ))}
                        </div>
                        {ev.reasoning && (
                          <p className="text-sm text-gray-600 mt-3 italic">{ev.reasoning}</p>
                        )}
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
