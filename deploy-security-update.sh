#!/usr/bin/env bash
#
# Deploy Security Updates to VPS
# This script uploads the security settings UI and agent SDK fixes
#

set -e

VPS_HOST="root@92.112.181.127"
VPS_DIR="/var/www/ai-desktop"

echo "====================================="
echo "Flow Builder Security Update"
echo "====================================="
echo ""

# Files to upload
FILES_TO_UPLOAD=(
  "lib/flow-builder/stores/settings-store.ts"
  "components/flow-builder/FlowBuilderSettings.tsx"
  "app/api/flow-builder/settings/route.ts"
  "app/api/flow-builder/messages/route.ts"
  "agent-sdk/index.js"
)

echo "📦 Files to upload:"
for file in "${FILES_TO_UPLOAD[@]}"; do
  echo "  - $file"
done
echo ""

# Upload files
echo "⬆️  Uploading files to VPS..."
for file in "${FILES_TO_UPLOAD[@]}"; do
  echo "  Uploading $file..."
  scp "$file" "${VPS_HOST}:${VPS_DIR}/$file"
done
echo "✓ Upload complete"
echo ""

# Add environment variable for sandbox bypass
echo "🔧 Configuring environment..."
ssh "$VPS_HOST" bash -c "'
cd $VPS_DIR

# Add ALLOW_SANDBOX_BYPASS to .env if not present
if ! grep -q \"ALLOW_SANDBOX_BYPASS\" .env; then
  echo \"\" >> .env
  echo \"# Security: Allow sandbox bypass for root execution\" >> .env
  echo \"ALLOW_SANDBOX_BYPASS=true\" >> .env
  echo \"✓ Added ALLOW_SANDBOX_BYPASS=true to .env\"
else
  echo \"✓ ALLOW_SANDBOX_BYPASS already in .env\"
fi
'"
echo ""

# Rebuild the app
echo "🔨 Building app on VPS..."
ssh "$VPS_HOST" bash -c "'
cd $VPS_DIR
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH

echo \"Removing old build...\"
rm -rf .next

echo \"Building app...\"
npm run build
'"
echo "✓ Build complete"
echo ""

# Restart PM2
echo "🔄 Restarting PM2 services..."
ssh "$VPS_HOST" bash -c "'
export PATH=/root/.nvm/versions/node/v22.11.0/bin:\$PATH
pm2 restart ai-desktop
pm2 save
'"
echo "✓ PM2 restarted"
echo ""

echo "====================================="
echo "✓ Deployment Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Open http://92.112.181.127 in your browser"
echo "2. Click 'Flow Builder' app"
echo "3. Click Settings (gear icon)"
echo "4. Go to Security tab"
echo "5. Read the warnings carefully"
echo "6. Enable 'Allow Sandbox Bypass' if you understand the risks"
echo "7. Save settings"
echo "8. Test creating a flow"
echo ""
