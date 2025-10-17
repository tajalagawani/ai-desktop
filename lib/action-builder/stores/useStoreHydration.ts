// Hook to hydrate store with client-side values after initial render
// This prevents hydration mismatches while still loading localStorage values

import { useEffect } from 'react';
import { useChatStore } from './chatStore';

export function useStoreHydration() {
  const store = useChatStore();

  useEffect(() => {
    // Only run on client side after hydration
    if (typeof window === 'undefined') return;

    // Load auth token
    const token = localStorage.getItem('auth-token');
    if (token) {
      store.setToken(token);
    }

    // Load UI preferences
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode !== store.isDarkMode) {
      store.toggleDarkMode();
    }

    const devMode = localStorage.getItem('dev_mode') === 'true';
    if (devMode !== store.isDevMode) {
      store.toggleDevMode();
    }

    // Load settings
    const autoExpandTools = localStorage.getItem('autoExpandTools') === 'true';
    if (autoExpandTools !== store.autoExpandTools) {
      store.setAutoExpandTools(autoExpandTools);
    }

    const showRawParameters = localStorage.getItem('showRawParameters') === 'true';
    if (showRawParameters !== store.showRawParameters) {
      store.setShowRawParameters(showRawParameters);
    }

    const autoScrollToBottom = localStorage.getItem('autoScrollToBottom') !== 'false';
    if (autoScrollToBottom !== store.autoScrollToBottom) {
      store.setAutoScrollToBottom(autoScrollToBottom);
    }

    const sendByCtrlEnter = localStorage.getItem('sendByCtrlEnter') === 'true';
    if (sendByCtrlEnter !== store.sendByCtrlEnter) {
      store.setSendByCtrlEnter(sendByCtrlEnter);
    }

    const tasksEnabled = localStorage.getItem('tasks-enabled') !== 'false';
    if (tasksEnabled !== store.tasksEnabled) {
      store.setTasksEnabled(tasksEnabled);
    }

    // Detect mobile
    const checkMobile = () => {
      store.setIsMobile(window.innerWidth < 768);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);

    // Detect PWA
    const isPWA = window.matchMedia('(display-mode: standalone)').matches || (window.navigator as any).standalone;
    if (isPWA) {
      document.documentElement.classList.add('pwa-mode');
      document.body.classList.add('pwa-mode');
    }

    return () => {
      window.removeEventListener('resize', checkMobile);
    };
  }, []);
}
