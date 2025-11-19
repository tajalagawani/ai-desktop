# AI Desktop - Architecture

## Directory Structure

```
ai-desktop/
├── src/                             # Source code
│   ├── app/                         # Next.js app directory
│   ├── components/                  # React components (by feature)
│   │   ├── ui/                      # Base UI (shadcn/ui)
│   │   ├── layout/                  # Layout components
│   │   ├── features/                # Feature components
│   │   ├── shared/                  # Shared components
│   │   └── auth/                    # Auth components
│   ├── lib/                         # Core libraries
│   │   ├── api/                     # API clients
│   │   ├── hooks/                   # React hooks
│   │   ├── stores/                  # State management
│   │   ├── services/                # Business logic
│   │   ├── utils/                   # Utilities
│   │   └── config/                  # Configuration
│   ├── data/                        # Static data
│   ├── types/                       # TypeScript types
│   └── styles/                      # Global styles
│
├── backend/                         # Backend server
│   ├── app/api/                     # API routes
│   ├── app/websocket/               # WebSocket handlers
│   └── server.js                    # Entry point
│
├── storage/                         # Runtime data (gitignored)
│   ├── data/                        # JSON database
│   ├── logs/                        # Log files
│   └── flows/                       # Generated workflows
│
├── public/                          # Static assets
└── docs/                            # Documentation
```

## Key Principles

1. **Feature-Based Organization**: Components organized by feature, not type
2. **Separation of Concerns**: Source code (src/) vs runtime data (storage/)
3. **Clear Module Boundaries**: Each module has a single responsibility
4. **Scalable Structure**: Easy to add new features without refactoring

## Import Paths

Use TypeScript path aliases:
```typescript
import { Button } from '@/components/ui/button'
import { useDesktop } from '@/lib/hooks'
import { DesktopStore } from '@/lib/stores'
import type { AppConfig } from '@/types'
```

## State Management

- Zustand for global state
- React hooks for local state
- Server state via API clients

## Styling

- Tailwind CSS for styling
- shadcn/ui for base components
- CSS modules for component-specific styles
