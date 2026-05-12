'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, Upload, Check, Edit2, Save, User, Briefcase, GraduationCap, Code, Award, Loader, FileText } from 'lucide-react'
import Link from 'next/link'

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/profile/get')
      const data = await response.json()

      if (data.success) {
        setProfile(data.profile)
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      alert('Please upload a PDF file')
      return
    }

    setUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/profile/upload-resume', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setProfile(data.profile)
        alert('✓ Resume parsed successfully! Review and edit your profile below.')
      } else {
        alert(data.message || 'Failed to parse resume')
      }
    } catch (error) {
      alert('Error uploading resume')
    } finally {
      setUploading(false)
    }
  }

  const handleSaveProfile = async () => {
    setSaving(true)

    try {
      const response = await fetch('http://localhost:8000/api/profile/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile)
      })

      const data = await response.json()

      if (data.success) {
        setProfile(data.profile)
        setEditing(false)
        alert('✓ Profile saved successfully!')
      } else {
        alert(data.message || 'Failed to save profile')
      }
    } catch (error) {
      alert('Error saving profile')
    } finally {
      setSaving(false)
    }
  }

  const updateField = (field: string, value: any) => {
    setProfile({ ...profile, [field]: value })
  }

  const updateNestedField = (parent: string, field: string, value: any) => {
    setProfile({
      ...profile,
      [parent]: {
        ...profile[parent],
        [field]: value
      }
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader className="w-8 h-8 animate-spin text-linkedin-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">AI Profile Builder</h1>
            </div>

            {profile && (
              <div className="flex items-center space-x-3">
                {!editing ? (
                  <button
                    onClick={() => setEditing(true)}
                    className="px-4 py-2 bg-linkedin-600 hover:bg-linkedin-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Edit2 className="w-4 h-4" />
                    <span>Edit Profile</span>
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => setEditing(false)}
                      className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveProfile}
                      disabled={saving}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50"
                    >
                      {saving ? (
                        <>
                          <Loader className="w-4 h-4 animate-spin" />
                          <span>Saving...</span>
                        </>
                      ) : (
                        <>
                          <Save className="w-4 h-4" />
                          <span>Save Profile</span>
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!profile ? (
          // Upload Section
          <div className="card text-center py-12">
            <div className="mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-linkedin-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Resume</h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Our AI will intelligently parse your resume and extract all relevant information including
                experience, skills, achievements, projects, and education. You can review and edit everything before
                generating LinkedIn posts.
              </p>
            </div>

            <div className="max-w-md mx-auto">
              <label className="block">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
                <div className="px-8 py-4 bg-gradient-to-r from-linkedin-600 to-purple-600 hover:from-linkedin-700 hover:to-purple-700 text-white font-bold rounded-lg cursor-pointer transition-all flex items-center justify-center space-x-3">
                  {uploading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Parsing Resume with AI...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      <span>Upload Resume (PDF)</span>
                    </>
                  )}
                </div>
              </label>

              <p className="text-sm text-gray-500 mt-4">
                Supported format: PDF only. Your data is processed securely and never shared.
              </p>
            </div>

            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
              <div className="p-4 bg-blue-50 rounded-lg">
                <Code className="w-8 h-8 text-blue-600 mb-2 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-1">Smart Extraction</h3>
                <p className="text-sm text-gray-600">AI adapts to your resume format and headings</p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <Edit2 className="w-8 h-8 text-purple-600 mb-2 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-1">Review & Edit</h3>
                <p className="text-sm text-gray-600">Verify and customize all extracted data</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <Check className="w-8 h-8 text-green-600 mb-2 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-1">Generate Posts</h3>
                <p className="text-sm text-gray-600">AI uses your real data to create authentic posts</p>
              </div>
            </div>
          </div>
        ) : (
          // Profile Display/Edit Section
          <div className="space-y-6">
            {/* Personal Info */}
            <div className="card">
              <div className="flex items-center mb-4">
                <User className="w-6 h-6 text-linkedin-600 mr-2" />
                <h2 className="text-xl font-bold text-gray-900">Personal Information</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={profile.name || ''}
                      onChange={(e) => updateField('name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.name || 'Not provided'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  {editing ? (
                    <input
                      type="email"
                      value={profile.email || ''}
                      onChange={(e) => updateField('email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.email || 'Not provided'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                  {editing ? (
                    <input
                      type="text"
                      value={profile.phone || ''}
                      onChange={(e) => updateField('phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.phone || 'Not provided'}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  {editing ? (
                    <input
                      type="text"
                      value={profile.location || ''}
                      onChange={(e) => updateField('location', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                    />
                  ) : (
                    <p className="text-gray-900">{profile.location || 'Not provided'}</p>
                  )}
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Professional Summary</label>
                {editing ? (
                  <textarea
                    value={profile.summary || ''}
                    onChange={(e) => updateField('summary', e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                  />
                ) : (
                  <p className="text-gray-700 whitespace-pre-line">{profile.summary || 'Not provided'}</p>
                )}
              </div>
            </div>

            {/* Experience */}
            {profile.experience && profile.experience.length > 0 && (
              <div className="card">
                <div className="flex items-center mb-4">
                  <Briefcase className="w-6 h-6 text-linkedin-600 mr-2" />
                  <h2 className="text-xl font-bold text-gray-900">Work Experience</h2>
                  <span className="ml-auto px-3 py-1 bg-linkedin-100 text-linkedin-700 rounded-full text-sm font-medium">
                    {profile.total_experience_display || `${profile.total_experience_months} months` || `${profile.total_experience_years} years`}
                  </span>
                </div>

                <div className="space-y-4">
                  {profile.experience.map((exp: any, idx: number) => (
                    <div key={idx} className="p-4 bg-gray-50 rounded-lg border-l-4 border-linkedin-500">
                      <h3 className="font-bold text-gray-900">{exp.title}</h3>
                      <p className="text-linkedin-600 font-medium">{exp.company}</p>
                      <p className="text-sm text-gray-600">
                        {exp.start_date} - {exp.end_date} • {exp.duration_display || exp.duration || `${exp.duration_months} months`}
                      </p>

                      {exp.responsibilities && exp.responsibilities.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Responsibilities:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {exp.responsibilities.map((resp: string, i: number) => (
                              <li key={i} className="text-sm text-gray-600">{resp}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {exp.achievements && exp.achievements.length > 0 && (
                        <div className="mt-3">
                          <p className="text-sm font-medium text-gray-700 mb-2">Key Achievements:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {exp.achievements.map((achievement: string, i: number) => (
                              <li key={i} className="text-sm text-gray-600">{achievement}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {exp.technologies && exp.technologies.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {exp.technologies.map((tech: string, i: number) => (
                            <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Skills */}
            {profile.skills && (
              <div className="card">
                <div className="flex items-center mb-4">
                  <Code className="w-6 h-6 text-linkedin-600 mr-2" />
                  <h2 className="text-xl font-bold text-gray-900">Skills</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {profile.skills.programming && profile.skills.programming.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Programming Languages</h3>
                      <div className="flex flex-wrap gap-2">
                        {profile.skills.programming.map((skill: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {profile.skills.frameworks && profile.skills.frameworks.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Frameworks & Libraries</h3>
                      <div className="flex flex-wrap gap-2">
                        {profile.skills.frameworks.map((skill: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {profile.skills.tools && profile.skills.tools.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Tools & Technologies</h3>
                      <div className="flex flex-wrap gap-2">
                        {profile.skills.tools.map((skill: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Projects */}
            {profile.projects && profile.projects.length > 0 && (
              <div className="card">
                <div className="flex items-center mb-4">
                  <Code className="w-6 h-6 text-linkedin-600 mr-2" />
                  <h2 className="text-xl font-bold text-gray-900">Projects</h2>
                  <span className="ml-auto px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                    {profile.total_projects_count || profile.projects.length} projects
                  </span>
                </div>

                <div className="space-y-4">
                  {profile.projects.map((project: any, idx: number) => (
                    <div key={idx} className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                      <div className="flex items-start justify-between">
                        <h3 className="font-bold text-gray-900">{project.name}</h3>
                        {project.link && (
                          <a
                            href={project.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-linkedin-600 hover:text-linkedin-700 text-sm underline"
                          >
                            View Project
                          </a>
                        )}
                      </div>

                      <p className="text-gray-700 mt-2 leading-relaxed">{project.description}</p>

                      {project.role && (
                        <p className="text-sm text-gray-600 mt-2">
                          <span className="font-medium">Role:</span> {project.role}
                        </p>
                      )}

                      {project.outcomes && project.outcomes.length > 0 && (
                        <div className="mt-2">
                          <p className="text-sm font-medium text-gray-700 mb-1">Outcomes:</p>
                          <ul className="list-disc list-inside space-y-1">
                            {project.outcomes.map((outcome: string, i: number) => (
                              <li key={i} className="text-sm text-gray-600">{outcome}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {project.technologies && project.technologies.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {project.technologies.map((tech: string, i: number) => (
                            <span key={i} className="px-2 py-1 bg-white text-purple-700 text-xs rounded border border-purple-300">
                              {tech}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Achievements */}
            {profile.achievements && profile.achievements.length > 0 && (
              <div className="card">
                <div className="flex items-center mb-4">
                  <Award className="w-6 h-6 text-linkedin-600 mr-2" />
                  <h2 className="text-xl font-bold text-gray-900">Achievements & Awards</h2>
                </div>

                <ul className="space-y-2">
                  {profile.achievements.map((achievement: string, idx: number) => (
                    <li key={idx} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{achievement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Education */}
            {profile.education && profile.education.length > 0 && (
              <div className="card">
                <div className="flex items-center mb-4">
                  <GraduationCap className="w-6 h-6 text-linkedin-600 mr-2" />
                  <h2 className="text-xl font-bold text-gray-900">Education</h2>
                </div>

                <div className="space-y-4">
                  {profile.education.map((edu: any, idx: number) => (
                    <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                      <h3 className="font-bold text-gray-900">{edu.degree} in {edu.major}</h3>
                      <p className="text-linkedin-600 font-medium">{edu.institution}</p>
                      <p className="text-sm text-gray-600">Graduated: {edu.graduation_year}</p>
                      {edu.gpa && <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            <div className="card bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200">
              <h3 className="font-bold text-gray-900 mb-3 flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                Profile Ready!
              </h3>
              <p className="text-gray-700 mb-4">
                Your profile has been successfully parsed. Now you can generate personalized LinkedIn posts using your real
                achievements, skills, and experience!
              </p>
              <Link
                href="/content/kickstart"
                className="inline-block px-6 py-3 bg-gradient-to-r from-linkedin-600 to-purple-600 hover:from-linkedin-700 hover:to-purple-700 text-white font-bold rounded-lg transition-all"
              >
                Generate 50+ LinkedIn Posts →
              </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
