import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Statistics({ apiUrl }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${apiUrl}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div className="loading-spinner" style={{ width: '40px', height: '40px' }}></div>
        <p style={{ marginTop: '1rem' }}>Carregando estatísticas...</p>
      </div>
    );
  }

  if (!stats || stats.total_analyzed === 0) {
    return (
      <div className="card">
        <h2 className="card-title">Estatísticas</h2>
        <p style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>
          Nenhuma análise realizada ainda
        </p>
      </div>
    );
  }

  const pieData = [
    { name: 'URLs Seguras', value: stats.safe_urls, color: '#43e97b' },
    { name: 'URLs Suspeitas', value: stats.phishing_urls, color: '#E74C3C' }
  ];

  const classificationData = Object.entries(stats.classifications_distribution).map(([key, value]) => ({
    name: key,
    count: value
  }));

  return (
    <div>
      <div className="card">
        <h2 className="card-title">Estatísticas Gerais</h2>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>{stats.total_analyzed}</h3>
            <p>URLs Analisadas</p>
          </div>
          <div className="stat-card" style={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            <h3>{stats.safe_urls}</h3>
            <p>URLs Seguras</p>
          </div>
          <div className="stat-card" style={{ background: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)' }}>
            <h3>{stats.phishing_urls}</h3>
            <p>URLs Suspeitas</p>
          </div>
          <div className="stat-card" style={{ background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)' }}>
            <h3>{stats.average_risk_score}</h3>
            <p>Score Médio de Risco</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">Distribuição de URLs</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2 className="card-title">Distribuição por Classificação</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={classificationData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h2 className="card-title">Insights</h2>
        <div style={{ background: '#f8f9fa', padding: '1.5rem', borderRadius: '8px' }}>
          <ul style={{ lineHeight: '2' }}>
            <li>
              <strong>{stats.safe_percentage}%</strong> das URLs analisadas são seguras
            </li>
            <li>
              <strong>{stats.phishing_percentage}%</strong> das URLs analisadas são suspeitas de phishing
            </li>
            <li>
              O score médio de risco é <strong>{stats.average_risk_score}</strong> pontos
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Statistics;
