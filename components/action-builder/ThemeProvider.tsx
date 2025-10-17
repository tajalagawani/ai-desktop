'use client';

import { useEffect } from 'react';
import { useChatStore } from '@/lib/action-builder/stores/chatStore';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const isDarkMode = useChatStore(state => state.isDarkMode);

  useEffect(() => {
    // Initialize dark mode from localStorage on mount
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  useEffect(() => {
    // Update dark mode when state changes
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  return <>{children}</>;
}
