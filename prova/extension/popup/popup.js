// Popup Script
const API_URL = 'http://localhost:5000';

let currentTab = null;
let settings = null;
let whitelist = [];

// Inicializar
document.addEventListener('DOMContentLoaded', async () => {
  // Obter tab atual
  const tabs = await browser.tabs.query({ active: true, currentWindow: true });
  currentTab = tabs[0];
  
  // Carregar configurações
  const response = await browser.runtime.sendMessage({ action: 'getSettings' });
  settings = response.settings;
  whitelist = response.whitelist;
  
  // Atualizar UI
  updateUI();
  loadSettings();
  loadWhitelist();
  
  // Verificar status da página atual
  checkCurrentPage();
  
  // Configurar event listeners
  setupEventListeners();
});

// Atualizar UI com informações da página
function updateUI() {
  const urlElement = document.getElementById('currentUrl');
  if (currentTab && currentTab.url) {
    const url = new URL(currentTab.url);
    urlElement.textContent = url.hostname;
  }
}

// Verificar página atual
async function checkCurrentPage() {
  if (!currentTab || !currentTab.url) return;
  
  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: currentTab.url })
    });
    
    const result = await response.json();
    displayResult(result);
  } catch (error) {
    console.error('Erro ao analisar:', error);
    document.getElementById('statusTitle').textContent = 'Erro na Análise';
    document.getElementById('statusDescription').textContent = 'Não foi possível conectar ao servidor';
  }
}

// Exibir resultado
function displayResult(result) {
  const statusCircle = document.getElementById('statusCircle');
  const statusIcon = document.getElementById('statusIcon');
  const statusTitle = document.getElementById('statusTitle');
  const statusDescription = document.getElementById('statusDescription');
  
  statusCircle.className = 'status-circle';
  
  if (result.is_safe) {
    statusCircle.classList.add('safe');
    statusIcon.textContent = '✓';
    statusTitle.textContent = 'Site Seguro';
    statusTitle.style.color = '#43e97b';
    statusDescription.textContent = `Score de Risco: ${result.risk_score}/100`;
  } else {
    statusCircle.classList.add('danger');
    statusIcon.textContent = '⚠';
    statusTitle.textContent = 'Site Suspeito!';
    statusTitle.style.color = '#E74C3C';
    statusDescription.textContent = `Score de Risco: ${result.risk_score}/100 - CUIDADO!`;
  }
}

// Carregar configurações
function loadSettings() {
  document.getElementById('enabledToggle').checked = settings.enabled;
  document.getElementById('autoBlockToggle').checked = settings.autoBlock;
  document.getElementById('notificationsToggle').checked = settings.showNotifications;
  document.getElementById('sensitivitySelect').value = settings.sensitivity;
}

// Carregar whitelist
function loadWhitelist() {
  const container = document.getElementById('whitelistContainer');
  
  if (whitelist.length === 0) {
    container.innerHTML = '<p style="text-align: center; color: #999; font-size: 13px;">Nenhum site adicionado</p>';
    return;
  }
  
  container.innerHTML = '';
  whitelist.forEach(domain => {
    const item = document.createElement('div');
    item.className = 'whitelist-item';
    item.innerHTML = `
      <span>${domain}</span>
      <button onclick="removeFromWhitelist('${domain}')">✕</button>
    `;
    container.appendChild(item);
  });
}

// Configurar event listeners
function setupEventListeners() {
  // Analisar novamente
  document.getElementById('analyzeBtn').addEventListener('click', () => {
    checkCurrentPage();
  });
  
  // Adicionar à whitelist
  document.getElementById('addWhitelistBtn').addEventListener('click', async () => {
    if (currentTab && currentTab.url) {
      const domain = new URL(currentTab.url).hostname;
      await browser.runtime.sendMessage({
        action: 'addToWhitelist',
        domain: domain
      });
      
      whitelist.push(domain);
      loadWhitelist();
      alert(`${domain} adicionado à lista de sites confiáveis!`);
    }
  });
  
  // Abrir dashboard
  document.getElementById('openDashboardBtn').addEventListener('click', () => {
    browser.tabs.create({ url: 'http://localhost:3000' });
  });
  
  // Configurações
  document.getElementById('enabledToggle').addEventListener('change', (e) => {
    settings.enabled = e.target.checked;
    saveSettings();
  });
  
  document.getElementById('autoBlockToggle').addEventListener('change', (e) => {
    settings.autoBlock = e.target.checked;
    saveSettings();
  });
  
  document.getElementById('notificationsToggle').addEventListener('change', (e) => {
    settings.showNotifications = e.target.checked;
    saveSettings();
  });
  
  document.getElementById('sensitivitySelect').addEventListener('change', (e) => {
    settings.sensitivity = e.target.value;
    saveSettings();
  });
}

// Salvar configurações
async function saveSettings() {
  await browser.runtime.sendMessage({
    action: 'updateSettings',
    settings: settings
  });
}

// Remover da whitelist (global para ser chamada do HTML)
window.removeFromWhitelist = async function(domain) {
  await browser.runtime.sendMessage({
    action: 'removeFromWhitelist',
    domain: domain
  });
  
  whitelist = whitelist.filter(d => d !== domain);
  loadWhitelist();
};
