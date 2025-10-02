"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { BackgroundBeams } from "@/components/ui/background-beams"
import { LayoutTextFlip } from "@/components/ui/layout-text-flip"
import { TextHoverEffect } from "@/components/ui/text-hover-effect"
import { motion } from "framer-motion"
import { Shield, Smartphone } from "lucide-react"

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
    <div className="h-screen w-full bg-background relative flex flex-col items-center justify-center antialiased overflow-hidden">
      <BackgroundBeams paused={!showLogin} />

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
        <>
          {/* Show login form after transition */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="max-w-md mx-auto p-4 relative z-10"
          >
            <Card className="bg-card/80 backdrop-blur-sm border-border p-8">
              <div className="text-center mb-6">
                <div className="flex justify-center mb-4">
                  <div className="p-3 rounded-full bg-teal-500/10 border border-teal-500/20">
                    <Shield className="h-8 w-8 text-teal-500" />
                  </div>
                </div>
                <h1 className="text-2xl font-bold text-foreground mb-2">Two-Factor Authentication</h1>
                <p className="text-muted-foreground text-sm">
                  Enter the 6-digit code from your authenticator app to access AI Desktop
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-1">
                  <label htmlFor="auth-code" className="text-sm font-medium text-foreground block mb-3">
                    Authentication Code
                  </label>
                  <div className="relative">
                    <Input
                      id="auth-code"
                      type="text"
                      value={code}
                      onChange={handleCodeChange}
                      placeholder="000000"
                      className="text-center text-2xl font-mono tracking-widest"
                      maxLength={6}
                      autoComplete="one-time-code"
                    />
                    <Smartphone className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  </div>
                  {error && <p className="text-sm text-red-500 mt-1">{error}</p>}
                </div>

                <Button type="submit" className="w-full" disabled={code.length !== 6 || isLoading}>
                  {isLoading ? "Verifying..." : "Verify & Continue"}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <p className="text-xs text-muted-foreground">
                  Don't have access to your authenticator app?{" "}
                  <button className="text-teal-500 hover:underline">Use backup codes</button>
                </p>
              </div>
            </Card>
          </motion.div>

          {/* Flipped text in bottom left corner */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.3 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            className="absolute bottom-6 -left-8 z-10"
          >
            <div className="scale-75">
              <LayoutTextFlip
                text="Securing access to "
                words={["AI Desktop", "Your Workspace", "The Future", "Innovation"]}
              />
            </div>
          </motion.div>
        </>
      )}
    </div>
  )
}