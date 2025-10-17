// Hook to hydrate Zustand store with localStorage values on client-side only
// This prevents hydration mismatches between server and client

import { useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

export function useStoreHydration() {
  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') return;

    const store = useChatStore.getState();

    // Hydrate auth token
    const token = localStorage.getItem('auth-token');
    if (token) {
      store.setToken(token);
    }

    // Hydrate UI settings
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode !== store.isDarkMode) {
      store.toggleDarkMode();
    }

    const devMode = localStorage.getItem('dev_mode') === 'true';
    if (devMode !== store.isDevMode) {
      store.toggleDevMode();
    }

    // Hydrate other settings
    const autoExpandTools = localStorage.getItem('autoExpandTools') === 'true';
    if (autoExpandTools) {
      store.setAutoExpandTools(true);
    }

    const showRawParameters = localStorage.getItem('showRawParameters') === 'true';
    if (showRawParameters) {
      store.setShowRawParameters(true);
    }

    const autoScrollToBottom = localStorage.getItem('autoScrollToBottom');
    if (autoScrollToBottom === 'false') {
      store.setAutoScrollToBottom(false);
    }

    const sendByCtrlEnter = localStorage.getItem('sendByCtrlEnter') === 'true';
    if (sendByCtrlEnter) {
      store.setSendByCtrlEnter(true);
    }

    const tasksEnabled = localStorage.getItem('tasks-enabled');
    if (tasksEnabled === 'false') {
      store.setTasksEnabled(false);
    }

    // Detect mobile
    const checkMobile = () => {
      store.setIsMobile(window.innerWidth < 768);
    };
    checkMobile();

    // Detect PWA mode
    const isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                  (window.navigator as any).standalone;
    if (isPWA) {
      // Store doesn't have setPWA, but we can add it or just set it directly
      // For now, we'll just log it
      console.log('Running in PWA mode');
    }
  }, []);
}
