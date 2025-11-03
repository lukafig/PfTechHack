#!/bin/bash

echo "🛡️  PhishGuard - Sistema de Detecção de Phishing"
echo "=================================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Verificar Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale Node.js 16+"
    exit 1
fi

echo "✓ Python e Node.js encontrados"
echo ""

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p backend/data
mkdir -p backend/models
mkdir -p extension/icons

# Setup Backend
echo ""
echo "🐍 Configurando Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "Ativando ambiente virtual..."
source venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "✓ Backend configurado"
cd ..

# Setup Frontend
echo ""
echo "⚛️  Configurando Frontend..."
cd frontend

echo "Instalando dependências..."
npm install

echo "✓ Frontend configurado"
cd ..

# Criar ícones da extensão (placeholders)
echo ""
echo "🎨 Criando ícones da extensão..."
# Aqui você pode adicionar comandos para gerar ícones ou usar placeholders

echo ""
echo "=================================================="
echo "✅ Instalação concluída com sucesso!"
echo ""
echo "Para iniciar o sistema:"
echo ""
echo "1. Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "2. Frontend (em outro terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Extensão Firefox:"
echo "   - Abra Firefox"
echo "   - Digite about:debugging"
echo "   - Clique em 'Este Firefox'"
echo "   - Clique em 'Carregar extensão temporária'"
echo "   - Selecione extension/manifest.json"
echo ""
echo "=================================================="
