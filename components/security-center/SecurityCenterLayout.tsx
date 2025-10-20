'use client';

import { StatsOverview } from './StatsOverview';
import { NodesAuthSection } from './NodesAuthSection';
import { ServicesAuthSection } from './ServicesAuthSection';
import { DockerServicesSection } from './DockerServicesSection';
import { UnifiedCatalogView } from './UnifiedCatalogView';
import { useNodeAuth } from '@/lib/hooks/useNodeAuth';
import { useDockerDirect } from '@/lib/hooks/useDockerDirect';

export function SecurityCenterLayout() {
  const { nodes } = useNodeAuth();
  const { services } = useDockerDirect();

  // Calculate stats
  const enabledNodes = nodes.filter(n => n.userEnabled).length;
  const totalNodes = nodes.length;
  const runningServices = services.filter(s => s.status === 'running').length;
  const totalServices = services.length;
  const deployedFlows = 0; // Not needed for now

  return (
    <div className="space-y-8">
      {/* Stats Overview */}
      <StatsOverview
        enabledNodes={enabledNodes}
        totalNodes={totalNodes}
        runningServices={runningServices}
        totalServices={totalServices}
        deployedFlows={deployedFlows}
      />

      {/* Unified Catalog */}
      <UnifiedCatalogView />

      {/* Docker Infrastructure Services Authentication */}
      <ServicesAuthSection />

      {/* All Running Docker Containers */}
      <DockerServicesSection />

      {/* API Nodes Requiring Authentication */}
      <NodesAuthSection />
    </div>
  );
}
