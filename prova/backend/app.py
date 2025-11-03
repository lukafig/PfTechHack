"""
Sistema de Detecção de Phishing - Backend API
Nota A - TecHacker
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from datetime import datetime
import os
from bs4 import BeautifulSoup

# Importar módulos de análise
from analyzers.url_analyzer import URLAnalyzer
from analyzers.ml_classifier import MLClassifier
from analyzers.content_analyzer import ContentAnalyzer
from analyzers.geolocation_analyzer import GeolocationAnalyzer
from analyzers.oauth_analyzer import OAuthAnalyzer
from analyzers.email_blacklist_analyzer import EmailBlacklistAnalyzer
from analyzers.screenshot_analyzer import ScreenshotAnalyzer
from database.history import URLHistory

# Configuração da aplicação
app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# Configurar diretório de screenshots
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'screenshots')
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar componentes
url_analyzer = URLAnalyzer()
ml_classifier = MLClassifier()
content_analyzer = ContentAnalyzer()
geolocation_analyzer = GeolocationAnalyzer()
oauth_analyzer = OAuthAnalyzer()
email_blacklist_analyzer = EmailBlacklistAnalyzer()
screenshot_analyzer = ScreenshotAnalyzer()
history = URLHistory()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/static/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Servir screenshots capturados"""
    return send_from_directory(SCREENSHOTS_DIR, filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    """
    Endpoint principal para análise de URL
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL não fornecida'}), 400
        
        logger.info(f"Analisando URL: {url}")
        
        # 1. Análises Heurísticas
        heuristic_results = url_analyzer.analyze(url)
        
        # 2. Análise de Conteúdo
        content_results = content_analyzer.analyze(url)
        
        # 3. Análise de Geolocalização
        geolocation_results = geolocation_analyzer.analyze(url)
        
        # 4. Análise de OAuth (detecção de páginas falsas)
        # Criar BeautifulSoup object do HTML
        html_content = content_results.get('html', '')
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            oauth_results = oauth_analyzer.analyze(soup, url)
        else:
            oauth_results = {
                'is_oauth_page': False,
                'is_legitimate': True,
                'provider': None,
                'risk_score': 0,
                'details': ['Não foi possível obter HTML para análise OAuth']
            }
        
        # 5. Análise de Blacklist de Email
        email_blacklist_results = email_blacklist_analyzer.analyze(url)
        
        # 6. Análise de Screenshot - COM TIMEOUT AGRESSIVO
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
        
        def run_screenshot():
            try:
                return screenshot_analyzer.analyze(url)
            except Exception as e:
                logger.error(f"Erro screenshot: {e}")
                return None
        
        screenshot_results = None
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_screenshot)
                screenshot_results = future.result(timeout=12)  # 12 segundos MAX
        except (FutureTimeoutError, Exception) as e:
            logger.warning(f"Screenshot timeout ou erro: {e}")
            screenshot_results = None
        
        if not screenshot_results:
            screenshot_results = {
                'screenshot_captured': False,
                'screenshot_path': None,
                'visual_hash': None,
                'is_clone': False,
                'cloned_brand': None,
                'similarity_score': 0,
                'risk_score': 0,
                'details': ['⚡ Screenshot timeout (>12s) - análise pulada'],
                'error': 'Timeout',
                'feature_available': False
            }
        
        # 7. Machine Learning Classification
        ml_results = ml_classifier.classify(url, heuristic_results, content_results)
        
        # 8. Calcular score final de risco (0-100)
        risk_score = calculate_risk_score(
            heuristic_results, 
            content_results, 
            ml_results,
            geolocation_results,
            oauth_results,
            email_blacklist_results,
            screenshot_results
        )
        
        # 5. Determinar classificação final
        classification = classify_url(risk_score)
        
        # Compilar resultado completo
        result = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'risk_score': risk_score,
            'classification': classification,
            'is_safe': risk_score < 40,
            'heuristic_analysis': heuristic_results,
            'content_analysis': content_results,
            'geolocation_analysis': geolocation_results,
            'oauth_analysis': oauth_results,
            'email_blacklist_analysis': email_blacklist_results,
            'screenshot_analysis': screenshot_results,
            'ml_prediction': ml_results,
            'recommendations': generate_recommendations(
                risk_score, 
                heuristic_results, 
                geolocation_results,
                oauth_results,
                email_blacklist_results,
                screenshot_results
            )
        }
        
        # Salvar no histórico
        history.add_entry(result)
        
        logger.info(f"Análise concluída: {classification} (Score: {risk_score})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obter histórico de URLs analisadas"""
    try:
        limit = request.args.get('limit', 50, type=int)
        entries = history.get_recent(limit)
        return jsonify({'history': entries})
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/export', methods=['GET'])
def export_history():
    """Exportar histórico em formato CSV"""
    try:
        csv_data = history.export_csv()
        return csv_data, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=phishing_history.csv'
        }
    except Exception as e:
        logger.error(f"Erro ao exportar histórico: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Obter estatísticas gerais"""
    try:
        stats = history.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/whitelist', methods=['GET', 'POST', 'DELETE'])
def manage_whitelist():
    """Gerenciar lista de sites confiáveis"""
    try:
        if request.method == 'GET':
            whitelist = url_analyzer.get_whitelist()
            return jsonify({'whitelist': whitelist})
        
        elif request.method == 'POST':
            data = request.get_json()
            domain = data.get('domain')
            url_analyzer.add_to_whitelist(domain)
            return jsonify({'success': True, 'message': f'Domínio {domain} adicionado à whitelist'})
        
        elif request.method == 'DELETE':
            data = request.get_json()
            domain = data.get('domain')
            url_analyzer.remove_from_whitelist(domain)
            return jsonify({'success': True, 'message': f'Domínio {domain} removido da whitelist'})
            
    except Exception as e:
        logger.error(f"Erro ao gerenciar whitelist: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_risk_score(heuristic, content, ml, geolocation, oauth, email_blacklist, screenshot):
    """
    Calcular score de risco combinado (0-100)
    Maior score = maior risco
    
    Inclui análises de:
    - Heurísticas (35%) - aumentado pois detecta domínios novos, SSL, etc
    - Conteúdo (15%)
    - Machine Learning (20%) - reduzido pois precisa treino
    - Geolocalização (10%)
    - OAuth falso (10%)
    - Email Blacklist (5%)
    - Screenshot (5%)
    """
    # Pesos para cada componente
    heuristic_weight = 0.35
    content_weight = 0.15
    ml_weight = 0.20
    geolocation_weight = 0.10
    oauth_weight = 0.10
    email_blacklist_weight = 0.05
    screenshot_weight = 0.05
    
    # Normalizar scores
    heuristic_score = heuristic.get('risk_score', 0)
    content_score = content.get('risk_score', 0)
    ml_score = ml.get('phishing_probability', 0) * 100
    geolocation_score = geolocation.get('risk_score', 0)
    oauth_score = oauth.get('risk_score', 0)
    email_blacklist_score = email_blacklist.get('risk_score', 0)
    screenshot_score = screenshot.get('risk_score', 0)
    
    # Calcular média ponderada
    final_score = (
        heuristic_score * heuristic_weight +
        content_score * content_weight +
        ml_score * ml_weight +
        geolocation_score * geolocation_weight +
        oauth_score * oauth_weight +
        email_blacklist_score * email_blacklist_weight +
        screenshot_score * screenshot_weight
    )
    
    # BÔNUS CRÍTICOS: indicadores de alto risco
    bonus = 0
    
    # Domínio muito novo (< 7 dias) = +30 pontos
    if heuristic.get('young_domain'):
        whois_info = heuristic.get('checks', {}).get('whois', {}).get('info', {})
        age_days = whois_info.get('age_days', 999)
        if age_days < 7:
            bonus += 30
            logger.warning(f"ALERTA: Domínio muito novo ({age_days} dias) - Adicionando +30 ao score")
        elif age_days < 30:
            bonus += 20
            logger.warning(f"ALERTA: Domínio novo ({age_days} dias) - Adicionando +20 ao score")
    
    # Problemas no SSL = +15 pontos
    if heuristic.get('ssl_issues'):
        bonus += 15
        logger.warning("ALERTA: Problemas no SSL detectados - Adicionando +15 ao score")
    
    # Domínio suspeito = +10 pontos
    if heuristic.get('suspicious_domain'):
        bonus += 10
        logger.warning("ALERTA: Domínio suspeito detectado - Adicionando +10 ao score")
    
    # NOVO: Logos de marcas detectadas (brand spoofing) = +25 pontos
    brand_logos = content.get('checks', {}).get('brand_logos', {})
    if brand_logos.get('brands_detected') and len(brand_logos.get('brands_detected', [])) > 0:
        brands = ', '.join(brand_logos.get('brands_detected', []))
        bonus += 25
        logger.warning(f"ALERTA CRÍTICO: Logos de marca detectadas ({brands}) - POSSÍVEL CLONE! Adicionando +25 ao score")
    
    # NOVO: Conteúdo com alto risco (>50) = +10 pontos adicional
    if content_score > 50:
        bonus += 10
        logger.warning(f"ALERTA: Conteúdo suspeito (score {content_score}) - Adicionando +10 ao score")
    
    # NOVO: Path suspeito (wp-content, admin, login com strings aleatórias) = +10 pontos
    url_lower = heuristic.get('url', '').lower()
    suspicious_paths = ['wp-content/', 'wp-admin/', 'wp-login', '/admin/', '/login/']
    has_random_string = any(len(part) > 20 and not part.endswith(('.html', '.php', '.jsp')) 
                           for part in url_lower.split('/'))
    if any(path in url_lower for path in suspicious_paths) and has_random_string:
        bonus += 10
        logger.warning("ALERTA: Path suspeito com string aleatória detectado - Adicionando +10 ao score")
    
    final_score = min(100, final_score + bonus)
    
    return round(final_score, 2)

def classify_url(risk_score):
    """Classificar URL baseado no score de risco"""
    if risk_score < 20:
        return 'SAFE'
    elif risk_score < 40:
        return 'LOW_RISK'
    elif risk_score < 60:
        return 'MEDIUM_RISK'
    elif risk_score < 80:
        return 'HIGH_RISK'
    else:
        return 'CRITICAL'

def generate_recommendations(risk_score, heuristic_results, geolocation_results, oauth_results, email_blacklist_results, screenshot_results):
    """Gerar recomendações baseadas na análise"""
    recommendations = []
    
    if risk_score < 40:
        recommendations.append("✓ Esta URL parece segura, mas sempre verifique a legitimidade antes de fornecer informações sensíveis.")
    else:
        recommendations.append("⚠ NÃO acesse esta URL ou forneça informações pessoais.")
        
        if heuristic_results.get('blacklisted'):
            recommendations.append("⚠ URL encontrada em listas de phishing conhecidas.")
        
        if heuristic_results.get('suspicious_domain'):
            recommendations.append("⚠ Domínio possui características suspeitas.")
        
        if heuristic_results.get('ssl_issues'):
            recommendations.append("⚠ Problemas detectados no certificado SSL.")
        
        if heuristic_results.get('young_domain'):
            recommendations.append("⚠ Domínio foi registrado recentemente.")
        
        # Recomendações de geolocalização
        if geolocation_results.get('high_risk_country'):
            recommendations.append(f"⚠ Servidor hospedado em país de alto risco: {geolocation_results.get('country', 'Desconhecido')}.")
        
        if geolocation_results.get('suspicious_asn'):
            recommendations.append("⚠ ASN do servidor associado a atividades suspeitas.")
        
        if geolocation_results.get('vps_hosting'):
            recommendations.append("⚠ Servidor hospedado em provedor VPS frequentemente usado para phishing.")
        
        # Recomendações de OAuth
        if oauth_results.get('is_oauth_page') and oauth_results.get('is_fake'):
            recommendations.append("⚠ PÁGINA FALSA DE LOGIN DETECTADA! Não forneça suas credenciais.")
            if oauth_results.get('fake_provider'):
                recommendations.append(f"⚠ Tentativa de imitar página de login do {oauth_results.get('fake_provider')}.")
        
        if oauth_results.get('excessive_permissions'):
            recommendations.append("⚠ Página OAuth solicita permissões excessivas e suspeitas.")
        
        # Recomendações de Email Blacklist
        if email_blacklist_results.get('blacklisted'):
            num_lists = email_blacklist_results.get('blacklisted_count', 0)
            recommendations.append(f"⚠ Servidor encontrado em {num_lists} lista(s) de spam/phishing.")
            
            reputation = email_blacklist_results.get('reputation', '')
            if reputation == 'very_bad':
                recommendations.append("⚠ REPUTAÇÃO CRÍTICA: Servidor altamente suspeito.")
            elif reputation == 'bad':
                recommendations.append("⚠ Servidor com reputação ruim em múltiplas listas.")
        
        # Recomendações de Screenshot
        if screenshot_results.get('is_clone'):
            brand = screenshot_results.get('cloned_brand', 'marca conhecida')
            similarity = screenshot_results.get('similarity_score', 0)
            recommendations.append(f"🚨 CLONAGEM VISUAL DETECTADA: Página imita {brand.upper()} ({similarity:.0f}% similar)!")
            recommendations.append("⚠ PERIGO CRÍTICO: Tentativa de roubo de credenciais por clonagem visual.")
        elif screenshot_results.get('cloned_brand') and screenshot_results.get('similarity_score', 0) > 50:
            brand = screenshot_results.get('cloned_brand')
            recommendations.append(f"⚠ Página visualmente similar ao {brand.upper()}. Verifique cuidadosamente a URL.")
    
    return recommendations

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
