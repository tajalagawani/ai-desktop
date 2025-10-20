'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw } from 'lucide-react';
import { useUnifiedCatalog } from '@/lib/hooks/useUnifiedCatalog';

export function UnifiedCatalogView() {
  const { catalog, loading, refresh } = useUnifiedCatalog();

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-semibold">Unified Catalog</h2>
          <p className="text-sm text-muted-foreground">
            What Flow Architect can access
          </p>
        </div>
        <Button onClick={refresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {loading ? (
        <Skeleton className="h-64" />
      ) : (
        <Card>
          <CardContent className="p-6">
            <div className="grid grid-cols-3 gap-6 mb-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-500">
                  {catalog.summary.totalServices}
                </div>
                <div className="text-sm text-muted-foreground">Services</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-500">
                  {catalog.summary.totalNodes}
                </div>
                <div className="text-sm text-muted-foreground">Nodes</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-500">
                  {catalog.summary.totalFlows}
                </div>
                <div className="text-sm text-muted-foreground">Flows</div>
              </div>
            </div>

            <Separator className="my-4" />

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold mb-2">Available Services</h3>
                <div className="flex flex-wrap gap-2">
                  {catalog.services.map(s => (
                    <Badge key={s.id} variant="secondary">
                      {s.name}
                    </Badge>
                  ))}
                  {catalog.services.length === 0 && (
                    <span className="text-sm text-muted-foreground">None</span>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold mb-2">
                  Enabled Nodes ({catalog.summary.enabledNodes})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {catalog.nodes.slice(0, 10).map(n => (
                    <Badge key={n.id} variant="default">
                      {n.displayName}
                    </Badge>
                  ))}
                  {catalog.nodes.length > 10 && (
                    <Badge variant="outline">
                      +{catalog.nodes.length - 10} more
                    </Badge>
                  )}
                  {catalog.nodes.length === 0 && (
                    <span className="text-sm text-muted-foreground">
                      No nodes enabled yet
                    </span>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold mb-2">Deployed Flows</h3>
                <div className="flex flex-wrap gap-2">
                  {catalog.flows.map(f => (
                    <Badge key={f.id} variant="outline">
                      {f.name}
                    </Badge>
                  ))}
                  {catalog.flows.length === 0 && (
                    <span className="text-sm text-muted-foreground">None</span>
                  )}
                </div>
              </div>
            </div>

            {catalog.generated && (
              <div className="mt-4 pt-4 border-t text-xs text-muted-foreground">
                Last updated: {new Date(catalog.generated).toLocaleString()}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
