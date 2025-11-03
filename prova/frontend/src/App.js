import React, { useState } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import URLScanner from './components/URLScanner';
import ResultsDisplay from './components/ResultsDisplay';
import HistoryView from './components/HistoryView';
import Statistics from './components/Statistics';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [activeTab, setActiveTab] = useState('scanner');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeURL = async (url) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/analyze`, { url });
      setAnalysisResult(response.data);
      setActiveTab('results');
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao analisar URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="container">
          <h1>GonePhishin'</h1>
          <p className="subtitle">Sistema de Detecção de Phishing</p>
        </div>
      </header>

      <nav className="navigation">
        <div className="nav-container">
          <button
            className={activeTab === 'scanner' ? 'active' : ''}
            onClick={() => setActiveTab('scanner')}
          >
            Analisar
          </button>
          <button
            className={activeTab === 'results' ? 'active' : ''}
            onClick={() => setActiveTab('results')}
            disabled={!analysisResult}
          >
            Resultados
          </button>
          <button
            className={activeTab === 'history' ? 'active' : ''}
            onClick={() => setActiveTab('history')}
          >
            Histórico
          </button>
          <button
            className={activeTab === 'stats' ? 'active' : ''}
            onClick={() => setActiveTab('stats')}
          >
            Estatísticas
          </button>
          <button
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
        </div>
      </nav>

      <main className="main-content">
        <div className="container">
          {activeTab === 'scanner' && (
            <URLScanner
              onAnalyze={analyzeURL}
              loading={loading}
              error={error}
            />
          )}

          {activeTab === 'results' && analysisResult && (
            <ResultsDisplay result={analysisResult} />
          )}

          {activeTab === 'history' && (
            <HistoryView apiUrl={API_URL} />
          )}

          {activeTab === 'stats' && (
            <Statistics apiUrl={API_URL} />
          )}

          {activeTab === 'dashboard' && (
            <Dashboard apiUrl={API_URL} />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>GonePhishin' - Sistema de Detecção de Phishing</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
