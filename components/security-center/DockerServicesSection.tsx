'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw, Database, Circle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useDockerDirect } from '@/lib/hooks/useDockerDirect';

export function DockerServicesSection() {
  const { services, loading, refresh } = useDockerDirect();

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Services</h2>
        <Button onClick={refresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : services.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {services.map(service => (
            <Card key={service.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Circle className={`w-3 h-3 ${service.status === 'running' ? 'fill-green-500 text-green-500' : 'fill-gray-400 text-gray-400'}`} />
                      <h3 className="font-semibold">{service.name}</h3>
                      <Badge variant={service.status === 'running' ? 'default' : 'secondary'}>
                        {service.status}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <p>Image: <code className="text-xs bg-muted px-1 rounded">{service.image}</code></p>
                      {service.ports.length > 0 && (
                        <p>Ports: {service.ports.join(', ')}</p>
                      )}
                      <p className="text-xs">Created: {service.created}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg mb-2">No services found</p>
            <p className="text-sm">
              Install services using the Service Manager
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
