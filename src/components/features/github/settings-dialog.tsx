"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { Settings, User, Key, AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface GitSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function GitSettingsDialog({ open, onOpenChange }: GitSettingsDialogProps) {
  const [gitUserName, setGitUserName] = useState("")
  const [gitUserEmail, setGitUserEmail] = useState("")
  const [githubToken, setGithubToken] = useState("")
  const [sshPrivateKey, setSshPrivateKey] = useState("")
  const [sshPublicKey, setSshPublicKey] = useState("")
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null)

  // Load settings from localStorage on mount
  useEffect(() => {
    if (open) {
      const settings = localStorage.getItem("git-settings")
      if (settings) {
        const parsed = JSON.parse(settings)
        setGitUserName(parsed.userName || "")
        setGitUserEmail(parsed.userEmail || "")
        setGithubToken(parsed.githubToken || "")
        setSshPrivateKey(parsed.sshPrivateKey || "")
        setSshPublicKey(parsed.sshPublicKey || "")
      }
    }
  }, [open])

  const handleTestToken = async () => {
    if (!githubToken) {
      setMessage({ type: "error", text: "Please enter a GitHub token first" })
      return
    }

    setTesting(true)
    setMessage(null)

    try {
      const response = await fetch("https://api.github.com/user", {
        headers: {
          Authorization: `token ${githubToken}`,
          Accept: "application/vnd.github.v3+json",
        },
      })

      if (response.ok) {
        const user = await response.json()
        setMessage({ type: "success", text: `Token is valid! Authenticated as ${user.login}` })
      } else {
        setMessage({ type: "error", text: "Token is invalid or expired" })
      }
    } catch (error: any) {
      setMessage({ type: "error", text: error.message || "Failed to verify token" })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage(null)

    try {
      // Save to localStorage
      const settings = {
        userName: gitUserName,
        userEmail: gitUserEmail,
        githubToken: githubToken,
        sshPrivateKey: sshPrivateKey,
        sshPublicKey: sshPublicKey,
      }
      localStorage.setItem("git-settings", JSON.stringify(settings))

      // Set git config if user name and email are provided
      if (gitUserName && gitUserEmail) {
        const configResponse = await fetch("/api/git-config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            userName: gitUserName,
            userEmail: gitUserEmail,
          }),
        })

        if (!configResponse.ok) {
          throw new Error("Failed to save git config")
        }
      }

      setMessage({ type: "success", text: "Settings saved successfully! You can now use your token for Git operations." })
      setTimeout(() => {
        setMessage(null)
      }, 3000)
    } catch (error: any) {
      setMessage({ type: "error", text: error.message || "Failed to save settings" })
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Git Settings
          </DialogTitle>
          <DialogDescription>
            Configure your Git credentials, SSH keys, and authentication settings.
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="user" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="user">
              <User className="h-4 w-4 mr-2" />
              User
            </TabsTrigger>
            <TabsTrigger value="github">
              <Key className="h-4 w-4 mr-2" />
              GitHub Token
            </TabsTrigger>
            <TabsTrigger value="ssh">
              <Key className="h-4 w-4 mr-2" />
              SSH Keys
            </TabsTrigger>
          </TabsList>

          <TabsContent value="user" className="space-y-4 mt-4">
            <div className="space-y-2">
              <Label htmlFor="git-username">Git User Name</Label>
              <Input
                id="git-username"
                placeholder="Your Name"
                value={gitUserName}
                onChange={(e) => setGitUserName(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                This will be used for commit author information
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="git-email">Git User Email</Label>
              <Input
                id="git-email"
                type="email"
                placeholder="your.email@example.com"
                value={gitUserEmail}
                onChange={(e) => setGitUserEmail(e.target.value)}
              />
              <p className="text-xs text-muted-foreground">
                This will be used for commit author information
              </p>
            </div>
          </TabsContent>

          <TabsContent value="github" className="space-y-4 mt-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Create a personal access token at{" "}
                <a
                  href="https://github.com/settings/tokens"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  github.com/settings/tokens
                </a>
                . Required scopes: repo, workflow
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="github-token">GitHub Personal Access Token</Label>
              <div className="flex gap-2">
                <Input
                  id="github-token"
                  type="password"
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  className={githubToken ? "border-green-500" : ""}
                />
                <Button
                  variant="outline"
                  onClick={handleTestToken}
                  disabled={!githubToken || testing}
                >
                  {testing ? "Testing..." : "Test"}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Used for push/pull operations with HTTPS
                {githubToken && <span className="text-green-600 ml-2">✓ Token entered</span>}
              </p>
            </div>
          </TabsContent>

          <TabsContent value="ssh" className="space-y-4 mt-4">
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Generate SSH keys using: ssh-keygen -t ed25519 -C "your_email@example.com"
                <br />
                Add the public key to GitHub at{" "}
                <a
                  href="https://github.com/settings/keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  github.com/settings/keys
                </a>
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="ssh-private-key">SSH Private Key (Optional)</Label>
              <Textarea
                id="ssh-private-key"
                placeholder="-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----"
                value={sshPrivateKey}
                onChange={(e) => setSshPrivateKey(e.target.value)}
                rows={8}
                className="font-mono text-xs"
              />
              <p className="text-xs text-muted-foreground">
                Your SSH private key for authentication. Stored locally only.
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ssh-public-key">SSH Public Key (Optional)</Label>
              <Textarea
                id="ssh-public-key"
                placeholder="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA... your_email@example.com"
                value={sshPublicKey}
                onChange={(e) => setSshPublicKey(e.target.value)}
                rows={3}
                className="font-mono text-xs"
              />
              <p className="text-xs text-muted-foreground">
                Your SSH public key (for reference)
              </p>
            </div>
          </TabsContent>
        </Tabs>

        {message && (
          <Alert variant={message.type === "error" ? "destructive" : "default"}>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "Saving..." : "Save Settings"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
