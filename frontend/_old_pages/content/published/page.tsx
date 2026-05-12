'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, TrendingUp, Heart, MessageCircle, Share2, Eye, ExternalLink } from 'lucide-react'

interface Post {
  id: number
  content: string
  published_at: string
  linkedin_url: string
  engagement: {
    likes: number
    comments: number
    shares: number
    views: number
  }
}

export default function PublishedPostsPage() {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPublishedPosts()
  }, [])

  const fetchPublishedPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/content/published')
      if (response.ok) {
        const data = await response.json()
        setPosts(data.posts || [])
      }
    } catch (error) {
      console.error('Error fetching published posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const totalEngagement = posts.reduce((sum, post) => {
    return sum + post.engagement.likes + post.engagement.comments + post.engagement.shares
  }, 0)

  const totalViews = posts.reduce((sum, post) => sum + post.engagement.views, 0)

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-linkedin-50 via-white to-blue-50 flex items-center justify-center">
        <div className="text-gray-600">Loading analytics...</div>
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
                <TrendingUp className="w-8 h-8 text-purple-600" />
                <h1 className="text-2xl font-bold text-gray-900">Content Analytics</h1>
              </div>
            </div>
            <Link href="/content/queue" className="btn-primary">
              Review Queue
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Posts</p>
                <p className="text-3xl font-bold text-gray-900">{posts.length}</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Views</p>
                <p className="text-3xl font-bold text-blue-600">{totalViews.toLocaleString()}</p>
              </div>
              <Eye className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Engagement</p>
                <p className="text-3xl font-bold text-green-600">{totalEngagement}</p>
              </div>
              <Heart className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Engagement</p>
                <p className="text-3xl font-bold text-orange-600">
                  {posts.length > 0 ? Math.round(totalEngagement / posts.length) : 0}
                </p>
              </div>
              <MessageCircle className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Posts List */}
        <div className="space-y-6">
          {posts.length === 0 ? (
            <div className="card text-center py-12">
              <TrendingUp className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No published posts yet</h3>
              <p className="text-gray-600 mb-6">
                Start creating and publishing content to see analytics here
              </p>
              <Link href="/content/queue" className="btn-primary inline-block">
                Review Queue
              </Link>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <p className="text-gray-700 mb-4 whitespace-pre-wrap line-clamp-4">
                      {post.content}
                    </p>
                    <p className="text-sm text-gray-600">
                      Published {new Date(post.published_at).toLocaleDateString()} at{' '}
                      {new Date(post.published_at).toLocaleTimeString()}
                    </p>
                  </div>
                  {post.linkedin_url && (
                    <a
                      href={post.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-secondary ml-4"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  )}
                </div>

                {/* Engagement Stats */}
                <div className="grid grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <Eye className="w-5 h-5 text-blue-500" />
                    <div>
                      <p className="text-sm text-gray-600">Views</p>
                      <p className="font-bold text-gray-900">{post.engagement.views.toLocaleString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Heart className="w-5 h-5 text-red-500" />
                    <div>
                      <p className="text-sm text-gray-600">Likes</p>
                      <p className="font-bold text-gray-900">{post.engagement.likes}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <MessageCircle className="w-5 h-5 text-green-500" />
                    <div>
                      <p className="text-sm text-gray-600">Comments</p>
                      <p className="font-bold text-gray-900">{post.engagement.comments}</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Share2 className="w-5 h-5 text-purple-500" />
                    <div>
                      <p className="text-sm text-gray-600">Shares</p>
                      <p className="font-bold text-gray-900">{post.engagement.shares}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
