'use client';

import { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { X, Search } from 'lucide-react';
import { type NodeAuthInfo } from '@/lib/hooks/useNodeAuth';

interface NodeSelectorProps {
  nodes: NodeAuthInfo[];
  onSelect: (node: NodeAuthInfo) => void;
  onClose: () => void;
}

export function NodeSelector({ nodes, onSelect, onClose }: NodeSelectorProps) {
  const [filter, setFilter] = useState<'all' | 'enabled' | 'disabled'>('all');
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState<'name' | 'operations'>('name');

  const filteredNodes = useMemo(() => {
    let result = [...nodes];

    // Filter by status
    if (filter === 'enabled') {
      result = result.filter(n => n.userEnabled);
    } else if (filter === 'disabled') {
      result = result.filter(n => !n.userEnabled);
    }

    // Search
    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter(n =>
        n.displayName.toLowerCase().includes(searchLower) ||
        n.description.toLowerCase().includes(searchLower) ||
        n.tags.some(t => t.toLowerCase().includes(searchLower))
      );
    }

    // Sort
    result.sort((a, b) => {
      if (sort === 'name') {
        return a.displayName.localeCompare(b.displayName);
      } else {
        return b.operations - a.operations;
      }
    });

    return result;
  }, [nodes, filter, search, sort]);

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Select Node to Configure</h2>
        <Button onClick={onClose} variant="outline" size="sm">
          <X className="w-4 h-4 mr-2" />
          Close
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <Select value={filter} onValueChange={(v) => setFilter(v as any)}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Nodes</SelectItem>
            <SelectItem value="enabled">Enabled Only</SelectItem>
            <SelectItem value="disabled">Disabled Only</SelectItem>
          </SelectContent>
        </Select>

        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search nodes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <Select value={sort} onValueChange={(v) => setSort(v as any)}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="name">Sort by Name</SelectItem>
            <SelectItem value="operations">Sort by Operations</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Nodes list */}
      {filteredNodes.length > 0 ? (
        <>
          <div className="grid grid-cols-1 gap-3">
            {filteredNodes.map(node => (
              <Card
                key={node.id}
                className="cursor-pointer hover:bg-accent transition-colors"
                onClick={() => onSelect(node)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold">{node.displayName}</h3>
                        <Badge variant={node.userEnabled ? 'default' : 'secondary'}>
                          {node.userEnabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                        <Badge variant="outline">
                          {node.operations} operations
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">
                        {node.description.substring(0, 150)}
                        {node.description.length > 150 ? '...' : ''}
                      </p>
                      {node.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {node.tags.map(tag => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="mt-4 text-sm text-muted-foreground text-center">
            Showing {filteredNodes.length} of {nodes.length} nodes
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-muted-foreground">
          <p>No nodes found matching your filters</p>
        </div>
      )}
    </div>
  );
}
