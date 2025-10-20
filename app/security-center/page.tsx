'use client';

import { SecurityCenterLayout } from '@/components/security-center/SecurityCenterLayout';

export default function SecurityCenterPage() {
  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Security Center</h1>
        <p className="text-muted-foreground">
          Manage authentication for services and nodes
        </p>
      </div>

      <SecurityCenterLayout />
    </div>
  );
}
