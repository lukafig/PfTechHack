#!/bin/bash

# Script para parar o PhishGuard

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "> Parando PhishGuard..."
echo ""

# Parar por PIDs salvos
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}> Backend parado (PID: $BACKEND_PID)${NC}"
    fi
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}> Frontend parado (PID: $FRONTEND_PID)${NC}"
    fi
    rm .frontend.pid
fi

# Garantir que tudo foi parado
pkill -f "python3.*app.py" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null
pkill -f "npm.*start" 2>/dev/null

sleep 1

echo ""
echo -e "${GREEN}> PhishGuard encerrado${NC}"
