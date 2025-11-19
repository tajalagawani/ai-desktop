import { create } from 'zustand';
import type { SessionData, ResultData } from '@/lib/flow-builder/utils/log-parser';

interface SessionStore {
  sessionData: SessionData | null;
  resultData: ResultData | null;
  setSessionData: (data: SessionData) => void;
  setResultData: (data: ResultData) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessionData: null,
  resultData: null,
  setSessionData: (data) => set({ sessionData: data }),
  setResultData: (data) => set({ resultData: data }),
  clearSession: () => set({ sessionData: null, resultData: null }),
}));
