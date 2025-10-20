'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { PlayCircle, StopCircle, AlertCircle, Eye, Copy, Check } from 'lucide-react';
import { toast } from 'sonner';
import type { ServiceInfo } from '@/lib/hooks/useServices';

interface ServiceCardProps {
  service: ServiceInfo;
  onRefresh: () => void;
}

export function ServiceCard({ service, onRefresh }: ServiceCardProps) {
  const [showConnection, setShowConnection] = useState(false);
  const [copying, setCopying] = useState(false);

  const handleCopy = async () => {
    if (!service.connection?.string) return;

    await navigator.clipboard.writeText(service.connection.string);
    setCopying(true);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopying(false), 2000);
  };

  const statusIcon = {
    running: <PlayCircle className="w-5 h-5 text-green-500" />,
    stopped: <StopCircle className="w-5 h-5 text-muted-foreground" />,
    error: <AlertCircle className="w-5 h-5 text-red-500" />
  }[service.status];

  const statusColor = {
    running: 'bg-green-500',
    stopped: 'bg-gray-500',
    error: 'bg-red-500'
  }[service.status];

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2 flex-1 min-w-0">
            {statusIcon}
            <h3 className="text-lg font-semibold truncate">{service.name}</h3>
          </div>
          {service.category && (
            <Badge variant="outline" className="flex-shrink-0">{service.category}</Badge>
          )}
        </div>

        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${statusColor}`} />
            <span className="capitalize">{service.status}</span>
          </div>

          {service.connection && (
            <>
              <div className="text-sm text-muted-foreground">
                Port: {service.connection.port}
              </div>

              {showConnection && (
                <div className="mt-2 p-2 bg-muted rounded text-xs font-mono break-all">
                  {service.connection.string}
                </div>
              )}
            </>
          )}
        </div>

        {service.status === 'running' && service.connection && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowConnection(!showConnection)}
            >
              <Eye className="w-4 h-4 mr-1" />
              {showConnection ? 'Hide' : 'Show'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              disabled={copying}
            >
              {copying ? (
                <Check className="w-4 h-4 mr-1" />
              ) : (
                <Copy className="w-4 h-4 mr-1" />
              )}
              Copy
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
