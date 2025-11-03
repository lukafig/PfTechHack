import React, { useState, useEffect } from 'react';
import axios from 'axios';

function HistoryView({ apiUrl }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/history`);
      setHistory(response.data.history);
    } catch (error) {
      console.error('Erro ao carregar histórico:', error);
    } finally {
      setLoading(false);
    }
  };

  const exportHistory = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/history/export`);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'phishing_history.csv';
      a.click();
    } catch (error) {
      console.error('Erro ao exportar histórico:', error);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="loading-spinner" style={{ width: '40px', height: '40px' }}></div>
        <p style={{ marginTop: '1rem' }}>Carregando histórico...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 className="card-title">📜 Histórico de Análises</h2>
        <button onClick={exportHistory} className="btn-primary">
          📥 Exportar CSV
        </button>
      </div>

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
                <th>Data/Hora</th>
                <th>Score</th>
                <th>Classificação</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {history.map((entry) => (
                <tr key={entry.id}>
                  <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {entry.url}
                  </td>
                  <td>{new Date(entry.timestamp).toLocaleString('pt-BR')}</td>
                  <td>
                    <strong style={{ color: entry.risk_score >= 60 ? '#E74C3C' : '#43e97b' }}>
                      {entry.risk_score}
                    </strong>
                  </td>
                  <td>{entry.classification}</td>
                  <td>
                    <span className={`status-badge ${entry.is_safe ? 'safe' : 'danger'}`}>
                      {entry.is_safe ? 'Segura' : 'Suspeita'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default HistoryView;
