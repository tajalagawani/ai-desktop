'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Shield, Key, Circle } from 'lucide-react';
import { useServiceAuth } from '@/lib/hooks/useServiceAuth';

export function ServicesAuthSection() {
  const { services, loading, refresh } = useServiceAuth();

  // Only show services that require auth AND are running
  const authServices = services.filter(s => s.requiresAuth && s.status === 'running');

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Service Authentication</h2>
        <Button onClick={refresh} variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {loading ? (
        <Skeleton className="h-48" />
      ) : authServices.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {authServices.map(service => (
            <Card key={service.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Circle
                        className={`w-3 h-3 ${
                          service.status === 'running'
                            ? 'fill-green-500 text-green-500'
                            : service.status === 'stopped'
                            ? 'fill-yellow-500 text-yellow-500'
                            : 'fill-gray-400 text-gray-400'
                        }`}
                      />
                      <h3 className="font-semibold">{service.name}</h3>
                      <Badge variant={service.status === 'running' ? 'default' : 'secondary'}>
                        {service.status}
                      </Badge>
                      {service.hasStoredAuth ? (
                        <Badge variant="default" className="bg-green-600">
                          <Key className="w-3 h-3 mr-1" />
                          Configured
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-orange-600 border-orange-600">
                          <Shield className="w-3 h-3 mr-1" />
                          Needs Auth
                        </Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground space-y-1">
                      <p>
                        Type: <code className="text-xs bg-muted px-1 rounded">{service.category}</code>
                      </p>
                      {service.connection && (
                        <>
                          <p>
                            Host: <code className="text-xs bg-muted px-1 rounded">{service.connection.host}:{service.connection.port}</code>
                          </p>
                          {service.connection.username && (
                            <p>
                              Default Username: <code className="text-xs bg-muted px-1 rounded">{service.connection.username}</code>
                            </p>
                          )}
                        </>
                      )}
                      {service.docker?.container && (
                        <p>
                          Container: <code className="text-xs bg-muted px-1 rounded">{service.docker.container}</code>
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline">
                      {service.hasStoredAuth ? 'Update' : 'Configure'}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <Shield className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <h3 className="text-xl font-semibold mb-2">No Services Requiring Authentication</h3>
            <p className="text-muted-foreground">
              Infrastructure services with authentication will appear here.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
