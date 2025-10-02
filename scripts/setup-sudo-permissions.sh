#!/bin/bash
# Allow Node.js to manage firewall without password

# Get current user
USER=$(whoami)

# Create sudoers file for firewall commands
sudo tee /etc/sudoers.d/ai-desktop-firewall > /dev/null << SUDOERS
# AI Desktop - Allow firewall management
$USER ALL=(ALL) NOPASSWD: /usr/sbin/ufw
$USER ALL=(ALL) NOPASSWD: /usr/sbin/iptables
$USER ALL=(ALL) NOPASSWD: /usr/bin/firewall-cmd
SUDOERS

# Set correct permissions
sudo chmod 0440 /etc/sudoers.d/ai-desktop-firewall

echo "✅ Sudo permissions configured for firewall management"
echo "The app can now automatically open ports when installing services"
