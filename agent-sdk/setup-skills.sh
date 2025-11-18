#!/bin/bash
#
# Setup ACT Flow Architect Skills
# Copies skills to user's .claude directory for Claude Code to load
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_SKILLS_DIR="$HOME/.claude/skills"
SKILL_NAME="act-flow-architect"

echo "🔧 Setting up ACT Flow Architect Skills..."
echo ""

# Create user skills directory if it doesn't exist
if [ ! -d "$USER_SKILLS_DIR" ]; then
    echo "📁 Creating skills directory: $USER_SKILLS_DIR"
    mkdir -p "$USER_SKILLS_DIR"
fi

# Copy skills from project to user directory
SOURCE_DIR="$SCRIPT_DIR/.claude/skills/$SKILL_NAME"
TARGET_DIR="$USER_SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source skills not found at $SOURCE_DIR"
    exit 1
fi

echo "📋 Copying skills from project to user directory..."
echo "   Source: $SOURCE_DIR"
echo "   Target: $TARGET_DIR"

# Remove old skills if they exist
if [ -d "$TARGET_DIR" ]; then
    echo "🗑️  Removing old skills..."
    rm -rf "$TARGET_DIR"
fi

# Copy new skills
cp -r "$SOURCE_DIR" "$TARGET_DIR"

echo ""
echo "✅ Skills installed successfully!"
echo ""
echo "Skills location: $TARGET_DIR"
echo ""
echo "Files installed:"
ls -1 "$TARGET_DIR"
echo ""
echo "The skills will be loaded automatically by Claude Code when running the agent."
echo ""
