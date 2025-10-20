'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Plus, RefreshCw, Shield } from 'lucide-react';
import { NodeAuthForm } from './NodeAuthForm';
import { NodeSelector } from './NodeSelector';
import { useNodeAuth, type NodeAuthInfo } from '@/lib/hooks/useNodeAuth';

export function NodesAuthSection() {
  const { nodes, loading, refresh } = useNodeAuth();
  const [selectedNode, setSelectedNode] = useState<NodeAuthInfo | null>(null);
  const [showingSelector, setShowingSelector] = useState(false);

  // Show NodeSelector when + button is clicked
  if (showingSelector) {
    return (
      <NodeSelector
        nodes={nodes}
        onSelect={(node) => {
          setSelectedNode(node);
          setShowingSelector(false);
        }}
        onClose={() => setShowingSelector(false)}
      />
    );
  }

  // Show NodeAuthForm when a node is selected
  if (selectedNode) {
    return (
      <NodeAuthForm
        node={selectedNode}
        onBack={() => setSelectedNode(null)}
        onSuccess={() => {
          setSelectedNode(null);
          refresh();
        }}
      />
    );
  }

  // Default view: Show main screen with + button
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Node Authentication</h2>
        <div className="flex gap-2">
          <Button onClick={refresh} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => setShowingSelector(true)} size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Authentication
          </Button>
        </div>
      </div>

      {loading ? (
        <Skeleton className="h-48" />
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <Shield className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-xl font-semibold mb-2">Authentication Management</h3>
            <p className="text-muted-foreground mb-6">
              Manage API keys and credentials for {nodes.length} nodes requiring authentication.
            </p>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                <strong>{nodes.filter(n => n.userEnabled).length}</strong> nodes are currently enabled
              </p>
              <p>
                <strong>{nodes.filter(n => !n.userEnabled).length}</strong> nodes need configuration
              </p>
            </div>
            <Button
              onClick={() => setShowingSelector(true)}
              className="mt-6"
              size="lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              Configure Node Authentication
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
