import React, { useState } from 'react';

function ResultsDisplay({ result }) {
  const [showDetails, setShowDetails] = useState(false);
  const [expandedAnalyzers, setExpandedAnalyzers] = useState({});

  const toggleAnalyzer = (analyzer) => {
    setExpandedAnalyzers(prev => ({
      ...prev,
      [analyzer]: !prev[analyzer]
    }));
  };

  const getRiskLevel = (score) => {
    if (score < 20) return { level: 'safe', label: 'SEGURA', color: '#43e97b' };
    if (score < 40) return { level: 'low', label: 'BAIXO RISCO', color: '#90EE90' };
    if (score < 60) return { level: 'medium', label: 'MÉDIO RISCO', color: '#FFD700' };
    if (score < 80) return { level: 'high', label: 'ALTO RISCO', color: '#FF6B6B' };
    return { level: 'critical', label: 'CRÍTICO', color: '#E74C3C' };
  };

  const risk = getRiskLevel(result.risk_score);

  // Função para renderizar analyzer individual
  const renderAnalyzer = (name, data, icon) => {
    if (!data) return null;
    
    const isExpanded = expandedAnalyzers[name];
    const riskScore = data.risk_score || 0;
    const details = data.details || [];
    const screenshotPath = data.screenshot_path;
    
    return (
      <div key={name} style={{
        border: '1px solid #e0e0e0',
        borderRadius: '8px',
        marginBottom: '0.5rem',
        overflow: 'hidden'
      }}>
        <div
          onClick={() => toggleAnalyzer(name)}
          style={{
            padding: '1rem',
            background: '#f8f9fa',
            cursor: 'pointer',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = '#e9ecef'}
          onMouseLeave={(e) => e.currentTarget.style.background = '#f8f9fa'}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.5rem' }}>{icon}</span>
            <div>
              <div style={{ fontWeight: 'bold', color: '#333' }}>{name}</div>
              <div style={{ fontSize: '0.85rem', color: '#666' }}>
                Risk Score: <span style={{ fontWeight: 'bold', color: riskScore > 50 ? '#E74C3C' : '#43e97b' }}>{riskScore}</span>
              </div>
            </div>
          </div>
          <span style={{ 
            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.3s',
            fontSize: '1.2rem'
          }}>
            ▼
          </span>
        </div>
        
        {isExpanded && (
          <div style={{
            padding: '1rem',
            background: 'white',
            borderTop: '1px solid #e0e0e0',
            animation: 'slideDown 0.3s ease-out'
          }}>
            {/* Mostrar screenshot se disponível */}
            {screenshotPath && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ color: '#667eea', display: 'block', marginBottom: '0.5rem' }}>
                  📸 Screenshot Capturado:
                </strong>
                <div style={{ 
                  border: '2px solid #667eea',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                  <img 
                    src={`http://localhost:5000${screenshotPath}`}
                    alt="Screenshot da página analisada"
                    style={{ 
                      width: '100%',
                      height: 'auto',
                      display: 'block'
                    }}
                  />
                </div>
              </div>
            )}
            
            {details.length > 0 && (
              <div style={{ marginBottom: '1rem' }}>
                <strong style={{ color: '#667eea', display: 'block', marginBottom: '0.5rem' }}>
                  Detalhes da Análise:
                </strong>
                <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                  {details.map((detail, idx) => (
                    <li key={idx} style={{ marginBottom: '0.25rem', fontSize: '0.9rem' }}>
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Dados específicos do analyzer */}
            <div style={{ 
              background: '#f8f9fa', 
              padding: '0.75rem', 
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontFamily: 'monospace'
            }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div>
      <div className="card">
        <h2 className="card-title">🐟 Análise da Captura</h2>
        
        <div className="risk-score-container">
          <div className={`risk-score-circle ${risk.level}`}>
            <div>{result.risk_score}</div>
            <div style={{ fontSize: '1rem', fontWeight: 'normal' }}>/ 100</div>
          </div>
          <div className="classification-badge" style={{ background: risk.color, color: 'white' }}>
            {risk.label}
          </div>
          <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#666' }}>
            URL: <strong>{result.url}</strong>
          </p>
          <p style={{ fontSize: '0.85rem', color: '#999' }}>
            Analisado em: {new Date(result.timestamp).toLocaleString('pt-BR')}
          </p>
        </div>
        
        {/* Botão para ver detalhes dos analyzers */}
        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              padding: '0.75rem 1.5rem',
              background: '#4a90e2',
              color: 'white',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            <span>{showDetails ? 'Ocultar' : 'Ver'} Detalhes da Análise</span>
          </button>
        </div>
      </div>

      {/* Detalhes dos Analyzers */}
      {showDetails && (
        <div className="card" style={{ 
          borderTop: '3px solid #4a90e2'
        }}>
          <h3 className="card-title">
            <span>Análises Realizadas</span>
          </h3>
          <p style={{ color: '#666', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Resultados detalhados de cada módulo de análise:
          </p>

          {/* Renderizar cada analyzer */}
          {renderAnalyzer('Análise Heurística', result.heuristic_analysis, '')}
          {renderAnalyzer('Análise de Conteúdo', result.content_analysis, '')}
          {renderAnalyzer('Machine Learning', result.ml_prediction, '')}
          {renderAnalyzer('Geolocalização IP', result.geolocation_analysis, '')}
          {renderAnalyzer('OAuth Detector', result.oauth_analysis, '')}
          {renderAnalyzer('Email Blacklist', result.email_blacklist_analysis, '')}
          {renderAnalyzer('Screenshot Analysis', result.screenshot_analysis, '')}
        </div>
      )}

      {/* Recomendações */}
      {result.recommendations && result.recommendations.length > 0 && (
        <div className="card">
          <div className="recommendations">
            <h3>Recomendações</h3>
            <ul>
              {result.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Machine Learning Prediction */}
      {result.ml_prediction && (
        <div className="card">
          <h3 className="card-title">Predição de Machine Learning</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', margin: '1rem 0' }}>
            <div style={{ background: '#f8f9fa', padding: '1rem', borderRadius: '8px' }}>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>Probabilidade de Phishing</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: risk.color }}>
                {(result.ml_prediction.phishing_probability * 100).toFixed(1)}%
              </p>
            </div>
            <div style={{ background: '#f8f9fa', padding: '1rem', borderRadius: '8px' }}>
              <p style={{ color: '#666', fontSize: '0.9rem' }}>Confiança</p>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                {(result.ml_prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {result.ml_prediction.top_contributing_features && (
            <div style={{ marginTop: '1.5rem' }}>
              <h4 style={{ color: '#667eea', marginBottom: '1rem' }}>Features Mais Importantes:</h4>
              {result.ml_prediction.top_contributing_features.map((feature, index) => (
                <div key={index} style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                    <span>{feature.feature}</span>
                    <span>{(feature.importance * 100).toFixed(1)}%</span>
                  </div>
                  <div style={{ background: '#e0e0e0', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                    <div
                      style={{
                        background: '#667eea',
                        width: `${feature.importance * 100}%`,
                        height: '100%',
                        borderRadius: '4px'
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Análise Heurística */}
      {result.heuristic_analysis && result.heuristic_analysis.checks && (
        <div className="card">
          <h3 className="card-title">Análise Heurística</h3>
          <div className="details-grid">
            {/* Blacklist Check */}
            {result.heuristic_analysis.checks.blacklist && (
              <div className="detail-card">
                <h3>🚫 Listas Negras</h3>
                {result.heuristic_analysis.checks.blacklist.found ? (
                  <div>
                    <p style={{ color: '#E74C3C', fontWeight: 'bold' }}>URL encontrada em listas de phishing!</p>
                    <p>Fontes: {result.heuristic_analysis.checks.blacklist.sources.join(', ')}</p>
                  </div>
                ) : (
                  <p style={{ color: '#43e97b' }}>Não encontrada em listas de phishing</p>
                )}
              </div>
            )}

            {/* Domain Analysis */}
            {result.heuristic_analysis.checks.domain && (
              <div className="detail-card">
                <h3>🌐 Análise de Domínio</h3>
                {result.heuristic_analysis.checks.domain.issues.length > 0 ? (
                  <ul>
                    {result.heuristic_analysis.checks.domain.issues.map((issue, index) => (
                      <li key={index} style={{ color: '#E74C3C' }}>{issue}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: '#43e97b' }}>Sem problemas detectados</p>
                )}
              </div>
            )}

            {/* Brand Similarity */}
            {result.heuristic_analysis.checks.brand_similarity && result.heuristic_analysis.checks.brand_similarity.similar_brands.length > 0 && (
              <div className="detail-card">
                <h3>🏢 Similaridade com Marcas</h3>
                {result.heuristic_analysis.checks.brand_similarity.similar_brands.map((brand, index) => (
                  <div key={index} style={{ marginBottom: '0.5rem' }}>
                    <p style={{ color: '#E74C3C' }}>
                      {brand.similarity}% similar a "{brand.brand}"
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* WHOIS */}
            {result.heuristic_analysis.checks.whois && result.heuristic_analysis.checks.whois.info && (
              <div className="detail-card">
                <h3>📋 Informações WHOIS</h3>
                {result.heuristic_analysis.checks.whois.info.age_days !== undefined && (
                  <p>Idade: {result.heuristic_analysis.checks.whois.info.age_days} dias</p>
                )}
                {result.heuristic_analysis.checks.whois.info.creation_date && (
                  <p>Criado em: {new Date(result.heuristic_analysis.checks.whois.info.creation_date).toLocaleDateString('pt-BR')}</p>
                )}
                {result.heuristic_analysis.checks.whois.young_domain && (
                  <p style={{ color: '#E74C3C' }}>Domínio recém-criado</p>
                )}
              </div>
            )}

            {/* SSL */}
            {result.heuristic_analysis.checks.ssl && (
              <div className="detail-card">
                <h3>🔒 Certificado SSL</h3>
                {result.heuristic_analysis.checks.ssl.has_issues ? (
                  <p style={{ color: '#E74C3C' }}>Problemas detectados no SSL</p>
                ) : (
                  <p style={{ color: '#43e97b' }}>Certificado SSL válido</p>
                )}
                {result.heuristic_analysis.checks.ssl.details && result.heuristic_analysis.checks.ssl.details.expires_in_days && (
                  <p>Expira em: {result.heuristic_analysis.checks.ssl.details.expires_in_days} dias</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Análise de Conteúdo */}
      {result.content_analysis && result.content_analysis.checks && (
        <div className="card">
          <h3 className="card-title">📄 Análise de Conteúdo</h3>
          <div className="details-grid">
            {/* Login Forms */}
            {result.content_analysis.checks.login_forms && result.content_analysis.checks.login_forms.found && (
              <div className="detail-card">
                <h3>🔑 Formulários de Login</h3>
                <p style={{ color: '#FFA500' }}>{result.content_analysis.checks.login_forms.count} formulário(s) de login detectado(s)</p>
              </div>
            )}

            {/* Sensitive Info */}
            {result.content_analysis.checks.sensitive_info && result.content_analysis.checks.sensitive_info.requests_found.length > 0 && (
              <div className="detail-card">
                <h3>🔐 Informações Sensíveis</h3>
                <p style={{ color: '#E74C3C' }}>Solicitações de informações sensíveis:</p>
                <ul>
                  {result.content_analysis.checks.sensitive_info.requests_found.map((info, index) => (
                    <li key={index}>{info}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Brand Logos */}
            {result.content_analysis.checks.brand_logos && result.content_analysis.checks.brand_logos.brands_detected.length > 0 && (
              <div className="detail-card">
                <h3>🎨 Logos de Marcas</h3>
                <p style={{ color: '#E74C3C' }}>Logos detectadas que não correspondem ao domínio:</p>
                <ul>
                  {result.content_analysis.checks.brand_logos.brands_detected.map((brand, index) => (
                    <li key={index}>{brand}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Manipulation Techniques */}
            {result.content_analysis.checks.manipulation && result.content_analysis.checks.manipulation.techniques_found.length > 0 && (
              <div className="detail-card">
                <h3>🎭 Técnicas de Manipulação</h3>
                <ul>
                  {result.content_analysis.checks.manipulation.techniques_found.map((technique, index) => (
                    <li key={index} style={{ color: '#E74C3C' }}>{technique}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResultsDisplay;
