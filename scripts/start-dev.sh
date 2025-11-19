#!/bin/bash

# AI Desktop - Development Startup Script
# Starts both backend (port 3006) and frontend (port 3005)

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  AI Desktop Development Mode${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if PostgreSQL is running
echo -e "${YELLOW}→ Checking PostgreSQL...${NC}"
if ! pg_isready -q; then
    echo -e "${YELLOW}  Starting PostgreSQL...${NC}"
    brew services start postgresql@14
    sleep 2
fi
echo -e "${GREEN}✅ PostgreSQL is running${NC}"
echo ""

# Start backend
echo -e "${YELLOW}→ Starting Backend (port 3006)...${NC}"
cd backend
npm start &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 3
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Start frontend
echo -e "${YELLOW}→ Starting Frontend (port 3005)...${NC}"
npm run dev &
FRONTEND_PID=$!

# Wait a moment
sleep 2
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ All services running!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC} http://localhost:3005"
echo -e "${GREEN}Backend:${NC}  http://localhost:3006"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo -e '${YELLOW}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait for both processes
wait
