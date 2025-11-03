import React, { useState } from 'react';

function URLScanner({ onAnalyze, loading, error }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (url.trim()) {
      onAnalyze(url.trim());
    }
  };

  const exampleUrls = [
    'https://www.google.com',
    'http://suspicious-paypal-login.com',
    'https://g00gle-verify.tk'
  ];

  return (
    <div className="card url-scanner">
      <h2 className="card-title">Analisar URL</h2>
      <p>Digite a URL para verificar se há indícios de phishing</p>

      <form onSubmit={handleSubmit}>
        <div className="url-input-group">
          <input
            type="text"
            className="url-input"
            placeholder="https://exemplo.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !url.trim()}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span> Analisando...
              </>
            ) : (
              'Verificar'
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <p><strong>URLs de Teste:</strong></p>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          {exampleUrls.map((exampleUrl, index) => (
            <button
              key={index}
              onClick={() => setUrl(exampleUrl)}
              style={{
                padding: '0.5rem 1rem',
                background: '#f0f0f0',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              {exampleUrl}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '3rem', textAlign: 'left', background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
        <h3 style={{ color: '#667eea', marginBottom: '1rem' }}>Funcionalidades</h3>
        <ul style={{ lineHeight: '1.8' }}>
          <li>Verificação em bases de dados de phishing (PhishTank, OpenPhish)</li>
          <li>Análise heurística avançada de domínios</li>
          <li>Verificação de certificados SSL</li>
          <li>Análise WHOIS (idade do domínio)</li>
          <li>Detecção de similaridade com marcas conhecidas (Levenshtein)</li>
          <li>Análise de conteúdo e formulários suspeitos</li>
          <li>Classificação com Machine Learning</li>
          <li>Score de risco de 0 a 100</li>
        </ul>
      </div>
    </div>
  );
}

export default URLScanner;
