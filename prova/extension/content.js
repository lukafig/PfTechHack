// Content Script - Analisar links ao passar o mouse

// Criar tooltip
const tooltip = document.createElement('div');
tooltip.id = 'phishguard-tooltip';
tooltip.style.cssText = `
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 10px 15px;
  border-radius: 8px;
  font-size: 13px;
  font-family: Arial, sans-serif;
  z-index: 999999;
  display: none;
  max-width: 300px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
`;
document.body.appendChild(tooltip);

// Monitorar hover em links
document.addEventListener('mouseover', async (e) => {
  const link = e.target.closest('a');
  
  if (link && link.href) {
    const url = link.href;
    
    // Verificar se já temos resultado
    const response = await browser.runtime.sendMessage({
      action: 'checkURL',
      url: url
    });
    
    if (response.result) {
      showTooltip(e, response.result, url);
    }
  }
});

document.addEventListener('mouseout', (e) => {
  const link = e.target.closest('a');
  if (link) {
    hideTooltip();
  }
});

// Mostrar tooltip
function showTooltip(e, result, url) {
  const domain = new URL(url).hostname;
  
  let icon = '✓';
  let color = '#43e97b';
  let status = 'SEGURO';
  
  if (result.risk_score >= 60) {
    icon = '⚠️';
    color = '#E74C3C';
    status = 'PERIGOSO';
  } else if (result.risk_score >= 40) {
    icon = '⚠';
    color = '#FFD700';
    status = 'SUSPEITO';
  }
  
  tooltip.innerHTML = `
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
      <span style="font-size: 18px;">${icon}</span>
      <strong style="color: ${color};">${status}</strong>
    </div>
    <div style="font-size: 11px; opacity: 0.9;">
      ${domain}<br>
      Score de Risco: <strong>${result.risk_score}/100</strong>
    </div>
  `;
  
  tooltip.style.display = 'block';
  tooltip.style.left = `${e.clientX + 15}px`;
  tooltip.style.top = `${e.clientY + 15}px`;
}

// Ocultar tooltip
function hideTooltip() {
  tooltip.style.display = 'none';
}

// Mover tooltip com o mouse
document.addEventListener('mousemove', (e) => {
  if (tooltip.style.display === 'block') {
    tooltip.style.left = `${e.clientX + 15}px`;
    tooltip.style.top = `${e.clientY + 15}px`;
  }
});

console.log('PhishGuard Content Script loaded!');
