import { useState, useEffect, useCallback } from 'react';

export interface ServiceInfo {
  id: string;
  name: string;
  status: 'running' | 'stopped' | 'error';
  category: string;
  connection?: {
    host: string;
    port: number;
    string: string;
  };
}

export function useServices() {
  const [services, setServices] = useState<ServiceInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchServices = useCallback(async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/catalog?status=running');
      if (!response.ok) throw new Error('Failed to fetch services');

      const data = await response.json();
      setServices(data.services || []);
    } catch (err) {
      setServices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  return {
    services,
    loading,
    refresh: fetchServices
  };
}
