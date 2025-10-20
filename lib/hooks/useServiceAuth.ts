import { useState, useEffect, useCallback } from 'react';

export interface ServiceAuthInfo {
  id: string;
  name: string;
  type: string; // 'infrastructure' | 'flow'
  category: string;
  description: string;
  status: 'running' | 'stopped' | 'available' | 'not-installed';
  requiresAuth: boolean;
  hasStoredAuth: boolean;
  connection?: {
    host: string;
    port: number;
    string?: string;
    username?: string;
    password?: string;
  };
  docker?: {
    image?: string;
    container?: string;
    ports?: any[];
  };
}

/**
 * Hook to manage service authentication from dynamic catalog
 */
export function useServiceAuth() {
  const [services, setServices] = useState<ServiceAuthInfo[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchServices = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch from services API
      const response = await fetch('/api/services');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch services');
      }

      // Filter only services that have default credentials (require auth)
      const authRequiredServices = (data.services || [])
        .filter((s: any) => s.defaultCredentials && (s.defaultCredentials.username || s.defaultCredentials.password))
        .map((s: any) => ({
          id: s.id,
          name: s.name,
          type: 'infrastructure',
          category: s.category,
          description: s.description,
          status: s.status,
          requiresAuth: true,
          hasStoredAuth: false, // Will be updated below
          connection: {
            host: 'localhost',
            port: s.defaultCredentials.port || s.ports?.[0] || 0,
            username: s.defaultCredentials.username,
            password: s.defaultCredentials.password
          },
          docker: {
            image: s.dockerImage,
            container: s.containerName,
            ports: s.ports
          }
        }));

      // Check which services have stored auth
      const servicesWithAuthStatus = await Promise.all(
        authRequiredServices.map(async (service: ServiceAuthInfo) => {
          try {
            const authResponse = await fetch(`/api/services/${service.id}/auth`);
            return {
              ...service,
              hasStoredAuth: authResponse.ok
            };
          } catch {
            return {
              ...service,
              hasStoredAuth: false
            };
          }
        })
      );

      setServices(servicesWithAuthStatus);
    } catch (error) {
      console.error('Failed to fetch services:', error);
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
