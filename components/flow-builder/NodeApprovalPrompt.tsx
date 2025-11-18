'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui/badge';

interface NodeApprovalPromptProps {
  nodeType: string;
  nodeName: string;
  reason: string;
  requiredFields?: string[];
  onApprove: () => void;
  onReject: () => void;
}

export function NodeApprovalPrompt({
  nodeType,
  nodeName,
  reason,
  requiredFields = [],
  onApprove,
  onReject
}: NodeApprovalPromptProps) {
  const [responded, setResponded] = useState(false);
  const [response, setResponse] = useState<'approved' | 'rejected' | null>(null);

  const handleApprove = () => {
    setResponded(true);
    setResponse('approved');
    onApprove();
  };

  const handleReject = () => {
    setResponded(true);
    setResponse('rejected');
    onReject();
  };

  return (
    <div className="flex flex-col gap-2">
      {/* Header with Badge - EXACT same as TodoList */}
      <div className="flex items-center gap-2 flex-wrap">
        <Badge variant="tool">Permission Required</Badge>
        <span className="text-zinc-400">|</span>
        <span className="text-xs text-zinc-500 dark:text-zinc-400">
          Add {nodeName} Node
        </span>
        {responded && (
          <>
            <span className="text-zinc-400">•</span>
            <Badge variant={response === 'approved' ? 'default' : 'destructive'}>
              {response === 'approved' ? 'Approved' : 'Rejected'}
            </Badge>
          </>
        )}
      </div>

      {/* Tree items - EXACT same structure as TodoList */}
      <div className="space-y-1">
        {/* Main approval item - clickable like TodoList */}
        <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
          <button
            onClick={() => {}}
            className="flex items-center gap-2 text-xs text-zinc-700 dark:text-zinc-300 hover:text-zinc-900 dark:hover:text-zinc-100 transition-colors w-full text-left"
          >
            <span className="text-zinc-400">⊢</span>
            <Badge variant="mcp">
              <span className="flex items-center gap-1.5">
                <span className="text-yellow-600 dark:text-yellow-400">⚠</span>
                {nodeName}
              </span>
            </Badge>
          </button>
        </div>

        {/* Reason - same text styling as TodoList expanded content */}
        <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
          <div className="mt-2 ml-4 text-xs text-zinc-600 dark:text-zinc-400">
            <div className="flex items-center gap-2">
              <span className="font-medium">Reason:</span>
              <span>{reason}</span>
            </div>
          </div>
        </div>

        {/* Required fields (if any) - same styling as TodoList expanded content */}
        {requiredFields.length > 0 && (
          <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
            <div className="mt-2 ml-4 text-xs text-zinc-600 dark:text-zinc-400">
              <div className="flex items-center gap-2">
                <span className="font-medium">Required fields:</span>
                <div className="flex flex-wrap gap-1">
                  {requiredFields.map((field, i) => (
                    <span key={i} className="text-[10px] bg-zinc-100 dark:bg-zinc-900 px-2 py-1 rounded inline-block">
                      {field}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action buttons - same spacing and styling */}
        {!responded && (
          <div className="border-l-2 border-zinc-200 dark:border-zinc-700 pl-2">
            <div className="mt-2 ml-4 flex gap-2">
              <button
                onClick={handleApprove}
                className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs font-medium rounded transition-colors"
              >
                Approve
              </button>
              <button
                onClick={handleReject}
                className="px-3 py-1.5 bg-zinc-200 dark:bg-zinc-700 hover:bg-zinc-300 dark:hover:bg-zinc-600 text-zinc-900 dark:text-zinc-100 text-xs font-medium rounded transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
