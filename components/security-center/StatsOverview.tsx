'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Key, Database, Workflow, CheckCircle } from 'lucide-react';

interface StatsOverviewProps {
  enabledNodes: number;
  totalNodes: number;
  runningServices: number;
  totalServices: number;
  deployedFlows: number;
  passedTests?: number;
}

export function StatsOverview({
  enabledNodes,
  totalNodes,
  runningServices,
  totalServices,
  deployedFlows,
  passedTests = 0
}: StatsOverviewProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        icon={<Key className="w-5 h-5" />}
        title="Nodes Enabled"
        value={`${enabledNodes} / ${totalNodes}`}
        description="Authenticated nodes"
        variant={enabledNodes > 0 ? 'success' : 'warning'}
      />
      <StatCard
        icon={<Database className="w-5 h-5" />}
        title="Services Running"
        value={`${runningServices} / ${totalServices}`}
        description="Docker services"
        variant={runningServices > 0 ? 'success' : 'default'}
      />
      <StatCard
        icon={<Workflow className="w-5 h-5" />}
        title="Flows Deployed"
        value={deployedFlows.toString()}
        description="Active workflows"
        variant="default"
      />
      <StatCard
        icon={<CheckCircle className="w-5 h-5" />}
        title="Tests Passed"
        value={passedTests.toString()}
        description="Connection tests"
        variant={passedTests > 0 ? 'success' : 'default'}
      />
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  variant?: 'success' | 'warning' | 'default';
}

function StatCard({ icon, title, value, description, variant = 'default' }: StatCardProps) {
  const variantStyles = {
    success: 'border-green-500/50 bg-green-50/50 dark:bg-green-950/20',
    warning: 'border-yellow-500/50 bg-yellow-50/50 dark:bg-yellow-950/20',
    default: 'border-border'
  };

  const iconStyles = {
    success: 'text-green-500',
    warning: 'text-yellow-500',
    default: 'text-muted-foreground'
  };

  return (
    <Card className={variantStyles[variant]}>
      <CardContent className="p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className={iconStyles[variant]}>{icon}</div>
          <span className="text-sm font-medium text-muted-foreground">{title}</span>
        </div>
        <div className="text-2xl font-bold mb-1">{value}</div>
        <div className="text-xs text-muted-foreground">{description}</div>
      </CardContent>
    </Card>
  );
}
