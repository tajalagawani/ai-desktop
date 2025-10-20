import { useState, useEffect, useCallback } from 'react';

export interface DockerService {
  id: string;
  name: string;
  status: 'running' | 'stopped';
  image: string;
  ports: string[];
  created: string;
}

/**
 * Direct Docker access - super fast simple endpoint
 * Just runs `docker ps` - no heavy processing
 */
export function useDockerDirect() {
  const [services, setServices] = useState<DockerService[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchServices = useCallback(async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/docker/ps');
      const data = await response.json();
      setServices(data.services || []);
    } catch (error) {
      console.error('Failed to fetch Docker containers:', error);
      setServices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
    // No auto-refresh - user can click refresh button if needed
  }, [fetchServices]);

  return {
    services,
    loading,
    refresh: fetchServices
  };
}
