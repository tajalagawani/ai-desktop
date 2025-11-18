#!/bin/bash
#
# ACT Agent SDK - Complete Setup Script
# Verifies and configures all components: Skills, MCP Server, and Environment
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "════════════════════════════════════════════════════════"
echo "  ACT Agent SDK - Complete Setup"
echo "════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Check Node.js installation
print_status "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# 2. Check Python installation
print_status "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# 3. Install npm dependencies
print_status "Installing npm dependencies..."
cd "$SCRIPT_DIR"
if [ -f "package.json" ]; then
    npm install --silent
    print_success "npm dependencies installed"
else
    print_error "package.json not found"
    exit 1
fi

# 4. Setup Agent Skills
print_status "Setting up Agent Skills..."
USER_SKILLS_DIR="$HOME/.claude/skills"
SKILL_NAME="act-flow-architect"
SOURCE_DIR="$SCRIPT_DIR/.claude/skills/$SKILL_NAME"
TARGET_DIR="$USER_SKILLS_DIR/$SKILL_NAME"

if [ ! -d "$USER_SKILLS_DIR" ]; then
    mkdir -p "$USER_SKILLS_DIR"
    print_success "Created skills directory: $USER_SKILLS_DIR"
fi

if [ -d "$SOURCE_DIR" ]; then
    # Remove old skills if they exist
    if [ -d "$TARGET_DIR" ]; then
        rm -rf "$TARGET_DIR"
    fi

    # Copy new skills
    cp -r "$SOURCE_DIR" "$TARGET_DIR"
    print_success "Skills installed: $TARGET_DIR"

    # List installed skill files
    echo "   Files:"
    ls -1 "$TARGET_DIR" | sed 's/^/      - /'
else
    print_warning "Skills source directory not found: $SOURCE_DIR"
fi

# 5. Verify MCP Server
print_status "Verifying MCP Server..."
MCP_SERVER="$ACT_ROOT/mcp/index.js"
if [ -f "$MCP_SERVER" ]; then
    print_success "MCP Server found: $MCP_SERVER"

    # Test MCP server can start
    print_status "Testing MCP Server startup..."
    timeout 3 node "$MCP_SERVER" 2>&1 | grep -q "Flow Architect MCP Server" && \
        print_success "MCP Server test passed" || \
        print_warning "MCP Server test inconclusive (may still work)"
else
    print_error "MCP Server not found: $MCP_SERVER"
    exit 1
fi

# 6. Check environment configuration
print_status "Checking environment configuration..."
if [ -f "$SCRIPT_DIR/.env" ]; then
    print_success "Found .env file"

    # Check for API key
    if grep -q "ANTHROPIC_API_KEY=sk-ant-" "$SCRIPT_DIR/.env"; then
        print_success "Anthropic API key configured"
    else
        print_warning "Anthropic API key not found in .env"
        echo "   Please add your API key to $SCRIPT_DIR/.env"
        echo "   Example: ANTHROPIC_API_KEY=sk-ant-your-key-here"
    fi
else
    print_warning ".env file not found"
    echo "   Creating from example..."
    if [ -f "$SCRIPT_DIR/.env.example" ]; then
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        print_success "Created .env from example"
        print_warning "Please edit $SCRIPT_DIR/.env and add your ANTHROPIC_API_KEY"
    else
        print_error ".env.example not found"
    fi
fi

# 7. Verify ACT catalog
print_status "Verifying ACT catalog..."
CATALOG_FILE="$ACT_ROOT/catalog.json"
if [ -f "$CATALOG_FILE" ]; then
    NODE_COUNT=$(python3 -c "import json; print(len(json.load(open('$CATALOG_FILE'))['nodes']))" 2>/dev/null || echo "0")
    if [ "$NODE_COUNT" -gt 0 ]; then
        print_success "ACT catalog found: $NODE_COUNT nodes available"
    else
        print_warning "ACT catalog appears empty"
    fi
else
    print_warning "ACT catalog not found: $CATALOG_FILE"
    echo "   The agent may not be able to discover available nodes"
fi

# 8. Create flows directory
print_status "Setting up flows directory..."
FLOWS_DIR="$ACT_ROOT/flows"
if [ ! -d "$FLOWS_DIR" ]; then
    mkdir -p "$FLOWS_DIR"
    print_success "Created flows directory: $FLOWS_DIR"
else
    print_success "Flows directory exists: $FLOWS_DIR"
fi

# 9. Final summary
echo ""
echo "════════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "════════════════════════════════════════════════════════"
echo ""
print_success "Agent SDK is ready to use"
echo ""
echo "Quick Start:"
echo "  1. Add your API key to: $SCRIPT_DIR/.env"
echo "  2. Run: node index.js \"create a hello world API\""
echo "  3. Or: ./debug-run.sh \"your request here\""
echo ""
echo "Environment Variables (optional):"
echo "  ACT_AGENT_MODEL - Model to use (default: claude-sonnet-4-20250514)"
echo "  VERBOSE         - Enable debug output (true/false)"
echo ""
echo "Documentation:"
echo "  README: $SCRIPT_DIR/README.md"
echo "  Skills: $TARGET_DIR/SKILL.md"
echo ""
