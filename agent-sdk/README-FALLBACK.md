# Agent SDK - Fallback Copy

⚠️ **Note**: This is a fallback copy of the agent-sdk.

## Recommended Setup

The desktop app should use the agent-sdk from the **actwith-mcp** repository:

### Local Mac
```bash
# Set in .env
AGENT_SDK_PATH=/Users/tajnoah/act/agent-sdk
```

### VPS
```bash
# Set in .env
AGENT_SDK_PATH=/var/www/act/agent-sdk
```

## When This Fallback is Used

If `AGENT_SDK_PATH` is not set in `.env`, the app will use this local copy as a fallback.

## Recommended: Use External ACT

For best practice, always set `AGENT_SDK_PATH` to point to the main actwith-mcp repository.
