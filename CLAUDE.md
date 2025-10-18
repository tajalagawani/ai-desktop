# AI Desktop - Flow Architect System

**This project uses the modular Flow Architect agent system.**

The agent system is located in: `flow-architect/.claude/agents/flow-architect.md`

---

## Quick Start

When users ask you to create workflows, build APIs, or perform actions:

1. **Use the Flow Architect agent** by delegating to: `flow-architect/.claude/agents/flow-architect.md`
2. The agent will:
   - Classify the query into one of 10 categories
   - Load the appropriate context from `flow-architect/.claude/instructions/contexts/`
   - Read catalogs from `flow-architect/catalogs/`
   - Build and execute ACT flows

---

## System Architecture

```
flow-architect/
├── .claude/
│   ├── agents/
│   │   └── flow-architect.md          # Core routing agent (197 lines)
│   └── instructions/
│       ├── contexts/                   # 10 query-specific contexts
│       ├── examples/                   # 11 working example flows
│       ├── node-types/                 # Node reference docs (TODO)
│       ├── patterns/                   # Workflow patterns (TODO)
│       └── common/                     # Shared knowledge (TODO)
├── catalogs/
│   ├── service-catalog.json            # Available services
│   └── node-catalog.json               # Available node types
└── flows/                              # Generated workflows
```

---

## For All Requests

**Delegate to the Flow Architect agent:**

Read and follow the instructions in: `flow-architect/.claude/agents/flow-architect.md`

That agent will handle:
- Query classification
- Context loading
- Catalog reading
- Flow creation
- Execution via `/api/act/execute`

---

## Migration Note

This is the **modular system** that replaced the old monolithic CLAUDE.md files:
- Old `flow-architect/CLAUDE.md` (1,345 lines) → Archived as `.old-monolithic`
- Old `act-docker/CLAUDE.md` → Archived as `.old-action-builder`
- New modular system: 50% smaller context, easier to maintain

---

**Start by reading: `flow-architect/.claude/agents/flow-architect.md`**
