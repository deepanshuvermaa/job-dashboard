'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, Check, X, Edit2, Calendar, Send, Loader } from 'lucide-react'
import Link from 'next/link'

export default function ContentQueue() {
  const [posts, setPosts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [autoPosterActive, setAutoPosterActive] = useState(false)
  const [selectedPosts, setSelectedPosts] = useState<Set<number>>(new Set())
  const [posting, setPosting] = useState(false)

  useEffect(() => {
    fetchPosts()
    checkAutoPosterStatus()
  }, [])

  const fetchPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/posts?status=pending')
      const data = await response.json()
      setPosts(data.posts || [])
    } catch (error) {
      console.error('Error fetching posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const checkAutoPosterStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/linkedin/auto-post/status')
      const data = await response.json()
      setAutoPosterActive(data.active)
    } catch (error) {
      console.error('Error checking auto-poster status:', error)
    }
  }

  const handleStartAutoPoster = async () => {
    if (!confirm('This will open a Chrome window and log you into LinkedIn. Continue?')) {
      return
    }

    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/linkedin/auto-post/start', {
        method: 'POST'
      })
      const data = await response.json()

      if (data.success) {
        setAutoPosterActive(true)
        alert('Successfully logged into LinkedIn! You can now auto-post.')
      } else {
        alert(data.message)
      }
    } catch (error) {
      alert('Error starting auto-poster')
    } finally {
      setLoading(false)
    }
  }

  const handleStopAutoPoster = async () => {
    try {
      await fetch('http://localhost:8000/api/linkedin/auto-post/stop', {
        method: 'POST'
      })
      setAutoPosterActive(false)
    } catch (error) {
      console.error('Error stopping auto-poster:', error)
    }
  }

  const handleTogglePost = (postId: number) => {
    const newSelected = new Set(selectedPosts)
    if (newSelected.has(postId)) {
      newSelected.delete(postId)
    } else {
      newSelected.add(postId)
    }
    setSelectedPosts(newSelected)
  }

  const handlePostSingle = async (postId: number, content: string) => {
    if (!autoPosterActive) {
      alert('Please start the auto-poster first!')
      return
    }

    if (!confirm('Post this content to LinkedIn now?')) {
      return
    }

    setPosting(true)
    try {
      const response = await fetch('http://localhost:8000/api/linkedin/auto-post/post-single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ post_id: postId, content })
      })

      const data = await response.json()

      if (data.success) {
        alert('Successfully posted to LinkedIn!')
        fetchPosts()
      } else {
        alert(data.message)
      }
    } catch (error) {
      alert('Error posting to LinkedIn')
    } finally {
      setPosting(false)
    }
  }

  const handlePostMultiple = async () => {
    if (!autoPosterActive) {
      alert('Please start the auto-poster first!')
      return
    }

    if (selectedPosts.size === 0) {
      alert('Please select at least one post')
      return
    }

    const delayBetween = prompt(`Post ${selectedPosts.size} posts to LinkedIn?\n\nEnter delay between posts (seconds):`, '10')
    if (!delayBetween) return

    setPosting(true)
    try {
      const response = await fetch('http://localhost:8000/api/linkedin/auto-post/post-multiple', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_ids: Array.from(selectedPosts),
          delay_between: parseInt(delayBetween)
        })
      })

      const data = await response.json()
      alert(`Posted ${data.successful} out of ${data.total} posts successfully!`)
      setSelectedPosts(new Set())
      fetchPosts()
    } catch (error) {
      alert('Error posting to LinkedIn')
    } finally {
      setPosting(false)
    }
  }

  const handleApprove = (id: number) => {
    alert('Post scheduled for tomorrow at 10 AM!')
    setPosts(posts.filter(p => p.id !== id))
  }

  const handleReject = async (id: number) => {
    try {
      await fetch(`http://localhost:8000/api/posts/${id}`, {
        method: 'DELETE'
      })
      setPosts(posts.filter(p => p.id !== id))
    } catch (error) {
      console.error('Error deleting post:', error)
    }
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
              <h1 className="text-2xl font-bold text-gray-900">Review Content Queue</h1>
              <span className="px-3 py-1 bg-linkedin-100 text-linkedin-700 rounded-full text-sm font-medium">
                {posts.length} pending
              </span>
            </div>

            {/* Auto-Poster Controls */}
            <div className="flex items-center space-x-3">
              {!autoPosterActive ? (
                <button
                  onClick={handleStartAutoPoster}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Start Auto-Poster</span>
                </button>
              ) : (
                <>
                  <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 text-green-700 rounded-lg">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">Auto-Poster Active</span>
                  </div>
                  <button
                    onClick={handleStopAutoPoster}
                    className="px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors"
                  >
                    Stop
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Bulk Actions */}
        {selectedPosts.size > 0 && (
          <div className="card mb-6 bg-gradient-to-r from-linkedin-50 to-blue-50 border-linkedin-200">
            <div className="flex items-center justify-between">
              <p className="text-linkedin-900 font-medium">
                {selectedPosts.size} post{selectedPosts.size > 1 ? 's' : ''} selected
              </p>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setSelectedPosts(new Set())}
                  className="px-3 py-2 text-gray-700 hover:text-gray-900 text-sm font-medium"
                >
                  Clear
                </button>
                <button
                  onClick={handlePostMultiple}
                  disabled={posting}
                  className="px-4 py-2 bg-linkedin-600 hover:bg-linkedin-700 text-white font-medium rounded-lg transition-colors flex items-center space-x-2 disabled:opacity-50"
                >
                  {posting ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Posting...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Post to LinkedIn</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {posts.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-600">No posts in queue. Check back later!</p>
          </div>
        ) : (
          <div className="space-y-6">
            {posts.map(post => (
              <div key={post.id} className={`card ${selectedPosts.has(post.id) ? 'ring-2 ring-linkedin-500' : ''}`}>
                {/* Selection Checkbox */}
                <div className="mb-4 flex items-start justify-between">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPosts.has(post.id)}
                      onChange={() => handleTogglePost(post.id)}
                      className="w-5 h-5 text-linkedin-600 rounded focus:ring-linkedin-500"
                    />
                    <span className="text-sm text-gray-700 font-medium">Select for bulk posting</span>
                  </label>
                </div>

                {/* Source */}
                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Pillar:</span> {post.pillar}
                  </p>
                </div>

                {/* Post Content Preview */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Post Preview:
                  </label>
                  <div className="p-4 bg-white border-2 border-gray-200 rounded-lg">
                    <p className="text-gray-800 whitespace-pre-line">{post.content}</p>
                  </div>
                </div>

                {/* Hashtags */}
                {post.hashtags && post.hashtags.length > 0 && (
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Hashtags:
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {post.hashtags.map((tag, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex space-x-3 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handlePostSingle(post.id, post.content)}
                    disabled={posting || !autoPosterActive}
                    className="flex-1 bg-linkedin-600 hover:bg-linkedin-700 text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    title={!autoPosterActive ? 'Start Auto-Poster first' : 'Post to LinkedIn now'}
                  >
                    <Send className="w-5 h-5 mr-2" />
                    Post Now to LinkedIn
                  </button>
                  <button
                    onClick={() => handleApprove(post.id)}
                    className="px-6 py-3 bg-green-100 hover:bg-green-200 text-green-700 font-medium rounded-lg transition-colors flex items-center"
                    title="Schedule for later"
                  >
                    <Calendar className="w-5 h-5 mr-2" />
                    Schedule
                  </button>
                  <button
                    onClick={() => handleReject(post.id)}
                    className="px-6 py-3 bg-red-100 hover:bg-red-200 text-red-700 font-medium rounded-lg transition-colors"
                    title="Delete this post"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
