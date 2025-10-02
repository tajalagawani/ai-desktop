#!/bin/bash
# AI Desktop - Comprehensive UFW Security Setup
# Based on Hostinger UFW best practices

set -e

echo "=== AI Desktop Security Setup ==="
echo ""

# Step 1: Fix Docker sources
echo "Step 1: Fixing Docker apt sources..."
if [ -f /etc/apt/sources.list.d/docker.list ]; then
    sudo rm /etc/apt/sources.list.d/docker.list
    echo "✓ Removed corrupted Docker sources"
fi

# Step 2: Update package list
echo ""
echo "Step 2: Updating package list..."
sudo apt-get update

# Step 3: Install UFW
echo ""
echo "Step 3: Installing UFW firewall..."
sudo apt-get install -y ufw

# Step 4: Set default policies (CRITICAL - deny all incoming, allow outgoing)
echo ""
echo "Step 4: Setting default policies..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
echo "✓ Default policies set (deny incoming, allow outgoing)"

# Step 5: Allow essential services BEFORE enabling
echo ""
echo "Step 5: Allowing essential services..."
sudo ufw allow 22/tcp comment 'SSH access'
sudo ufw allow 80/tcp comment 'HTTP - AI Desktop'
echo "✓ SSH (22) and HTTP (80) allowed"

# Step 6: Enable UFW
echo ""
echo "Step 6: Enabling UFW firewall..."
sudo ufw --force enable
echo "✓ UFW enabled"

# Step 7: Enable logging
echo ""
echo "Step 7: Enabling security logging..."
sudo ufw logging on
echo "✓ UFW logging enabled"

# Step 8: Show current status
echo ""
echo "=== Current UFW Status ==="
sudo ufw status verbose

echo ""
echo "=== Setup Complete ==="
echo "✓ UFW installed and configured with secure defaults"
echo "✓ Only SSH (22) and HTTP (80) are open"
echo "✓ All other incoming connections blocked"
echo "✓ Logging enabled for security monitoring"
echo ""
echo "Next steps:"
echo "1. Run: bash scripts/create-ufw-profiles.sh"
echo "2. Install services from AI Desktop app"
echo "3. Ports will be opened automatically with proper rules"
echo "4. Monitor firewall logs: sudo tail -f /var/log/ufw.log"
