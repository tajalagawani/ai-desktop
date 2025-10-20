import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

export interface NodeAuthInfo {
  id: string;
  displayName: string;
  description: string;
  userEnabled: boolean;
  operations: number;
  tags: string[];
  authInfo: {
    requiresAuth: boolean;
    authType?: string;
    authFields: Array<{
      field: string;
      type: string;
      description: string;
      required: boolean;
      pattern?: string;
      example?: string;
      sensitive: boolean;
    }>;
  };
}

export function useNodeAuth() {
  const [nodes, setNodes] = useState<NodeAuthInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNodes = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/nodes/auth-required');
      if (!response.ok) throw new Error('Failed to fetch nodes');

      const data = await response.json();
      setNodes(data.nodes || []);
    } catch (err: any) {
      setError(err.message);
      toast.error('Failed to load nodes');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNodes();
  }, [fetchNodes]);

  return {
    nodes,
    loading,
    error,
    refresh: fetchNodes
  };
}
