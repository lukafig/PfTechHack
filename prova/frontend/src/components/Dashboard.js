import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Dashboard({ apiUrl }) {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [historyRes, statsRes] = await Promise.all([
        axios.get(`${apiUrl}/api/history?limit=10`),
        axios.get(`${apiUrl}/api/stats`)
      ]);
      setHistory(historyRes.data.history);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };

  return (
    <div>
      <div className="card">
        <h2 className="card-title">Dashboard</h2>
        <p>Visão geral do sistema de detecção de phishing</p>
      </div>

      {stats && (
        <div className="card">
          <h3 className="card-title">Resumo</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{stats.total_analyzed}</h3>
              <p>Total de Análises</p>
            </div>
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
              <h3>{stats.safe_percentage}%</h3>
              <p>Taxa de Segurança</p>
            </div>
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)' }}>
              <h3>{stats.phishing_percentage}%</h3>
              <p>Taxa de Phishing</p>
            </div>
            <div className="stat-card" style={{ background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' }}>
              <h3>{stats.average_risk_score}</h3>
              <p>Score Médio</p>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <h3 className="card-title">🕐 Análises Recentes</h3>
        {history.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>
            Nenhuma análise realizada ainda
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>URL</th>
                  <th>Score</th>
                  <th>Status</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {history.map((entry) => (
                  <tr key={entry.id}>
                    <td style={{ maxWidth: '400px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {entry.url}
                    </td>
                    <td>
                      <strong style={{ color: entry.risk_score >= 60 ? '#E74C3C' : '#43e97b' }}>
                        {entry.risk_score}
                      </strong>
                    </td>
                    <td>
                      <span className={`status-badge ${entry.is_safe ? 'safe' : 'danger'}`}>
                        {entry.is_safe ? '✓ Segura' : '⚠ Suspeita'}
                      </span>
                    </td>
                    <td>{new Date(entry.timestamp).toLocaleString('pt-BR')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h3 className="card-title">🛡️ Recursos do Sistema</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>🔍 Análise Heurística</h4>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Verificação de domínios, SSL, WHOIS, DNS e características suspeitas
            </p>
          </div>
          <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>🤖 Machine Learning</h4>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Classificação inteligente usando Random Forest com múltiplas features
            </p>
          </div>
          <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>📄 Análise de Conteúdo</h4>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Detecção de formulários, scripts maliciosos e técnicas de manipulação
            </p>
          </div>
          <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
            <h4 style={{ color: '#667eea', marginBottom: '0.5rem' }}>🏢 Similaridade de Marcas</h4>
            <p style={{ fontSize: '0.9rem', color: '#666' }}>
              Detecção de domínios similares a marcas conhecidas usando Levenshtein
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
