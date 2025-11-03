// Background Script - Monitoramento em tempo real
const API_URL = 'http://localhost:5000';
const CACHE_DURATION = 3600000; // 1 hora

// Configurações
let settings = {
  enabled: true,
  sensitivity: 'medium', // low, medium, high
  autoBlock: false,
  showNotifications: true
};

// Cache de URLs analisadas
let urlCache = {};

// Whitelist do usuário
let userWhitelist = [];

// Carregar configurações e whitelist
browser.storage.local.get(['settings', 'whitelist']).then((data) => {
  if (data.settings) settings = data.settings;
  if (data.whitelist) userWhitelist = data.whitelist;
});

// Monitorar todas as requisições
browser.webRequest.onBeforeRequest.addListener(
  async (details) => {
    if (!settings.enabled) return {};
    
    // Ignorar requisições de recursos
    if (details.type !== 'main_frame') return {};
    
    const url = details.url;
    const domain = new URL(url).hostname;
    
    // Verificar whitelist
    if (isWhitelisted(domain)) {
      return {};
    }
    
    // Verificar cache
    const cached = getCachedResult(url);
    if (cached) {
      if (cached.is_safe) {
        return {};
      } else {
        return handleUnsafeURL(url, cached, details.tabId);
      }
    }
    
    // Análise rápida em background
    analyzeURLAsync(url, details.tabId);
    
    return {};
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

// Analisar URL de forma assíncrona
async function analyzeURLAsync(url, tabId) {
  try {
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      console.error('Erro na API:', response.statusText);
      return;
    }
    
    const result = await response.json();
    
    // Adicionar ao cache
    cacheResult(url, result);
    
    // Verificar se é perigoso
    if (!result.is_safe) {
      // Mostrar notificação
      if (settings.showNotifications) {
        showNotification(url, result);
      }
      
      // Atualizar badge
      updateBadge(tabId, result.risk_score);
      
      // Bloquear se auto-block estiver ativado e risco for alto
      if (settings.autoBlock && result.risk_score >= getBlockThreshold()) {
        blockTab(tabId, url, result);
      }
    }
    
  } catch (error) {
    console.error('Erro ao analisar URL:', error);
  }
}

// Lidar com URLs não seguras
function handleUnsafeURL(url, result, tabId) {
  if (settings.autoBlock && result.risk_score >= getBlockThreshold()) {
    // Redirecionar para página de aviso
    return {
      redirectUrl: browser.runtime.getURL(`warning.html?url=${encodeURIComponent(url)}&score=${result.risk_score}`)
    };
  }
  
  return {};
}

// Gerenciar cache
function getCachedResult(url) {
  const cached = urlCache[url];
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.result;
  }
  return null;
}

function cacheResult(url, result) {
  urlCache[url] = {
    result,
    timestamp: Date.now()
  };
}

// Verificar whitelist
function isWhitelisted(domain) {
  return userWhitelist.some(whitelisted => 
    domain === whitelisted || domain.endsWith('.' + whitelisted)
  );
}

// Obter threshold de bloqueio baseado na sensibilidade
function getBlockThreshold() {
  switch (settings.sensitivity) {
    case 'low': return 80;
    case 'medium': return 60;
    case 'high': return 40;
    default: return 60;
  }
}

// Mostrar notificação
function showNotification(url, result) {
  const domain = new URL(url).hostname;
  
  browser.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon-96.png',
    title: '⚠️ PhishGuard - Site Suspeito Detectado',
    message: `O site ${domain} pode ser perigoso!\nScore de Risco: ${result.risk_score}/100\n\nTenha cuidado ao fornecer informações pessoais.`
  });
}

// Atualizar badge
function updateBadge(tabId, riskScore) {
  let color = '#43e97b'; // Verde
  let text = '✓';
  
  if (riskScore >= 80) {
    color = '#E74C3C'; // Vermelho
    text = '!!!';
  } else if (riskScore >= 60) {
    color = '#FF6B6B'; // Laranja escuro
    text = '!!';
  } else if (riskScore >= 40) {
    color = '#FFD700'; // Amarelo
    text = '!';
  }
  
  browser.browserAction.setBadgeText({ text, tabId });
  browser.browserAction.setBadgeBackgroundColor({ color, tabId });
}

// Bloquear tab
function blockTab(tabId, url, result) {
  browser.tabs.update(tabId, {
    url: browser.runtime.getURL(`warning.html?url=${encodeURIComponent(url)}&score=${result.risk_score}`)
  });
}

// Listener para mensagens do popup e content script
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'getSettings') {
    sendResponse({ settings, whitelist: userWhitelist });
  } else if (message.action === 'updateSettings') {
    settings = message.settings;
    browser.storage.local.set({ settings });
    sendResponse({ success: true });
  } else if (message.action === 'addToWhitelist') {
    if (!userWhitelist.includes(message.domain)) {
      userWhitelist.push(message.domain);
      browser.storage.local.set({ whitelist: userWhitelist });
    }
    sendResponse({ success: true });
  } else if (message.action === 'removeFromWhitelist') {
    userWhitelist = userWhitelist.filter(d => d !== message.domain);
    browser.storage.local.set({ whitelist: userWhitelist });
    sendResponse({ success: true });
  } else if (message.action === 'analyzeCurrentTab') {
    browser.tabs.query({ active: true, currentWindow: true }).then(tabs => {
      if (tabs[0]) {
        analyzeURLAsync(tabs[0].url, tabs[0].id);
      }
    });
    sendResponse({ success: true });
  } else if (message.action === 'checkURL') {
    // Verificar URL específica
    const cached = getCachedResult(message.url);
    if (cached) {
      sendResponse({ result: cached });
    } else {
      sendResponse({ result: null });
    }
  }
  
  return true; // Manter canal aberto para resposta assíncrona
});

// Limpar cache periodicamente
setInterval(() => {
  const now = Date.now();
  for (const url in urlCache) {
    if (now - urlCache[url].timestamp >= CACHE_DURATION) {
      delete urlCache[url];
    }
  }
}, 600000); // 10 minutos

console.log('PhishGuard Extension loaded!');
