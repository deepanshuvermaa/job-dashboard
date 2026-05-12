'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Github, Plus, Trash2, Play, Pause, RefreshCw, Search, Sparkles, FileText } from 'lucide-react'

interface GitHubRepo {
  id: number
  repo_name: string
  repo_url: string
  is_active: boolean
  last_synced: string
  post_count: number
  commits?: GitHubCommit[]
}

interface GitHubCommit {
  sha: string
  message: string
  author: string
  date: string
  days_ago: number
  url: string
}

interface AllRepo {
  name: string
  full_name: string
  description: string
  html_url: string
  language: string
  stars: number
  forks: number
  updated_at: string
  days_since_update: number
  is_private: boolean
  is_fork: boolean
}

export default function ContentSourcesPage() {
  const [repos, setRepos] = useState<GitHubRepo[]>([])
  const [loading, setLoading] = useState(true)
  const [newRepo, setNewRepo] = useState('')
  const [adding, setAdding] = useState(false)

  // Browse All Repos Modal
  const [showBrowseModal, setShowBrowseModal] = useState(false)
  const [allRepos, setAllRepos] = useState<AllRepo[]>([])
  const [loadingAllRepos, setLoadingAllRepos] = useState(false)
  const [selectedRepos, setSelectedRepos] = useState<string[]>([])

  // Create from Keywords Modal
  const [showKeywordsModal, setShowKeywordsModal] = useState(false)
  const [keywords, setKeywords] = useState('')
  const [tone, setTone] = useState('professional')
  const [length, setLength] = useState('medium')
  const [includeHashtags, setIncludeHashtags] = useState(true)
  const [includeEmoji, setIncludeEmoji] = useState(false)
  const [generatingPost, setGeneratingPost] = useState(false)

  // Generate from Commits
  const [generatingFromCommits, setGeneratingFromCommits] = useState(false)
  const [previewPost, setPreviewPost] = useState<{content: string, repoName: string, postId: number} | null>(null)
  const [editedContent, setEditedContent] = useState('')
  const [savingPost, setSavingPost] = useState(false)

  useEffect(() => {
    fetchRepos()
  }, [])

  const fetchRepos = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/content/sources')
      if (response.ok) {
        const data = await response.json()
        const reposWithCommits = await Promise.all(
          (data.sources || []).map(async (repo: GitHubRepo) => {
            try {
              const commitsResp = await fetch(`http://localhost:8000/api/content/sources/${repo.id}/commits?limit=30`)
              if (commitsResp.ok) {
                const commitsData = await commitsResp.json()
                return { ...repo, commits: commitsData.commits }
              }
            } catch (err) {
              console.error(`Error fetching commits for ${repo.repo_name}:`, err)
            }
            return repo
          })
        )
        setRepos(reposWithCommits)
      }
    } catch (error) {
      console.error('Error fetching repos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddRepo = async () => {
    if (!newRepo.trim()) return

    setAdding(true)
    try {
      const response = await fetch('http://localhost:8000/api/content/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: newRepo })
      })

      if (response.ok) {
        setNewRepo('')
        fetchRepos()
      }
    } catch (error) {
      console.error('Error adding repo:', error)
    } finally {
      setAdding(false)
    }
  }

  const handleToggleRepo = async (id: number, isActive: boolean) => {
    try {
      await fetch(`http://localhost:8000/api/content/sources/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !isActive })
      })
      fetchRepos()
    } catch (error) {
      console.error('Error toggling repo:', error)
    }
  }

  const handleDeleteRepo = async (id: number) => {
    if (!confirm('Are you sure you want to remove this repository?')) return

    try {
      await fetch(`http://localhost:8000/api/content/sources/${id}`, {
        method: 'DELETE'
      })
      fetchRepos()
    } catch (error) {
      console.error('Error deleting repo:', error)
    }
  }

  const handleSyncRepo = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/api/content/sources/${id}/sync`, {
        method: 'POST'
      })
      alert('Repository sync started! Check back in a few minutes.')
      fetchRepos()
    } catch (error) {
      console.error('Error syncing repo:', error)
    }
  }

  // Browse All Repos handlers
  const handleBrowseAllRepos = async () => {
    setShowBrowseModal(true)
    setLoadingAllRepos(true)
    try {
      const response = await fetch('http://localhost:8000/api/github/all-repos')
      if (response.ok) {
        const data = await response.json()
        setAllRepos(data.repos || [])
      } else {
        alert('Failed to fetch repositories. Make sure GitHub username is configured in settings.')
      }
    } catch (error) {
      console.error('Error fetching all repos:', error)
      alert('Error fetching repositories')
    } finally {
      setLoadingAllRepos(false)
    }
  }

  const handleToggleRepoSelection = (fullName: string) => {
    setSelectedRepos(prev =>
      prev.includes(fullName)
        ? prev.filter(r => r !== fullName)
        : [...prev, fullName]
    )
  }

  const handleAddSelectedRepos = async () => {
    if (selectedRepos.length === 0) {
      alert('Please select at least one repository')
      return
    }

    setAdding(true)
    try {
      const response = await fetch('http://localhost:8000/api/github/repos/add-multiple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedRepos)
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Successfully added ${data.added_count} repositories!`)
        setShowBrowseModal(false)
        setSelectedRepos([])
        fetchRepos()
      }
    } catch (error) {
      console.error('Error adding repos:', error)
      alert('Error adding repositories')
    } finally {
      setAdding(false)
    }
  }

  // Create Post from Keywords handlers
  const handleCreateFromKeywords = async () => {
    if (!keywords.trim()) {
      alert('Please enter keywords')
      return
    }

    setGeneratingPost(true)
    try {
      const response = await fetch('http://localhost:8000/api/content/create-from-keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords,
          tone,
          length,
          include_hashtags: includeHashtags,
          include_emoji: includeEmoji
        })
      })

      if (response.ok) {
        const data = await response.json()
        alert('Post created successfully! Check the Content Queue to review it.')
        setShowKeywordsModal(false)
        setKeywords('')
      } else {
        alert('Failed to generate post. Please try again.')
      }
    } catch (error) {
      console.error('Error creating post:', error)
      alert('Error generating post')
    } finally {
      setGeneratingPost(false)
    }
  }

  // Generate posts from commits
  const handleGenerateFromCommits = async () => {
    if (repos.filter(r => r.is_active).length === 0) {
      alert('No active repositories found. Add and activate repositories first.')
      return
    }

    if (!confirm('This will generate LinkedIn posts from recent commits in all active repositories. Continue?')) {
      return
    }

    setGeneratingFromCommits(true)
    try {
      const response = await fetch('http://localhost:8000/api/content/generate-from-commits', {
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()
        alert(`Generating posts from ${data.repo_count} repositories! Check the Content Queue in a few minutes.`)
        fetchRepos()
      } else {
        alert('Failed to generate posts. Please try again.')
      }
    } catch (error) {
      console.error('Error generating from commits:', error)
      alert('Error generating posts')
    } finally {
      setGeneratingFromCommits(false)
    }
  }

  // Generate post for individual repo
  const handleGenerateRepoPost = async (repoId: number, repoName: string) => {
    setGeneratingPost(true)
    try {
      const response = await fetch(`http://localhost:8000/api/content/sources/${repoId}/generate-post`, {
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()

        // Show preview modal with generated content
        setPreviewPost({
          content: data.content,
          repoName: repoName,
          postId: data.post_id
        })
        setEditedContent(data.content)
      } else {
        const error = await response.json()
        alert(`Failed: ${error.detail || 'Error generating post'}`)
      }
    } catch (error) {
      console.error('Error generating post:', error)
      alert('Error generating post')
    } finally {
      setGeneratingPost(false)
    }
  }

  const handleAcceptPost = () => {
    alert('✅ Post saved to Content Queue! Go to Review Posts to publish it.')
    setPreviewPost(null)
    fetchRepos()
  }

  const handleRejectPost = async () => {
    if (!confirm('Delete this post?')) return

    try {
      if (previewPost?.postId) {
        await fetch(`http://localhost:8000/api/posts/${previewPost.postId}`, {
          method: 'DELETE'
        })
      }
      setPreviewPost(null)
    } catch (error) {
      console.error('Error deleting post:', error)
    }
  }

  const handleSaveEdits = async () => {
    setSavingPost(true)
    try {
      if (previewPost?.postId) {
        await fetch(`http://localhost:8000/api/content/posts/${previewPost.postId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: editedContent })
        })

        alert('✅ Changes saved! Post updated in Content Queue.')
        setPreviewPost(null)
        fetchRepos()
      }
    } catch (error) {
      console.error('Error saving edits:', error)
      alert('Error saving changes')
    } finally {
      setSavingPost(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-gray-600">Loading sources...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="btn-secondary">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="flex items-center space-x-3">
                <Github className="w-8 h-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-gray-900">GitHub Content Sources</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <button
            onClick={handleBrowseAllRepos}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <Search className="w-5 h-5" />
            <span>Browse All My Repos</span>
          </button>

          <button
            onClick={() => setShowKeywordsModal(true)}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <Sparkles className="w-5 h-5" />
            <span>Create Post from Keywords</span>
          </button>

          <button
            onClick={handleGenerateFromCommits}
            disabled={generatingFromCommits}
            className="btn-primary flex items-center justify-center space-x-2"
          >
            <FileText className="w-5 h-5" />
            <span>{generatingFromCommits ? 'Generating...' : 'Generate from Commits'}</span>
          </button>
        </div>

        {/* Add New Repo */}
        <div className="card mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Add GitHub Repository</h2>
          <div className="flex space-x-3">
            <input
              type="text"
              value={newRepo}
              onChange={(e) => setNewRepo(e.target.value)}
              placeholder="username/repository or full GitHub URL"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleAddRepo()}
            />
            <button
              onClick={handleAddRepo}
              disabled={adding || !newRepo.trim()}
              className="btn-primary"
            >
              <Plus className="w-5 h-5 inline mr-2" />
              {adding ? 'Adding...' : 'Add Repo'}
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-2">
            Example: deepanshuverma966/linkedin-automation or https://github.com/user/repo
          </p>
        </div>

        {/* Repository List */}
        <div className="space-y-4">
          {repos.length === 0 ? (
            <div className="card text-center py-12">
              <Github className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No repositories added</h3>
              <p className="text-gray-600 mb-6">
                Add your first GitHub repository to start generating content from your commits and PRs
              </p>
            </div>
          ) : (
            repos.map((repo) => (
              <div key={repo.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Github className="w-6 h-6 text-blue-600" />
                      <h3 className="text-lg font-bold text-gray-900">{repo.repo_name}</h3>
                      {repo.is_active ? (
                        <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                          Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                          Paused
                        </span>
                      )}
                    </div>

                    <a
                      href={repo.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline mb-3 block"
                    >
                      {repo.repo_url}
                    </a>

                    <div className="flex items-center space-x-6 text-sm text-gray-600 mb-4">
                      <div>
                        <span className="font-medium">Posts Generated:</span> {repo.post_count}
                      </div>
                      <div>
                        <span className="font-medium">Last Synced:</span>{' '}
                        {repo.last_synced
                          ? new Date(repo.last_synced).toLocaleDateString()
                          : 'Never'}
                      </div>
                    </div>

                    {/* Recent Commits Section */}
                    {repo.commits && repo.commits.length > 0 && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <h4 className="text-xs font-semibold text-gray-700 mb-2">
                          📝 Last 5 Commits
                        </h4>
                        <div className="space-y-2">
                          {repo.commits.map((commit) => (
                            <div key={commit.sha} className="flex items-start text-xs">
                              <a
                                href={commit.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-1 hover:text-blue-600 transition-colors"
                              >
                                <div className="flex items-center space-x-2">
                                  <code className="px-1.5 py-0.5 bg-gray-200 text-gray-700 rounded font-mono">
                                    {commit.sha}
                                  </code>
                                  <span className="text-gray-600">{commit.message}</span>
                                </div>
                                <div className="flex items-center space-x-3 mt-1 text-gray-500">
                                  <span>by {commit.author}</span>
                                  <span>•</span>
                                  <span>{commit.days_ago === 0 ? 'today' : `${commit.days_ago} days ago`}</span>
                                </div>
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => handleGenerateRepoPost(repo.id, repo.repo_name)}
                      className="px-4 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 font-medium rounded-lg transition-colors flex items-center space-x-2"
                      title="Generate Post from This Repo"
                    >
                      <Sparkles className="w-5 h-5" />
                      <span className="text-sm">Generate Post</span>
                    </button>

                    <button
                      onClick={() => handleSyncRepo(repo.id)}
                      className="btn-secondary"
                      title="Sync Now"
                    >
                      <RefreshCw className="w-5 h-5" />
                    </button>

                    <button
                      onClick={() => handleToggleRepo(repo.id, repo.is_active)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        repo.is_active
                          ? 'bg-orange-100 hover:bg-orange-200 text-orange-700'
                          : 'bg-green-100 hover:bg-green-200 text-green-700'
                      }`}
                      title={repo.is_active ? 'Pause' : 'Activate'}
                    >
                      {repo.is_active ? (
                        <Pause className="w-5 h-5" />
                      ) : (
                        <Play className="w-5 h-5" />
                      )}
                    </button>

                    <button
                      onClick={() => handleDeleteRepo(repo.id)}
                      className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Info Box */}
        <div className="card mt-6 bg-blue-50 border-blue-200">
          <h3 className="font-bold text-blue-900 mb-2">How it works</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Add repositories you want to generate content from</li>
            <li>• Active repos are automatically monitored for new commits and PRs</li>
            <li>• AI generates LinkedIn posts based on your activity</li>
            <li>• Review and approve posts in the Content Queue</li>
            <li>• Pause repos anytime to stop generating content from them</li>
          </ul>
        </div>
      </main>

      {/* Browse All Repos Modal */}
      {showBrowseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Browse All Your Repositories</h2>
                <button
                  onClick={() => setShowBrowseModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {loadingAllRepos ? (
                <div className="text-center py-12">
                  <div className="text-gray-600">Loading repositories...</div>
                </div>
              ) : allRepos.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-600">No repositories found. Make sure your GitHub username is configured in settings.</div>
                </div>
              ) : (
                <div className="space-y-3">
                  {allRepos.map((repo) => (
                    <div
                      key={repo.full_name}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        selectedRepos.includes(repo.full_name)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleToggleRepoSelection(repo.full_name)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3">
                            <input
                              type="checkbox"
                              checked={selectedRepos.includes(repo.full_name)}
                              onChange={() => {}}
                              className="w-4 h-4"
                            />
                            <div>
                              <h3 className="font-bold text-gray-900">{repo.name}</h3>
                              <p className="text-sm text-gray-600 mt-1">{repo.description}</p>
                              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                                <span className="px-2 py-1 bg-gray-100 rounded">{repo.language || 'Unknown'}</span>
                                <span>⭐ {repo.stars}</span>
                                <span>Updated {repo.days_since_update} days ago</span>
                                {repo.is_private && <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded">Private</span>}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                {selectedRepos.length} repository(ies) selected
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowBrowseModal(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddSelectedRepos}
                  disabled={adding || selectedRepos.length === 0}
                  className="btn-primary"
                >
                  {adding ? 'Adding...' : `Add ${selectedRepos.length} Selected`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Post from Keywords Modal */}
      {showKeywordsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Create Post from Keywords</h2>
                <button
                  onClick={() => setShowKeywordsModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Keywords / Topic
                </label>
                <input
                  type="text"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., React Hooks, Machine Learning, Career Growth"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="technical">Technical</option>
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
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500"
                  >
                    <option value="short">Short (100-150 words)</option>
                    <option value="medium">Medium (150-250 words)</option>
                    <option value="long">Long (250-400 words)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={includeHashtags}
                    onChange={(e) => setIncludeHashtags(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">Include Hashtags</span>
                </label>

                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={includeEmoji}
                    onChange={(e) => setIncludeEmoji(e.target.checked)}
                    className="w-4 h-4"
                  />
                  <span className="text-sm text-gray-700">Include Emojis</span>
                </label>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex items-center justify-end space-x-3">
              <button
                onClick={() => setShowKeywordsModal(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateFromKeywords}
                disabled={generatingPost || !keywords.trim()}
                className="btn-primary"
              >
                {generatingPost ? 'Generating...' : 'Generate Post'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Post Preview Modal */}
      {previewPost && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-2xl font-bold text-gray-900">Generated LinkedIn Post</h3>
              <p className="text-sm text-gray-600 mt-1">
                From: {previewPost.repoName}
              </p>
            </div>

            <div className="p-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Preview & Edit:
              </label>
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                rows={12}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-linkedin-500 focus:border-transparent font-sans text-gray-900"
                placeholder="Edit your post here..."
              />
              <p className="text-sm text-gray-500 mt-2">
                {editedContent.length} characters
              </p>
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
              <button
                onClick={handleRejectPost}
                className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg transition-colors"
              >
                Delete Post
              </button>

              <div className="flex items-center space-x-3">
                <button
                  onClick={handleSaveEdits}
                  disabled={savingPost}
                  className="px-6 py-2 bg-linkedin-600 hover:bg-linkedin-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50"
                >
                  {savingPost ? 'Saving...' : 'Save Edits'}
                </button>
                <button
                  onClick={handleAcceptPost}
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition-colors"
                >
                  Accept & Add to Queue
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
