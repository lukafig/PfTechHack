#!/bin/bash

# Script para iniciar o PhishGuard completo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "> Iniciando PhishGuard..."
echo ""

# Parar processos anteriores
echo "> Parando processos anteriores..."
pkill -f "python3.*app.py" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null
pkill -f "npm.*start" 2>/dev/null
pkill -f "node.*react-scripts" 2>/dev/null

# Matar processos nas portas
lsof -ti:5000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null

sleep 3

echo ""
echo -e "${GREEN}> Iniciando Backend (Flask)...${NC}"

# Iniciar backend (sem venv)
cd backend
python3 app.py > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

sleep 3

# Verificar se backend iniciou
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend rodando (PID: $BACKEND_PID)${NC}"
    echo -e "  📍 http://localhost:5000"
else
    echo -e "${RED}✗ Erro ao iniciar backend!${NC}"
    echo "Execute: cd backend && python3 app.py"
    exit 1
fi

echo ""
echo -e "${GREEN}>  Iniciando Frontend (React)...${NC}"

# Iniciar frontend
cd frontend
npm start > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${YELLOW}> Aguardando React compilar (15s)...${NC}"
sleep 15

# Verificar se frontend iniciou
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend rodando (PID: $FRONTEND_PID)${NC}"
    echo -e "  📍 http://localhost:3000"
else
    echo -e "${RED}✗ Erro ao iniciar frontend!${NC}"
    echo "Execute: cd frontend && npm start"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}> PhishGuard está ONLINE!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "> Serviços:"
echo -e "  Backend:  ${GREEN}http://localhost:5000${NC}"
echo -e "  Frontend: ${GREEN}http://localhost:3000${NC}"
echo ""
echo "️  7 Analyzers ativos:"
echo "  🔍 Heurística | 📝 Conteúdo | 🧠 ML"
echo "  🗺️ Geolocalização | 🛡️ OAuth | 🚫 Blacklist | 📷 Screenshot"
echo ""
echo -e "${GREEN}> Abra: http://localhost:3000${NC}"
echo ""

# Salvar PIDs
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
