"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { BackgroundBeams } from "@/components/ui/background-beams"
import { TextHoverEffect } from "@/components/ui/text-hover-effect"
import { motion } from "framer-motion"
import { User } from "lucide-react"

interface TwoFactorAuthProps {
  onAuthenticated: () => void
}

export function TwoFactorAuth({ onAuthenticated }: TwoFactorAuthProps) {
  const [code, setCode] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [showLogin, setShowLogin] = useState(false)

  // Auto-transition to login after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowLogin(true)
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (code.length !== 6) {
      setError("Please enter a 6-digit code")
      return
    }

    setIsLoading(true)
    setError("")

    // Simulate authentication delay
    setTimeout(() => {
      // For demo purposes, accept any 6-digit code
      // In a real app, this would validate against a backend
      if (code === "123456" || code.length === 6) {
        onAuthenticated()
      } else {
        setError("Invalid authentication code")
      }
      setIsLoading(false)
    }, 1500)
  }

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, "").slice(0, 6)
    setCode(value)
    setError("")
  }

  return (
    <div className="h-screen w-full relative flex flex-col items-center justify-center antialiased overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Subtle background effect */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-800/20 via-transparent to-transparent" />
      <BackgroundBeams paused={!showLogin} className="opacity-30" />

      {!showLogin ? (
        // Show ORCHA text hover effect first
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.5 }}
          transition={{ duration: 0.8 }}
          className="h-[40rem] flex items-center justify-center"
        >
          <TextHoverEffect text="ORCHA" />
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative z-10 flex flex-col items-center"
        >
          {/* User Avatar */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, duration: 0.3 }}
            className="mb-8"
          >
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-slate-700 to-slate-800 border-4 border-slate-600/50 shadow-2xl flex items-center justify-center">
                <User className="w-16 h-16 text-slate-300" strokeWidth={1.5} />
              </div>
              {/* Subtle glow effect */}
              <div className="absolute inset-0 rounded-full bg-slate-500/10 blur-2xl" />
            </div>
          </motion.div>

          {/* User Name */}
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2, duration: 0.3 }}
            className="text-3xl font-light text-white mb-2 tracking-wide"
          >
            ORCHA Desktop
          </motion.h1>

          {/* Authentication Form */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.3 }}
            className="w-80 mt-6"
          >
            <div className="space-y-4">
              {/* Input Field */}
              <div className="relative">
                <Input
                  id="auth-code"
                  type="text"
                  value={code}
                  onChange={handleCodeChange}
                  placeholder="Enter authentication code"
                  className="w-full h-12 px-4 bg-white/10 backdrop-blur-md border-white/20 hover:border-white/30 focus:border-white/50 text-white placeholder:text-slate-400 text-center text-lg tracking-widest font-mono rounded-lg transition-all duration-200 shadow-lg"
                  maxLength={6}
                  autoComplete="one-time-code"
                  autoFocus
                />
              </div>

              {/* Error Message */}
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-sm text-red-400 text-center"
                >
                  {error}
                </motion.p>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={code.length !== 6 || isLoading}
                className="w-full h-12 bg-white/20 hover:bg-white/30 backdrop-blur-md border border-white/30 text-white font-medium rounded-lg transition-all duration-200 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Verifying...
                  </span>
                ) : (
                  "Sign In"
                )}
              </Button>
            </div>
          </motion.form>

          {/* Helper Text */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4, duration: 0.3 }}
            className="mt-6 text-sm text-slate-400 text-center"
          >
            Enter your 6-digit authentication code
          </motion.p>
        </motion.div>
      )}

      {/* Bottom Info - OS Style */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-xs text-slate-500 text-center"
      >
        ORCHA Desktop • Secure Authentication
      </motion.div>
    </div>
  )
}