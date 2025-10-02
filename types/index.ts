/**
 * Centralized TypeScript type exports
 * Import types from here instead of individual files
 */

// Export types from app.types.ts
export type * from "./app.types"

// Re-export commonly used types from data files
export type { AppConfig, WindowConfig, DesktopFolder } from "@/data/desktop-apps"

// Future: Add more type exports as needed
// export type * from "./user.types"
// export type * from "./workflow.types"
// export type * from "./api.types"
