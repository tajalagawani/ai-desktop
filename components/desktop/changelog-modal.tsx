"use client"

import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, GitCommit, Clock, User, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ChangelogEntry {
  sha: string
  message: string
  author: string
  date: string
  url: string
}

interface ChangelogModalProps {
  isOpen: boolean
  onClose: () => void
}

export function ChangelogModal({ isOpen, onClose }: ChangelogModalProps) {
  const [changelog, setChangelog] = useState<ChangelogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchChangelog()
    }
  }, [isOpen])

  const fetchChangelog = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/changelog')
      const data = await response.json()

      if (data.success) {
        setChangelog(data.changelog)
      } else {
        setError('Failed to load changelog')
      }
    } catch (err) {
      setError('Failed to fetch changelog')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 7) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    } else if (days > 0) {
      return `${days} day${days > 1 ? 's' : ''} ago`
    } else if (hours > 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ago`
    } else {
      return 'Just now'
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9998]"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", duration: 0.3 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-2xl max-h-[80vh] bg-slate-900/95 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-2xl z-[9999] overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-slate-700/50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-slate-700/50 border border-slate-600/50">
                  <GitCommit className="w-5 h-5 text-slate-300" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-white">Recent Updates</h2>
                  <p className="text-sm text-slate-400">Latest changes from GitHub</p>
                </div>
              </div>
              <Button
                onClick={onClose}
                variant="ghost"
                size="icon"
                className="text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* Content */}
            <div className="overflow-y-auto max-h-[calc(80vh-120px)] p-6">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="flex flex-col items-center gap-3">
                    <div className="w-8 h-8 border-2 border-slate-600/30 border-t-slate-300 rounded-full animate-spin" />
                    <p className="text-sm text-slate-400">Loading changelog...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <p className="text-red-400 mb-2">{error}</p>
                    <Button onClick={fetchChangelog} variant="outline" size="sm">
                      Retry
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {changelog.map((entry, index) => (
                    <motion.div
                      key={entry.sha}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="group relative p-4 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:border-slate-600 hover:bg-slate-800/70 transition-all duration-200"
                    >
                      {/* Commit Info */}
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium mb-2 line-clamp-2">
                            {entry.message}
                          </p>
                          <div className="flex items-center gap-4 text-sm text-slate-400">
                            <span className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {entry.author}
                            </span>
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(entry.date)}
                            </span>
                            <span className="font-mono text-xs bg-slate-700/50 px-2 py-0.5 rounded">
                              {entry.sha}
                            </span>
                          </div>
                        </div>
                        <a
                          href={entry.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-slate-700 rounded-lg"
                        >
                          <ExternalLink className="w-4 h-4 text-slate-400" />
                        </a>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-700/50 bg-slate-900/50">
              <div className="flex items-center justify-between">
                <p className="text-xs text-slate-500">
                  Auto-updates every 60 seconds
                </p>
                <Button
                  onClick={fetchChangelog}
                  variant="outline"
                  size="sm"
                  disabled={loading}
                  className="text-slate-300 border-slate-700 hover:bg-slate-800"
                >
                  Refresh
                </Button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
