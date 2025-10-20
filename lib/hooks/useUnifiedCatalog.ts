import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

export interface UnifiedCatalog {
  services: Array<{
    id: string;
    name: string;
    type: string;
    status: string;
    category?: string;
  }>;
  nodes: Array<{
    id: string;
    displayName: string;
    type: string;
    enabled: boolean;
    authenticated: boolean;
    operations: number;
  }>;
  flows: Array<{
    id: string;
    name: string;
    type: string;
    status: string;
  }>;
  summary: {
    totalServices: number;
    totalNodes: number;
    totalFlows: number;
    enabledNodes: number;
  };
  generated?: string;
}

export function useUnifiedCatalog() {
  const [catalog, setCatalog] = useState<UnifiedCatalog>({
    services: [],
    nodes: [],
    flows: [],
    summary: {
      totalServices: 0,
      totalNodes: 0,
      totalFlows: 0,
      enabledNodes: 0
    }
  });
  const [loading, setLoading] = useState(true);

  const fetchCatalog = useCallback(async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/unified');
      if (!response.ok) throw new Error('Failed to fetch catalog');

      const data = await response.json();
      setCatalog(data);
    } catch (err) {
      // Silent fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCatalog();
  }, [fetchCatalog]);

  return {
    catalog,
    loading,
    refresh: fetchCatalog
  };
}
