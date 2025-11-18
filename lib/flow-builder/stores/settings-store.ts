import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface FlowBuilderSettings {
  // ACT Configuration
  actRoot: string;
  agentScriptPath: string;

  // API Configuration
  anthropicApiKey: string;

  // Agent Configuration
  defaultModel: string;
  defaultUserId: string;
  debugMode: boolean;
  verboseMode: boolean;

  // Security Configuration
  allowSandboxBypass: boolean;

  // UI Configuration
  autoScroll: boolean;
  showTimestamps: boolean;
  messageLimit: number;
}

interface SettingsState {
  settings: FlowBuilderSettings;
  updateSetting: <K extends keyof FlowBuilderSettings>(key: K, value: FlowBuilderSettings[K]) => void;
  updateSettings: (settings: Partial<FlowBuilderSettings>) => void;
  resetSettings: () => void;
}

const defaultSettings: FlowBuilderSettings = {
  // ACT Configuration
  actRoot: process.env.NEXT_PUBLIC_ACT_ROOT || '/Users/tajnoah/act',
  agentScriptPath: process.env.NEXT_PUBLIC_ACT_AGENT_SCRIPT || '',

  // API Configuration
  anthropicApiKey: process.env.NEXT_PUBLIC_ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY || '',

  // Agent Configuration
  defaultModel: process.env.NEXT_PUBLIC_FLOW_BUILDER_MODEL || 'claude-sonnet-4-20250514',
  defaultUserId: process.env.NEXT_PUBLIC_FLOW_BUILDER_USER_ID || 'default-user',
  debugMode: process.env.NEXT_PUBLIC_FLOW_BUILDER_DEBUG === 'true',
  verboseMode: process.env.NEXT_PUBLIC_FLOW_BUILDER_VERBOSE === 'true',

  // Security Configuration
  allowSandboxBypass: false,  // Default to SECURE - user must explicitly enable

  // UI Configuration
  autoScroll: true,
  showTimestamps: true,
  messageLimit: 100,
};

export const useFlowSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: defaultSettings,

      updateSetting: (key, value) =>
        set((state) => ({
          settings: {
            ...state.settings,
            [key]: value,
          },
        })),

      updateSettings: (newSettings) =>
        set((state) => ({
          settings: {
            ...state.settings,
            ...newSettings,
          },
        })),

      resetSettings: () =>
        set({
          settings: defaultSettings,
        }),
    }),
    {
      name: 'flow-builder-settings',
    }
  )
);
