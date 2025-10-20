'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2, TestTube, Save, AlertCircle, ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import type { NodeAuthInfo } from '@/lib/hooks/useNodeAuth';

interface NodeAuthFormProps {
  node: NodeAuthInfo;
  onBack: () => void;
  onSuccess: () => void;
}

export function NodeAuthForm({ node, onBack, onSuccess }: NodeAuthFormProps) {
  const [authData, setAuthData] = useState<Record<string, string>>({});
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
    details?: any;
  } | null>(null);

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      const response = await fetch(`/api/nodes/${node.id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authData })
      });

      const result = await response.json();
      setTestResult(result);

      if (result.success) {
        toast.success('Connection test passed!');
      } else {
        toast.error('Connection test failed');
      }
    } catch (error) {
      toast.error('Test failed');
      setTestResult({
        success: false,
        message: 'Network error during test'
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      const response = await fetch(`/api/nodes/${node.id}/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ authData })
      });

      if (response.ok) {
        toast.success('Authentication saved successfully!');
        onSuccess();
      } else {
        const error = await response.json();
        toast.error(error.error || 'Failed to save');
      }
    } catch (error) {
      toast.error('Failed to save authentication');
    } finally {
      setSaving(false);
    }
  };

  const isFormValid = node.authInfo.authFields
    .filter(f => f.required)
    .every(f => authData[f.field]?.trim());

  const formatFieldLabel = (field: string) => {
    return field
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="space-y-6">
      {/* Header with Back Button */}
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={onBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Nodes
        </Button>
        <div>
          <h2 className="text-2xl font-semibold">Configure Authentication</h2>
          <p className="text-muted-foreground">{node.displayName}</p>
        </div>
      </div>

      {/* Form Card */}
      <Card>
        <CardHeader>
          <CardTitle>Enter Your Credentials</CardTitle>
          <CardDescription>
            Enter your credentials to enable this node in Flow Architect
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Auth Fields */}
          <div className="space-y-4">
            {node.authInfo.authFields.map(field => (
              <div key={field.field} className="space-y-2">
                <Label htmlFor={field.field}>
                  {formatFieldLabel(field.field)}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </Label>
                <Input
                  id={field.field}
                  type={field.sensitive ? 'password' : 'text'}
                  placeholder={field.example || `Enter ${field.field}`}
                  value={authData[field.field] || ''}
                  onChange={(e) => setAuthData({
                    ...authData,
                    [field.field]: e.target.value
                  })}
                  required={field.required}
                />
                {field.description && (
                  <p className="text-xs text-muted-foreground">
                    {field.description}
                  </p>
                )}
                {field.pattern && (
                  <p className="text-xs text-muted-foreground">
                    Format: <code className="bg-muted px-1 rounded">{field.pattern}</code>
                  </p>
                )}
              </div>
            ))}
          </div>

          {/* Test Result */}
          {testResult && (
            <Alert variant={testResult.success ? 'default' : 'destructive'}>
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>
                {testResult.success ? 'Test Passed' : 'Test Failed'}
              </AlertTitle>
              <AlertDescription>
                {testResult.message}
                {testResult.details && (
                  <pre className="mt-2 text-xs overflow-auto bg-muted p-2 rounded">
                    {JSON.stringify(testResult.details, null, 2)}
                  </pre>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Button
              variant="outline"
              onClick={onBack}
            >
              Cancel
            </Button>
            <Button
              variant="secondary"
              onClick={handleTest}
              disabled={!isFormValid || testing}
            >
              {testing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Testing...
                </>
              ) : (
                <>
                  <TestTube className="w-4 h-4 mr-2" />
                  Test Connection
                </>
              )}
            </Button>
            <Button
              onClick={handleSave}
              disabled={!isFormValid || saving}
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
