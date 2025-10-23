'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ShieldAlert, ExternalLink, CheckCircle2 } from 'lucide-react';
import {
  Item,
  ItemContent,
  ItemTitle,
  ItemDescription,
  ItemActions,
  ItemMedia,
} from '@/components/ui/item';

interface NodeAuthRequestProps {
  nodeType: string;
  nodeName: string;
  requiredAuth?: string[];
  reason?: string;
  onAuthClick?: () => void;
}

export function NodeAuthRequest({
  nodeType,
  nodeName,
  requiredAuth = [],
  reason = "This operation requires authentication",
  onAuthClick
}: NodeAuthRequestProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleAuthClick = () => {
    // Open Security Center with this node selected
    if (onAuthClick) {
      onAuthClick();
    } else {
      // Default: dispatch event to open Security Center
      window.dispatchEvent(new CustomEvent('open-security-center', {
        detail: { nodeType, nodeName }
      }));
    }
  };

  // Check if node is authenticated (poll from signature)
  const checkAuth = async () => {
    try {
      const response = await fetch('/api/signature');
      const data = await response.json();
      if (data.authenticated_nodes?.includes(nodeType)) {
        setIsAuthenticated(true);
      }
    } catch (error) {
      console.error('Failed to check auth status:', error);
    }
  };

  return (
    <div className="my-3">
      <Item variant="outline" size="default">
        <ItemMedia>
          <div className="w-10 h-10 bg-orange-500/10 rounded-lg flex items-center justify-center">
            {isAuthenticated ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-orange-600" />
            )}
          </div>
        </ItemMedia>
        <ItemContent>
          <div className="flex items-center gap-2 mb-1">
            <ItemTitle className="text-base">{nodeName} Authentication Required</ItemTitle>
            <Badge variant={isAuthenticated ? "default" : "secondary"} className="text-xs">
              {nodeType}
            </Badge>
          </div>
          <ItemDescription className="text-sm">
            {isAuthenticated ? (
              <span className="text-green-600 font-medium">✓ Authenticated! You can now continue.</span>
            ) : (
              <>
                {reason}
                {requiredAuth.length > 0 && (
                  <span className="block mt-1">
                    Required: {requiredAuth.map(field => (
                      <code key={field} className="text-xs bg-muted px-1 py-0.5 rounded mx-0.5">
                        {field}
                      </code>
                    ))}
                  </span>
                )}
              </>
            )}
          </ItemDescription>
        </ItemContent>
        <ItemActions>
          {isAuthenticated ? (
            <Button
              size="sm"
              variant="outline"
              onClick={checkAuth}
              className="bg-green-500/10 border-green-600 hover:bg-green-500/20"
            >
              <CheckCircle2 className="w-4 h-4 mr-1" />
              Authenticated
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={handleAuthClick}
              className="bg-orange-600 hover:bg-orange-700 text-white"
            >
              <ShieldAlert className="w-4 h-4 mr-1.5" />
              Authenticate
              <ExternalLink className="w-3 h-3 ml-1.5" />
            </Button>
          )}
        </ItemActions>
      </Item>
    </div>
  );
}
