                # PhishGuard - Sistema de Detecção de Phishing

**Avaliação Final - Tecnologias Hackers**

Sistema completo de detecção de phishing com análise avançada, Machine Learning, interface web e extensão para navegador Firefox.

---

## Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Componentes](#componentes)
- [Tecnologias](#tecnologias)
- [Requisitos Implementados](#requisitos-implementados)

---

## Visão Geral

PhishGuard é um sistema abrangente de detecção de phishing que combina múltiplas técnicas de análise:

- **Análise Heurística Avançada**: Verificação de domínios, SSL, WHOIS, DNS
- **Machine Learning Pré-Treinado**: Random Forest com dataset UCI (2.000+ URLs reais)
- **Análise de Conteúdo**: Detecção de formulários, scripts maliciosos e técnicas de manipulação
- **Interface Web Completa**: Dashboard interativo com visualizações e histórico
- **Extensão para Navegador**: Plugin Firefox com verificação em tempo real

### Modelo de Machine Learning

O sistema utiliza um **modelo pré-treinado** com características de phishing conhecidas:

- **Dataset**: UCI Phishing Websites (2.000 URLs reais)
- **Algoritmo**: Random Forest (200 estimators, max_depth=15)
- **Features analisadas**: 11 características incluindo:
  - Comprimento da URL
  - Número de subdomínios
  - Presença de caracteres especiais
  - Idade do domínio (WHOIS)
  - Informações de geolocalização IP
  - Presença de IP na URL
  - Uso de HTTPS
  - Padrões suspeitos
- **Acurácia**: 100% no dataset de treinamento
- **Modelo explicável**: Mostra quais features foram mais importantes na decisão

---

## Funcionalidades

### Análise de URLs

#### Verificação Básica
- Verificação em listas de phishing (PhishTank, OpenPhish)
- Detecção de números substituindo letras
- Identificação de excesso de subdomínios
- Detecção de caracteres especiais suspeitos
- Interface web básica com indicadores visuais

#### Análise Heurística Avançada
- Todas as verificações básicas
- Análise de idade do domínio (WHOIS)
- Verificação de DNS dinâmico
- Análise de certificados SSL
- Detecção de redirecionamentos suspeitos
- Similaridade com marcas conhecidas (Levenshtein Distance)
- Análise de conteúdo e formulários
- Dashboard interativo com histórico exportável

#### Sistema Avançado com Machine Learning
- Plugin para Firefox com verificação em tempo real
- Monitoramento ativo de todas as páginas
- Notificações em tempo real
- Bloqueio preventivo opcional
- Personalização de sensibilidade
- Whitelist de sites confiáveis
- Análise de links ao passar o mouse
- Dashboard analítico completo
- Machine Learning com Random Forest
- Score de risco quantitativo (0-100)
- Modelo de decisão explicável
- Análise de código-fonte e scripts
- Detecção de técnicas de manipulação
- Verificação de URLs encurtadas
- Análise de comportamento do site

---

## 🏗️ Arquitetura

```
PhishGuard/
├── backend/                    # API Flask
│   ├── app.py                 # Aplicação principal
│   ├── analyzers/             # Módulos de análise
│   │   ├── url_analyzer.py   # Análise heurística
│   │   ├── content_analyzer.py # Análise de conteúdo
│   │   └── ml_classifier.py  # Machine Learning
│   ├── database/
│   │   └── history.py        # Gerenciamento de histórico
│   └── requirements.txt
│
├── frontend/                   # Interface React
│   ├── src/
│   │   ├── App.js            # Componente principal
│   │   ├── components/       # Componentes React
│   │   │   ├── URLScanner.js
│   │   │   ├── ResultsDisplay.js
│   │   │   ├── HistoryView.js
│   │   │   ├── Statistics.js
│   │   │   └── Dashboard.js
│   │   └── App.css
│   └── package.json
│
└── extension/                  # Extensão Firefox
    ├── manifest.json
    ├── background.js          # Script de background
    ├── content.js            # Content script
    ├── popup/
    │   ├── popup.html
    │   └── popup.js
    └── warning.html          # Página de bloqueio
```

---

## Instalação

### Pré-requisitos

- Python 3.8+
- Node.js 16+
- Firefox (para extensão)

### 1. Backend (API Flask)

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python app.py
```

O backend estará disponível em `http://localhost:5000`

### 2. Frontend (React)

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar aplicação
npm start
```

O frontend estará disponível em `http://localhost:3000`

### 3. Extensão Firefox

1. Abra Firefox
2. Digite `about:debugging` na barra de endereços
3. Clique em "Este Firefox"
4. Clique em "Carregar extensão temporária"
5. Navegue até a pasta `extension` e selecione `manifest.json`

---

## 📖 Uso

### Rodar o Sistema

Execute o script de inicialização na raiz do projeto:

```bash
./start.sh
```

O script irá:
1. Iniciar o backend Flask em `http://localhost:5000`
2. Iniciar o frontend React em `http://localhost:3000`


### Parar o Sistema

Para encerrar o backend e frontend:

```bash
./stop.sh
```

### Interface Web

1. Acesse `http://localhost:3000`
2. Digite a URL que deseja analisar
3. Clique em "Analisar"
4. Visualize os resultados detalhados:
   - Score de risco (0-100)
   - Classificação (SAFE, LOW_RISK, MEDIUM_RISK, HIGH_RISK, CRITICAL)
   - Análise heurística completa
   - Predição de Machine Learning
   - Recomendações de segurança

### Extensão Firefox

**Como Carregar a Extensão:**

1. Abra o Firefox
2. Digite `about:debugging` na barra de endereços
3. Clique em "Este Firefox" (ou "This Firefox")
4. Clique em "Carregar extensão temporária" (ou "Load Temporary Add-on")
5. Navegue até a pasta `extension/` do projeto
6. Selecione o arquivo `manifest.json`

**Funcionalidades da Extensão:**

- Monitora automaticamente todas as URLs visitadas
- Badge colorido indica nível de risco:
  - Verde (✓): Site seguro
  - Amarelo (!): Risco médio
  - Vermelho (!!!): Site perigoso
- Passe o mouse sobre links para ver análise prévia
- Clique no ícone para ver detalhes da página atual
- Configure bloqueio automático e sensibilidade nas configurações
- Adicione sites confiáveis à whitelist

### API REST

#### Analisar URL
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://exemplo.com"}'
```

#### Obter Histórico
```bash
curl http://localhost:5000/api/history
```

#### Obter Estatísticas
```bash
curl http://localhost:5000/api/stats
```

---

## 🧩 Componentes

### Backend

#### URLAnalyzer
- Verificação em blacklists (PhishTank)
- Análise de características do domínio
- Similaridade com marcas (Levenshtein)
- Análise WHOIS (idade do domínio)
- Verificação SSL
- Análise DNS
- Detecção de redirecionamentos
- URLs encurtadas

#### ContentAnalyzer
- Detecção de formulários de login
- Verificação de informações sensíveis
- Detecção de logos de marcas
- Análise de scripts maliciosos
- Técnicas de manipulação
- Práticas SEO maliciosas
- Temporizadores de urgência
- Análise OAuth

#### MLClassifier
- Random Forest Classifier
- Features: comprimento URL, subdomínios, caracteres especiais, idade do domínio, etc.
- Probabilidade de phishing
- Importância de features
- Score de confiança

### Frontend

#### URLScanner
- Input de URL
- Botão de análise
- URLs de exemplo
- Lista de funcionalidades

#### ResultsDisplay
- Score de risco visual
- Badge de classificação
- Recomendações
- Predição ML
- Análise heurística detalhada
- Análise de conteúdo

#### HistoryView
- Tabela de histórico
- Exportação CSV
- Filtros e ordenação

#### Statistics
- Cards de estatísticas
- Gráfico de pizza (distribuição)
- Gráfico de barras (classificações)
- Insights

#### Dashboard
- Visão geral
- Análises recentes
- Recursos do sistema

### Extensão

#### Background Script
- Monitoramento de requisições
- Cache de resultados
- Gerenciamento de whitelist
- Notificações
- Bloqueio automático

#### Content Script
- Tooltip ao passar mouse
- Análise prévia de links

#### Popup
- Status da página atual
- Configurações
- Whitelist
- Análise manual

---

## 🛠️ Tecnologias

### Backend
- **Flask**: Framework web
- **BeautifulSoup4**: Parsing HTML
- **python-whois**: Análise WHOIS
- **python-Levenshtein**: Cálculo de similaridade
- **dnspython**: Análise DNS
- **scikit-learn**: Machine Learning
- **NumPy**: Computação numérica

### Frontend
- **React**: Framework UI
- **Axios**: Cliente HTTP
- **Recharts**: Visualizações
- **Lucide React**: Ícones

### Extensão
- **WebExtensions API**: APIs do navegador
- **Firefox Manifest V2**: Estrutura da extensão

---

## Requisitos Implementados

### Plugin para Navegador Web com Verificação em Tempo Real

- **Integração com navegador**: Plugin para Firefox
- **Monitoramento ativo**: Verificação de todas as páginas em tempo real
- **Notificações em tempo real**: Alertas quando site suspeito é detectado
- **Bloqueio preventivo**: Opção para bloquear automaticamente phishing
- **Personalização**: Níveis de sensibilidade e whitelist
- **Análise de links**: Verificação ao passar mouse

### Sistema Web Avançado com Machine Learning

- **Dashboard analítico**: Interface completa com visualizações
- **Machine learning**: Random Forest com múltiplas características
  - Comprimento da URL
  - Número de subdomínios
  - Presença de caracteres especiais
  - Idade do domínio
  - Informações WHOIS
  - Palavras-chave de phishing
  - Geolocalização IP
- **Análise de reputação do host**: Verificação em blacklists
- **Modelo de decisão explicável**: Features mais importantes
- **Avaliação de risco quantitativa**: Score 0-100 com fatores

### Características Adicionais Avançadas

- **Análise do código-fonte**: Scripts maliciosos e ofuscação
- **Verificação SEO maliciosas**: Keyword stuffing, cloaking
- **URLs encurtadas**: Detecção de serviços de encurtamento
- **Detecção de phishing zero-day**: ML para novas ameaças
- **Análise de comportamento do site**:
  - Bloqueio de clique direito
  - Ocultação de URL real
  - Manipulação de DOM
  - Temporizadores de urgência

---

## Score de Risco

O sistema calcula um score de 0 a 100:

- **0-20**: SAFE (Seguro) - Verde
- **20-40**: LOW_RISK (Baixo Risco) - Verde Claro
- **40-60**: MEDIUM_RISK (Médio Risco) - Amarelo
- **60-80**: HIGH_RISK (Alto Risco) - Laranja
- **80-100**: CRITICAL (Crítico) - Vermelho

O score é calculado combinando:
- 35% Análise Heurística
- 30% Análise de Conteúdo
- 35% Machine Learning

---

## Segurança

- Todas as análises são feitas localmente ou via API própria
- Nenhuma informação sensível é enviada para terceiros
- Cache local para melhor performance
- Whitelist para sites confiáveis
- Bloqueio preventivo opcional

---
