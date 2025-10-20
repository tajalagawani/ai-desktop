'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, XCircle, Zap, Key, Edit2, Trash2, Plus } from 'lucide-react';
import { toast } from 'sonner';
import type { NodeAuthInfo } from '@/lib/hooks/useNodeAuth';

interface NodeAuthCardProps {
  node: NodeAuthInfo;
  onRefresh: () => void;
  onEdit: () => void;
}

export function NodeAuthCard({ node, onRefresh, onEdit }: NodeAuthCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Remove authentication for ${node.displayName}?`)) return;

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/nodes/${node.id}/auth`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Authentication removed');
        onRefresh();
      } else {
        toast.error('Failed to remove authentication');
      }
    } catch (error) {
      toast.error('Failed to remove authentication');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Card className={node.userEnabled ? 'border-green-500' : ''}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                {node.userEnabled ? (
                  <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
                ) : (
                  <XCircle className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                )}
                <h3 className="text-lg font-semibold truncate">{node.displayName}</h3>
                <Badge variant={node.userEnabled ? "default" : "secondary"} className="flex-shrink-0">
                  {node.userEnabled ? 'Enabled' : 'Not Configured'}
                </Badge>
              </div>

              <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                {node.description}
              </p>

              <div className="flex items-center gap-4 text-sm flex-wrap">
                <span className="flex items-center gap-1">
                  <Zap className="w-4 h-4" />
                  {node.operations} operations
                </span>
                <span className="flex items-center gap-1">
                  <Key className="w-4 h-4" />
                  {node.authInfo.authFields.length} auth field{node.authInfo.authFields.length !== 1 ? 's' : ''}
                </span>
                {node.authInfo.authType && (
                  <Badge variant="outline">{node.authInfo.authType}</Badge>
                )}
              </div>

              <div className="flex gap-2 mt-3 flex-wrap">
                {node.tags.slice(0, 5).map(tag => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="flex gap-2 flex-shrink-0">
              {node.userEnabled ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onEdit}
                  >
                    <Edit2 className="w-4 h-4 md:mr-1" />
                    <span className="hidden md:inline">Edit</span>
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDelete();
                    }}
                    disabled={isDeleting}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <Button
                  variant="default"
                  size="sm"
                  onClick={onEdit}
                  type="button"
                >
                  <Plus className="w-4 h-4 md:mr-1" />
                  <span className="hidden md:inline">Add Auth</span>
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
