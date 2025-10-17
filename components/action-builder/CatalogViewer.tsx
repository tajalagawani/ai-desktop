'use client';

import { useState, useEffect } from 'react';
import { authenticatedFetch } from '@/lib/action-builder/api';

interface Service {
  id: string;
  name?: string;
  type: string;
  port: number;
}

interface Node {
  type: string;
  name?: string;
}

interface Catalogs {
  services: Service[];
  nodes: Node[];
}

export default function CatalogViewer() {
  const [catalogs, setCatalogs] = useState<Catalogs>({ services: [], nodes: [] });
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCatalogs();
  }, []);

  async function loadCatalogs() {
    setIsLoading(true);
    setError(null);
    try {
      const servicesRes = await authenticatedFetch('/api/flow-architect/catalogs/service-catalog.json');
      const nodesRes = await authenticatedFetch('/api/flow-architect/catalogs/node-catalog.json');

      if (!servicesRes.ok || !nodesRes.ok) {
        // Silently fail if catalogs don't exist yet
        setCatalogs({ services: [], nodes: [] });
        return;
      }

      const servicesData = await servicesRes.json();
      const nodesData = await nodesRes.json();

      setCatalogs({
        services: servicesData.services || [],
        nodes: nodesData.nodes || []
      });
    } catch (err: any) {
      console.error('Error loading catalogs:', err);
      // Don't show error to user, just set empty catalogs
      setCatalogs({ services: [], nodes: [] });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="catalog-viewer border-t border-border">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-muted transition-colors"
      >
        <span className="text-sm font-semibold text-foreground">
          📋 Available Services & Tools
        </span>
        <span className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div className="px-4 pb-4 max-h-96 overflow-y-auto">
          {isLoading ? (
            <div className="text-center py-4 text-muted-foreground">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-muted-foreground mx-auto mb-2"></div>
              <p className="text-sm">Loading catalogs...</p>
            </div>
          ) : error ? (
            <div className="text-center py-4 text-destructive">
              <p className="text-sm">Error: {error}</p>
              <button
                onClick={loadCatalogs}
                className="mt-2 text-xs px-3 py-1 bg-muted rounded hover:bg-muted/80"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Services Section */}
              <div>
                <h3 className="font-bold text-sm mb-2 text-foreground">
                  🗄️ Services ({catalogs.services.length})
                </h3>
                {catalogs.services.length > 0 ? (
                  <div className="grid grid-cols-1 gap-2">
                    {catalogs.services.map(svc => (
                      <div
                        key={svc.id}
                        className="p-2 bg-muted rounded text-xs"
                      >
                        <div className="font-semibold text-foreground">
                          {svc.name || svc.id}
                        </div>
                        <div className="text-muted-foreground">
                          Type: {svc.type} • Port: {svc.port}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No services configured</p>
                )}
              </div>

              {/* Tools/Nodes Section */}
              <div>
                <h3 className="font-bold text-sm mb-2 text-foreground">
                  🔧 Tools ({catalogs.nodes.length})
                </h3>
                {catalogs.nodes.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {catalogs.nodes.map(node => (
                      <span
                        key={node.type}
                        className="px-2 py-1 bg-primary/10 text-primary rounded text-xs font-mono"
                        title={node.name || node.type}
                      >
                        {node.type}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No tools configured</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
