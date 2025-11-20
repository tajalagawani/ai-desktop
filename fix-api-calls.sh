#!/bin/bash
# Script to fix all fetch('/api/...') calls to use apiFetch

# List of files to fix (from grep results, excluding Desktop.tsx, FileManager.tsx, VSCodeManager.tsx which are already fixed)
files=(
  "src/components/features/github/diff-panel.tsx"
  "src/components/features/github/views/stashes-view.tsx"
  "src/components/features/github/views/pull-requests-view.tsx"
  "src/components/features/github/views/branches-view.tsx"
  "src/components/features/github/views/history-view.tsx"
  "src/components/features/github/views/changes-view.tsx"
  "src/components/features/github/header.tsx"
  "src/components/features/service-manager/ServiceManager.tsx"
  "src/components/features/mcp-hub/MCPHub.tsx"
  "src/components/features/flow-builder/SessionList.tsx"
  "src/components/features/flow-builder/ChatMessage.tsx"
  "src/components/features/flow-builder/ChatInterface.tsx"
  "src/components/features/flow-builder/ChatInput.tsx"
  "src/components/features/service-manager/ServiceDetails.tsx"
  "src/components/features/github/clone-dialog.tsx"
  "src/components/features/github/views/tags-view.tsx"
  "src/components/layout/desktop/ChangelogModal.tsx"
  "src/components/features/vscode/deploy-config.tsx"
  "src/components/features/vscode/delete-dialog.tsx"
  "src/components/features/vscode/clone-dialog.tsx"
  "src/components/features/system-monitor/SystemMonitor.tsx"
  "src/components/features/service-manager/ServiceViewer.tsx"
  "src/components/features/github/settings-dialog.tsx"
  "src/components/features/vscode/deployment-card.tsx"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Processing: $file"

    # Check if apiFetch import already exists
    if ! grep -q "import.*apiFetch.*from.*@/lib/utils/api" "$file"; then
      # Find the last import statement and add after it
      sed -i '' '/^import/,/^import/{
        /^import/!b
        :a
        n
        /^import/ba
        /^$/i\
import { apiFetch } from "@/lib/utils/api"
      }' "$file"
    fi

    # Replace all fetch('/api/ with apiFetch('/api/
    sed -i '' 's/fetch(\x27\/api\//apiFetch(\x27\/api\//g' "$file"
    sed -i '' 's/fetch("\/api\//apiFetch("\/api\//g' "$file"

    echo "  ✓ Fixed $file"
  else
    echo "  ⚠ File not found: $file"
  fi
done

echo ""
echo "Done! Fixed all API calls."
