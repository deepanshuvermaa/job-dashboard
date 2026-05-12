'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Sparkles, Zap, FileText, X } from 'lucide-react'

export default function LinkedInKickstartPage() {
  const [questions, setQuestions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState<any>(null)
  const [hasProfile, setHasProfile] = useState(false)

  // User context form
  const [industry, setIndustry] = useState('Full Stack Development')
  const [achievements, setAchievements] = useState('')
  const [notes, setNotes] = useState('')
  const [numPosts, setNumPosts] = useState(50)
  const [tone, setTone] = useState('conversational')
  const [length, setLength] = useState('medium')
  const [selectedQuestions, setSelectedQuestions] = useState<number[]>([])

  const [generating, setGenerating] = useState(false)
  const [generatedPosts, setGeneratedPosts] = useState<any[]>([])
  const [currentlyGenerating, setCurrentlyGenerating] = useState(0)
  const [showPreview, setShowPreview] = useState(false)
  const [editingPostIndex, setEditingPostIndex] = useState<number | null>(null)
  const [editedContent, setEditedContent] = useState('')

  useEffect(() => {
    fetchQuestions()
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/profile/get')
      const data = await response.json()

      if (data.success) {
        setProfile(data.profile)
        setHasProfile(true)

        // Pre-fill form with profile data
        if (data.profile.primary_industry) {
          setIndustry(data.profile.primary_industry)
        }
        if (data.profile.achievements && data.profile.achievements.length > 0) {
          setAchievements(data.profile.achievements.join('\n'))
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
    }
  }

  const fetchQuestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/content/questions')
      const data = await response.json()
      setQuestions(data.questions || [])
    } catch (error) {
      console.error('Error fetching questions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleQuestion = (id: number) => {
    setSelectedQuestions(prev =>
      prev.includes(id)
        ? prev.filter(qid => qid !== id)
        : [...prev, id]
    )
  }

  const handleGenerateBulkPosts = async () => {
    setGenerating(true)
    setGeneratedPosts([])
    setShowPreview(true)
    setCurrentlyGenerating(0)

    const posts: any[] = []

    // Get questions to use
    const questionsToUse = selectedQuestions.length > 0
      ? questions.filter((q: any) => selectedQuestions.includes(q.id))
      : questions

    // Cycle through questions to reach numPosts
    const questionsForGeneration = []
    while (questionsForGeneration.length < numPosts) {
      questionsForGeneration.push(...questionsToUse)
    }
    const finalQuestions = questionsForGeneration.slice(0, numPosts)

    // Generate posts one by one
    for (let i = 0; i < finalQuestions.length; i++) {
      setCurrentlyGenerating(i + 1)

      try {
        const response = await fetch('http://localhost:8000/api/content/generate-single-post', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: finalQuestions[i].question,
            industry,
            achievements,
            notes,
            tone,
            length
          })
        })

        if (response.ok) {
          const data = await response.json()
          const newPost = {
            id: i + 1,
            question: finalQuestions[i].question,
            content: data.content,
            tone,
            length
          }
          posts.push(newPost)
          setGeneratedPosts([...posts])
        }
      } catch (error) {
        console.error(`Error generating post ${i + 1}:`, error)
      }
    }

    setGenerating(false)
    setCurrentlyGenerating(0)
  }

  const handleEditPost = (index: number) => {
    setEditingPostIndex(index)
    setEditedContent(generatedPosts[index].content)
  }

  const handleSaveEdit = () => {
    if (editingPostIndex !== null) {
      const updated = [...generatedPosts]
      updated[editingPostIndex].content = editedContent
      setGeneratedPosts(updated)
      setEditingPostIndex(null)
    }
  }

  const handleRegeneratePost = async (index: number) => {
    const post = generatedPosts[index]

    try {
      const response = await fetch('http://localhost:8000/api/content/generate-single-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: post.question,
          industry,
          achievements,
          notes,
          tone,
          length
        })
      })

      if (response.ok) {
        const data = await response.json()
        const updated = [...generatedPosts]
        updated[index].content = data.content
        setGeneratedPosts(updated)
      }
    } catch (error) {
      console.error('Error regenerating post:', error)
    }
  }

  const handleDeletePost = (index: number) => {
    const updated = generatedPosts.filter((_, i) => i !== index)
    setGeneratedPosts(updated)
  }

  const handleSaveAllToQueue = async () => {
    if (generatedPosts.length === 0) {
      alert('No posts to save')
      return
    }

    if (!confirm(`Save ${generatedPosts.length} posts to Content Queue?`)) {
      return
    }

    try {
      // Save each post to backend
      for (const post of generatedPosts) {
        await fetch('http://localhost:8000/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            content: post.content,
            pillar: 'linkedin_questions',
            status: 'pending'
          })
        })
      }

      alert(`✅ Successfully saved ${generatedPosts.length} posts to Content Queue!\n\nGo to Review Posts to publish them to LinkedIn.`)
      setShowPreview(false)
      setGeneratedPosts([])
    } catch (error) {
      alert('Error saving posts to queue')
      console.error('Error:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50">
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/content/sources" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">LinkedIn Content Kickstart</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Generate 50+ authentic, human-sounding LinkedIn posts
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Status Banner */}
        {hasProfile ? (
          <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">Profile Loaded: {profile?.name}</h3>
                  <p className="text-sm text-gray-600">
                    Using your resume data • {profile?.total_experience_years} years experience • {profile?.skills?.programming?.length || 0} skills
                  </p>
                </div>
              </div>
              <Link
                href="/profile"
                className="px-4 py-2 bg-white hover:bg-gray-50 text-linkedin-600 font-medium rounded-lg transition-colors border border-linkedin-300"
              >
                View/Edit Profile
              </Link>
            </div>
          </div>
        ) : (
          <div className="mb-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">No Resume Profile Uploaded</h3>
                  <p className="text-sm text-gray-600">
                    Upload your resume for AI to generate highly personalized posts using your real achievements
                  </p>
                </div>
              </div>
              <Link
                href="/profile"
                className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white font-bold rounded-lg transition-colors"
              >
                Upload Resume
              </Link>
            </div>
          </div>
        )}

        {/* User Context Form */}
        <div className="card mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
            Your Profile & Preferences
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Industry / Field
              </label>
              <input
                type="text"
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                placeholder="e.g., Full Stack Development, Data Science"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Number of Posts
              </label>
              <input
                type="number"
                value={numPosts}
                onChange={(e) => setNumPosts(parseInt(e.target.value))}
                min={10}
                max={100}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Achievements (optional)
              </label>
              <textarea
                value={achievements}
                onChange={(e) => setAchievements(e.target.value)}
                placeholder="e.g., Built SaaS platforms, scaled to 100+ users, improved ROI by 60%"
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Notes (optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="e.g., Passionate about AI automation, Recent CS graduate"
                rows={2}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tone
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="conversational">Conversational</option>
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="inspirational">Inspirational</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Length
              </label>
              <select
                value={length}
                onChange={(e) => setLength(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="short">Short (150-200 words)</option>
                <option value="medium">Medium (200-300 words)</option>
                <option value="long">Long (300-400 words)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Question Selection (Optional) */}
        <div className="card mb-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-blue-600" />
            Question Bank (Optional - Select Specific Questions)
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Leave empty to use all 30 questions (cycles through for 50+ posts), or select specific ones
          </p>

          <div className="grid grid-cols-1 gap-2 max-h-96 overflow-y-auto">
            {questions.map((q) => (
              <div
                key={q.id}
                className={`p-3 border rounded-lg cursor-pointer transition-all ${
                  selectedQuestions.includes(q.id)
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleToggleQuestion(q.id)}
              >
                <div className="flex items-start space-x-3">
                  <input
                    type="checkbox"
                    checked={selectedQuestions.includes(q.id)}
                    onChange={() => {}}
                    className="mt-1 w-4 h-4"
                  />
                  <div className="flex-1">
                    <span className="text-sm text-gray-700">{q.question}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {selectedQuestions.length > 0 && (
            <div className="mt-4 flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedQuestions.length} question(s) selected
              </span>
              <button
                onClick={() => setSelectedQuestions([])}
                className="text-sm text-purple-600 hover:text-purple-800"
              >
                Clear Selection
              </button>
            </div>
          )}
        </div>

        {/* Generate Button */}
        <div className="flex justify-center">
          <button
            onClick={handleGenerateBulkPosts}
            disabled={generating}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold rounded-lg shadow-lg hover:from-purple-700 hover:to-blue-700 transition-all flex items-center space-x-3 disabled:opacity-50"
          >
            <Zap className="w-6 h-6" />
            <span>{generating ? `Generating ${numPosts} Posts...` : `Generate ${numPosts} LinkedIn Posts`}</span>
          </button>
        </div>

        {/* Info Box */}
        <div className="card mt-6 bg-blue-50 border-blue-200">
          <h3 className="font-bold text-blue-900 mb-2">What Makes These Posts Special?</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✓ Written in simple, conversational English (no corporate jargon)</li>
            <li>✓ Uses your actual resume data and experiences</li>
            <li>✓ No em dashes, minimal emojis, sounds human</li>
            <li>✓ Follows proven LinkedIn post structure (Hook, Insight, Takeaway, CTA)</li>
            <li>✓ Based on 30 high-impact questions that drive engagement</li>
            <li>✓ Saved to Content Queue for review before posting</li>
          </ul>
        </div>
      </main>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 overflow-y-auto">
          <div className="min-h-screen p-4">
            <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-2xl">
              {/* Header */}
              <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-linkedin-50 to-purple-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">Generated LinkedIn Posts</h2>
                    <p className="text-sm text-gray-600 mt-1">
                      {generating ? (
                        `Generating post ${currentlyGenerating}/${numPosts}...`
                      ) : (
                        `${generatedPosts.length} posts ready to review`
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowPreview(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                {generating && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-linkedin-600 to-purple-600 h-2 rounded-full transition-all"
                        style={{ width: `${(currentlyGenerating / numPosts) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Posts List */}
              <div className="p-6 max-h-[70vh] overflow-y-auto">
                {generatedPosts.length === 0 && !generating && (
                  <div className="text-center py-12 text-gray-500">
                    No posts generated yet
                  </div>
                )}

                <div className="space-y-4">
                  {generatedPosts.map((post, index) => (
                    <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-linkedin-300 transition-colors">
                      {/* Post Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-sm">Post #{post.id}</h3>
                          <p className="text-xs text-gray-500 mt-1">{post.question}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleEditPost(index)}
                            className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm rounded transition-colors"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleRegeneratePost(index)}
                            className="px-3 py-1 bg-purple-100 hover:bg-purple-200 text-purple-700 text-sm rounded transition-colors"
                          >
                            Regenerate
                          </button>
                          <button
                            onClick={() => handleDeletePost(index)}
                            className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 text-sm rounded transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </div>

                      {/* Post Content */}
                      {editingPostIndex === index ? (
                        <div>
                          <textarea
                            value={editedContent}
                            onChange={(e) => setEditedContent(e.target.value)}
                            rows={8}
                            className="w-full px-3 py-2 border-2 border-linkedin-500 rounded-lg focus:ring-2 focus:ring-linkedin-500 font-sans text-sm"
                          />
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500">{editedContent.length} characters</span>
                            <div className="flex space-x-2">
                              <button
                                onClick={() => setEditingPostIndex(null)}
                                className="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm rounded"
                              >
                                Cancel
                              </button>
                              <button
                                onClick={handleSaveEdit}
                                className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded"
                              >
                                Save
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-gray-50 p-3 rounded border border-gray-200">
                          <p className="text-sm text-gray-800 whitespace-pre-line">{post.content}</p>
                          <div className="mt-2 text-xs text-gray-500">{post.content.length} characters</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer Actions */}
              <div className="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
                <div className="text-sm text-gray-600">
                  {generatedPosts.length} posts ready
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => setGeneratedPosts([])}
                    disabled={generating}
                    className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg transition-colors disabled:opacity-50"
                  >
                    Clear All
                  </button>
                  <button
                    onClick={handleSaveAllToQueue}
                    disabled={generating || generatedPosts.length === 0}
                    className="px-6 py-2 bg-gradient-to-r from-linkedin-600 to-purple-600 hover:from-linkedin-700 hover:to-purple-700 text-white font-bold rounded-lg transition-all disabled:opacity-50"
                  >
                    Save All to Queue ({generatedPosts.length})
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
