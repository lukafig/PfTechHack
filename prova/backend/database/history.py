"""
Gerenciamento de Histórico de URLs Analisadas
"""

import json
import os
from datetime import datetime
import csv
from io import StringIO

class URLHistory:
    def __init__(self, db_file='data/history.json'):
        self.db_file = db_file
        self.history = self.load_history()
    
    def load_history(self):
        """Carregar histórico do arquivo"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Salvar histórico no arquivo"""
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_entry(self, result):
        """Adicionar nova entrada ao histórico"""
        entry = {
            'id': len(self.history) + 1,
            'url': result['url'],
            'timestamp': result['timestamp'],
            'risk_score': result['risk_score'],
            'classification': result['classification'],
            'is_safe': result['is_safe']
        }
        
        self.history.insert(0, entry)  # Adicionar no início
        
        # Limitar tamanho do histórico
        if len(self.history) > 1000:
            self.history = self.history[:1000]
        
        self.save_history()
    
    def get_recent(self, limit=50):
        """Obter entradas recentes"""
        return self.history[:limit]
    
    def export_csv(self):
        """Exportar histórico em formato CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['ID', 'URL', 'Data/Hora', 'Score de Risco', 'Classificação', 'Seguro'])
        
        # Dados
        for entry in self.history:
            writer.writerow([
                entry['id'],
                entry['url'],
                entry['timestamp'],
                entry['risk_score'],
                entry['classification'],
                'Sim' if entry['is_safe'] else 'Não'
            ])
        
        return output.getvalue()
    
    def get_statistics(self):
        """Calcular estatísticas do histórico"""
        if not self.history:
            return {
                'total_analyzed': 0,
                'safe_urls': 0,
                'phishing_urls': 0,
                'average_risk_score': 0,
                'classifications_distribution': {}
            }
        
        total = len(self.history)
        safe = sum(1 for entry in self.history if entry['is_safe'])
        phishing = total - safe
        
        avg_risk = sum(entry['risk_score'] for entry in self.history) / total
        
        # Distribuição por classificação
        classifications = {}
        for entry in self.history:
            cls = entry['classification']
            classifications[cls] = classifications.get(cls, 0) + 1
        
        return {
            'total_analyzed': total,
            'safe_urls': safe,
            'phishing_urls': phishing,
            'average_risk_score': round(avg_risk, 2),
            'classifications_distribution': classifications,
            'safe_percentage': round((safe / total) * 100, 2),
            'phishing_percentage': round((phishing / total) * 100, 2)
        }
