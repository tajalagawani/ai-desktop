'use client';

import { useState } from 'react';
import { useFlowSettingsStore } from '@/lib/flow-builder/stores/settings-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Save, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react';

export function FlowBuilderSettings() {
  const { settings, updateSetting, updateSettings, resetSettings } = useFlowSettingsStore();
  const [localSettings, setLocalSettings] = useState(settings);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    updateSettings(localSettings);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    if (confirm('Reset all settings to defaults? This cannot be undone.')) {
      resetSettings();
      setLocalSettings(useFlowSettingsStore.getState().settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  const updateLocal = <K extends keyof typeof localSettings>(
    key: K,
    value: typeof localSettings[K]
  ) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="h-full overflow-auto p-6 bg-background">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">Flow Builder Settings</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Configure ACT agent paths, API keys, and UI preferences
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button size="sm" onClick={handleSave} disabled={saved}>
              {saved ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Saved
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Info Alert */}
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Settings are saved locally in your browser. For production use, configure these values in
            your <code className="font-mono text-xs bg-muted px-1 py-0.5 rounded">.env</code> file.
          </AlertDescription>
        </Alert>

        {/* Settings Tabs */}
        <Tabs defaultValue="act" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="act">ACT Config</TabsTrigger>
            <TabsTrigger value="api">API Keys</TabsTrigger>
            <TabsTrigger value="agent">Agent</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="ui">UI Options</TabsTrigger>
          </TabsList>

          {/* ACT Configuration Tab */}
          <TabsContent value="act" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-medium mb-4">ACT Installation Paths</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="actRoot">ACT Root Directory</Label>
                  <Input
                    id="actRoot"
                    value={localSettings.actRoot}
                    onChange={(e) => updateLocal('actRoot', e.target.value)}
                    placeholder="/var/www/act"
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground">
                    Path to your ACT installation directory
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="agentScriptPath">Agent Script Path (Optional)</Label>
                  <Input
                    id="agentScriptPath"
                    value={localSettings.agentScriptPath}
                    onChange={(e) => updateLocal('agentScriptPath', e.target.value)}
                    placeholder="Auto-detected: ${ACT_ROOT}/agent-sdk/debug-run.sh"
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground">
                    Leave empty to auto-detect. Otherwise, full path to debug-run.sh
                  </p>
                </div>

                <Alert>
                  <AlertDescription className="text-xs">
                    <strong>Default:</strong> If ACT Root is <code className="font-mono bg-muted px-1 py-0.5 rounded">/var/www/act</code>,
                    the script will be at <code className="font-mono bg-muted px-1 py-0.5 rounded">/var/www/act/agent-sdk/debug-run.sh</code>
                  </AlertDescription>
                </Alert>
              </div>
            </Card>
          </TabsContent>

          {/* API Keys Tab */}
          <TabsContent value="api" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-medium mb-4">API Configuration</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="anthropicApiKey">Anthropic API Key</Label>
                  <Input
                    id="anthropicApiKey"
                    type="password"
                    value={localSettings.anthropicApiKey}
                    onChange={(e) => updateLocal('anthropicApiKey', e.target.value)}
                    placeholder="sk-ant-..."
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground">
                    Your Anthropic API key for Claude access
                  </p>
                </div>

                <Alert className="bg-yellow-500/10 border-yellow-500/20">
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                  <AlertDescription className="text-xs text-yellow-600">
                    <strong>Security Note:</strong> Browser storage is not secure for API keys in production.
                    For production deployments, set <code className="font-mono bg-yellow-500/20 px-1 py-0.5 rounded">ANTHROPIC_API_KEY</code> in
                    your ACT installation's <code className="font-mono bg-yellow-500/20 px-1 py-0.5 rounded">.env</code> file instead.
                  </AlertDescription>
                </Alert>
              </div>
            </Card>
          </TabsContent>

          {/* Agent Configuration Tab */}
          <TabsContent value="agent" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-medium mb-4">Agent Behavior</h3>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="defaultModel">Default Model</Label>
                  <select
                    id="defaultModel"
                    value={localSettings.defaultModel}
                    onChange={(e) => updateLocal('defaultModel', e.target.value)}
                    className="w-full px-3 py-2 bg-background border rounded-md text-sm"
                  >
                    <option value="claude-sonnet-4-20250514">Claude Sonnet 4 (Recommended)</option>
                    <option value="claude-opus-4-20250514">Claude Opus 4 (Most Capable)</option>
                    <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet (Legacy)</option>
                  </select>
                  <p className="text-xs text-muted-foreground">
                    Which Claude model to use for flow generation
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="defaultUserId">Default User ID</Label>
                  <Input
                    id="defaultUserId"
                    value={localSettings.defaultUserId}
                    onChange={(e) => updateLocal('defaultUserId', e.target.value)}
                    placeholder="default-user"
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground">
                    User identifier for session tracking
                  </p>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="debugMode">Debug Mode</Label>
                    <p className="text-xs text-muted-foreground">
                      Show detailed debug logs in console
                    </p>
                  </div>
                  <Switch
                    id="debugMode"
                    checked={localSettings.debugMode}
                    onCheckedChange={(checked) => updateLocal('debugMode', checked)}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="verboseMode">Verbose Mode</Label>
                    <p className="text-xs text-muted-foreground">
                      Include all agent output in stream
                    </p>
                  </div>
                  <Switch
                    id="verboseMode"
                    checked={localSettings.verboseMode}
                    onCheckedChange={(checked) => updateLocal('verboseMode', checked)}
                  />
                </div>
              </div>
            </Card>
          </TabsContent>

          {/* Security Configuration Tab */}
          <TabsContent value="security" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-medium mb-4">Security Settings</h3>
              <div className="space-y-4">
                <Alert className="bg-red-500/10 border-red-500/20">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-xs text-red-600">
                    <strong>WARNING:</strong> These settings affect the security of your agent execution.
                    Only enable these if you understand the risks and are running on a trusted server.
                  </AlertDescription>
                </Alert>

                <div className="border-2 border-red-500/20 rounded-lg p-4 bg-red-500/5">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <Label htmlFor="allowSandboxBypass" className="font-semibold text-red-600">
                          Allow Sandbox Bypass (Root Only)
                        </Label>
                        <span className="text-xs bg-red-600 text-white px-2 py-0.5 rounded-full">
                          DANGEROUS
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        When running as root user (VPS deployments), this allows the agent to bypass
                        sandbox restrictions. This is <strong>required for VPS deployment</strong> but
                        should <strong>NEVER</strong> be enabled on your local development machine.
                      </p>
                      <div className="text-xs text-red-600 space-y-1 mt-2">
                        <p><strong>Enable this ONLY if:</strong></p>
                        <ul className="list-disc list-inside ml-2 space-y-1">
                          <li>You are running on a dedicated VPS server</li>
                          <li>The server is running as root user</li>
                          <li>You trust the AI agent with full system access</li>
                        </ul>
                        <p className="mt-2"><strong>DO NOT enable if:</strong></p>
                        <ul className="list-disc list-inside ml-2 space-y-1">
                          <li>Running on your local development machine</li>
                          <li>Running in a shared hosting environment</li>
                          <li>You are unsure about the security implications</li>
                        </ul>
                      </div>
                    </div>
                    <Switch
                      id="allowSandboxBypass"
                      checked={localSettings.allowSandboxBypass}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          // Show confirmation dialog
                          const confirmed = confirm(
                            'WARNING: You are about to enable sandbox bypass!\n\n' +
                            'This allows the AI agent to run with unrestricted access to your system.\n\n' +
                            'ONLY enable this on a trusted VPS server running as root.\n\n' +
                            'Do you understand the risks and want to proceed?'
                          );
                          if (confirmed) {
                            updateLocal('allowSandboxBypass', true);
                          }
                        } else {
                          updateLocal('allowSandboxBypass', false);
                        }
                      }}
                      className="mt-1"
                    />
                  </div>
                </div>

                <Alert>
                  <AlertDescription className="text-xs">
                    <strong>Current Environment:</strong> {' '}
                    <code className="font-mono bg-muted px-1 py-0.5 rounded">
                      {typeof window !== 'undefined' && window.location.hostname === 'localhost'
                        ? 'Local Development'
                        : 'Remote Server'}
                    </code>
                    <br />
                    <strong>Recommendation:</strong> {' '}
                    {typeof window !== 'undefined' && window.location.hostname === 'localhost'
                      ? 'Keep sandbox bypass DISABLED for local development.'
                      : 'You may enable sandbox bypass if running as root on VPS.'}
                  </AlertDescription>
                </Alert>
              </div>
            </Card>
          </TabsContent>

          {/* UI Options Tab */}
          <TabsContent value="ui" className="space-y-4">
            <Card className="p-6">
              <h3 className="text-lg font-medium mb-4">Interface Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="autoScroll">Auto-scroll to Bottom</Label>
                    <p className="text-xs text-muted-foreground">
                      Automatically scroll to latest message
                    </p>
                  </div>
                  <Switch
                    id="autoScroll"
                    checked={localSettings.autoScroll}
                    onCheckedChange={(checked) => updateLocal('autoScroll', checked)}
                  />
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-0.5">
                    <Label htmlFor="showTimestamps">Show Timestamps</Label>
                    <p className="text-xs text-muted-foreground">
                      Display message timestamps
                    </p>
                  </div>
                  <Switch
                    id="showTimestamps"
                    checked={localSettings.showTimestamps}
                    onCheckedChange={(checked) => updateLocal('showTimestamps', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="messageLimit">Message History Limit</Label>
                  <Input
                    id="messageLimit"
                    type="number"
                    min="10"
                    max="1000"
                    value={localSettings.messageLimit}
                    onChange={(e) => updateLocal('messageLimit', parseInt(e.target.value) || 100)}
                    className="font-mono text-sm"
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum number of messages to keep in memory (10-1000)
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Current Configuration Summary */}
        <Card className="p-6 bg-muted/30">
          <h3 className="text-sm font-medium mb-3">Current Configuration</h3>
          <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-xs">
            <div>
              <span className="text-muted-foreground">ACT Root:</span>{' '}
              <code className="font-mono bg-background px-1 py-0.5 rounded">{localSettings.actRoot}</code>
            </div>
            <div>
              <span className="text-muted-foreground">Model:</span>{' '}
              <code className="font-mono bg-background px-1 py-0.5 rounded">{localSettings.defaultModel}</code>
            </div>
            <div>
              <span className="text-muted-foreground">User ID:</span>{' '}
              <code className="font-mono bg-background px-1 py-0.5 rounded">{localSettings.defaultUserId}</code>
            </div>
            <div>
              <span className="text-muted-foreground">Debug:</span>{' '}
              <code className="font-mono bg-background px-1 py-0.5 rounded">
                {localSettings.debugMode ? 'ON' : 'OFF'}
              </code>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
