"""
Analisador de Conteúdo de Páginas Web
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import hashlib

class ContentAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze(self, url):
        """Executar análise completa de conteúdo"""
        results = {
            'risk_score': 0,
            'checks': {}
        }
        
        try:
            # Buscar conteúdo da página
            response = self.session.get(url, timeout=10, allow_redirects=True)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. Detectar formulários de login
            login_forms = self.detect_login_forms(soup)
            results['checks']['login_forms'] = login_forms
            results['risk_score'] += login_forms['risk_score']
            
            # 2. Verificar solicitações de informações sensíveis
            sensitive_info = self.check_sensitive_info_requests(soup)
            results['checks']['sensitive_info'] = sensitive_info
            results['risk_score'] += sensitive_info['risk_score']
            
            # 3. Detectar logos e imagens de marcas
            brand_detection = self.detect_brand_logos(soup, url)
            results['checks']['brand_logos'] = brand_detection
            results['risk_score'] += brand_detection['risk_score']
            
            # 4. Análise de scripts maliciosos
            script_analysis = self.analyze_scripts(soup)
            results['checks']['scripts'] = script_analysis
            results['risk_score'] += script_analysis['risk_score']
            
            # 5. Detectar técnicas de manipulação
            manipulation = self.detect_manipulation_techniques(soup, html_content)
            results['checks']['manipulation'] = manipulation
            results['risk_score'] += manipulation['risk_score']
            
            # 6. Verificar práticas SEO maliciosas
            seo_analysis = self.analyze_seo_practices(soup)
            results['checks']['seo'] = seo_analysis
            results['risk_score'] += seo_analysis['risk_score']
            
            # 7. Detectar temporizadores de urgência
            urgency_timers = self.detect_urgency_timers(soup, html_content)
            results['checks']['urgency_timers'] = urgency_timers
            results['risk_score'] += urgency_timers['risk_score']
            
            # 8. Análise de OAuth suspeito
            oauth_analysis = self.analyze_oauth(soup)
            results['checks']['oauth'] = oauth_analysis
            results['risk_score'] += oauth_analysis['risk_score']
            
        except requests.RequestException as e:
            results['error'] = f'Erro ao acessar URL: {str(e)}'
            results['risk_score'] = 0
        except Exception as e:
            results['error'] = f'Erro na análise: {str(e)}'
        
        # Normalizar score
        results['risk_score'] = min(100, results['risk_score'])
        
        return results
    
    def detect_login_forms(self, soup):
        """Detectar formulários de login"""
        result = {
            'risk_score': 0,
            'found': False,
            'count': 0,
            'details': []
        }
        
        forms = soup.find_all('form')
        
        for form in forms:
            # Procurar campos de senha
            password_fields = form.find_all('input', {'type': 'password'})
            
            if password_fields:
                result['found'] = True
                result['count'] += 1
                
                # Verificar campos sensíveis
                form_fields = [input_tag.get('name', '') for input_tag in form.find_all('input')]
                
                sensitive_fields = []
                for field in form_fields:
                    field_lower = field.lower()
                    if any(keyword in field_lower for keyword in ['password', 'pass', 'pwd', 'senha']):
                        sensitive_fields.append(field)
                    if any(keyword in field_lower for keyword in ['email', 'username', 'login', 'user']):
                        sensitive_fields.append(field)
                    if any(keyword in field_lower for keyword in ['credit', 'card', 'cvv', 'ssn', 'cpf']):
                        sensitive_fields.append(field)
                        result['risk_score'] += 20  # Dados financeiros
                
                result['details'].append({
                    'sensitive_fields': sensitive_fields,
                    'action': form.get('action', ''),
                    'method': form.get('method', 'GET')
                })
                
                # Formulários de login aumentam risco
                result['risk_score'] += 15
        
        return result
    
    def check_sensitive_info_requests(self, soup):
        """Verificar solicitações de informações sensíveis"""
        result = {
            'risk_score': 0,
            'requests_found': []
        }
        
        # Palavras-chave sensíveis
        sensitive_keywords = [
            'credit card', 'cartão de crédito', 'cvv', 'security code',
            'social security', 'ssn', 'cpf', 'tax id',
            'bank account', 'conta bancária', 'routing number',
            'passport', 'passaporte', 'driver license',
            'mother maiden name', 'nome de solteira'
        ]
        
        text_content = soup.get_text().lower()
        
        for keyword in sensitive_keywords:
            if keyword in text_content:
                result['requests_found'].append(keyword)
                result['risk_score'] += 10
        
        # Limitar score máximo
        result['risk_score'] = min(50, result['risk_score'])
        
        return result
    
    def detect_brand_logos(self, soup, url):
        """Detectar logos de marcas conhecidas"""
        result = {
            'risk_score': 0,
            'brands_detected': []
        }
        
        # Marcas para verificar
        brands = ['paypal', 'amazon', 'google', 'microsoft', 'apple', 'facebook', 
                  'netflix', 'ebay', 'bank', 'banco', 'bradesco', 'itau', 'santander']
        
        # Verificar imagens
        images = soup.find_all('img')
        
        domain = urlparse(url).netloc.lower()
        
        for img in images:
            src = img.get('src', '').lower()
            alt = img.get('alt', '').lower()
            
            for brand in brands:
                if brand in src or brand in alt:
                    # Se detectar logo de marca mas domínio não corresponde
                    if brand not in domain:
                        result['brands_detected'].append(brand)
                        result['risk_score'] += 20
        
        # Limitar score
        result['risk_score'] = min(60, result['risk_score'])
        
        return result
    
    def analyze_scripts(self, soup):
        """Analisar scripts para detectar código malicioso"""
        result = {
            'risk_score': 0,
            'suspicious_patterns': []
        }
        
        scripts = soup.find_all('script')
        
        # Padrões suspeitos
        suspicious_patterns = [
            (r'eval\s*\(', 'eval() - possível ofuscação'),
            (r'document\.write\s*\(', 'document.write() - possível injeção'),
            (r'fromCharCode', 'fromCharCode - possível ofuscação'),
            (r'unescape\s*\(', 'unescape() - possível ofuscação'),
            (r'String\.fromCharCode', 'String.fromCharCode - ofuscação'),
            (r'window\.location\s*=', 'Redirecionamento via JavaScript'),
            (r'document\.cookie', 'Acesso a cookies'),
            (r'addEventListener\s*\(\s*["\']contextmenu', 'Bloqueio de menu de contexto'),
            (r'oncontextmenu\s*=', 'Bloqueio de clique direito')
        ]
        
        for script in scripts:
            script_content = script.string or ''
            
            for pattern, description in suspicious_patterns:
                if re.search(pattern, script_content, re.IGNORECASE):
                    result['suspicious_patterns'].append(description)
                    result['risk_score'] += 10
        
        # Limitar score
        result['risk_score'] = min(50, result['risk_score'])
        
        return result
    
    def detect_manipulation_techniques(self, soup, html_content):
        """Detectar técnicas de manipulação"""
        result = {
            'risk_score': 0,
            'techniques_found': []
        }
        
        # 1. Bloqueio de clique direito
        if 'oncontextmenu' in html_content.lower():
            result['techniques_found'].append('Bloqueio de clique direito')
            result['risk_score'] += 15
        
        # 2. Ocultar URL real
        if 'window.location' in html_content and 'href' in html_content:
            result['techniques_found'].append('Possível ocultação de URL')
            result['risk_score'] += 10
        
        # 3. Iframes ocultos
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            style = iframe.get('style', '')
            if 'display:none' in style or 'visibility:hidden' in style:
                result['techniques_found'].append('Iframe oculto')
                result['risk_score'] += 20
        
        # 4. Popups automáticos
        if 'window.open' in html_content:
            result['techniques_found'].append('Popup automático')
            result['risk_score'] += 10
        
        return result
    
    def analyze_seo_practices(self, soup):
        """Analisar práticas SEO maliciosas"""
        result = {
            'risk_score': 0,
            'issues': []
        }
        
        # Keyword stuffing
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '')
            if len(keywords.split(',')) > 50:
                result['issues'].append('Keyword stuffing detectado')
                result['risk_score'] += 10
        
        # Cloaking (texto oculto)
        hidden_elements = soup.find_all(style=re.compile(r'display\s*:\s*none|visibility\s*:\s*hidden'))
        if len(hidden_elements) > 10:
            result['issues'].append('Excesso de elementos ocultos')
            result['risk_score'] += 15
        
        return result
    
    def detect_urgency_timers(self, soup, html_content):
        """Detectar temporizadores de urgência"""
        result = {
            'risk_score': 0,
            'timers_found': False
        }
        
        # Palavras-chave de urgência
        urgency_keywords = [
            'expires in', 'expira em', 'tempo limitado', 'limited time',
            'act now', 'aja agora', 'última chance', 'last chance',
            'countdown', 'contagem regressiva'
        ]
        
        text_content = soup.get_text().lower()
        
        for keyword in urgency_keywords:
            if keyword in text_content:
                result['timers_found'] = True
                result['risk_score'] += 10
                break
        
        # Verificar scripts de countdown
        if 'setinterval' in html_content.lower() or 'countdown' in html_content.lower():
            result['timers_found'] = True
            result['risk_score'] += 10
        
        return result
    
    def analyze_oauth(self, soup):
        """Analisar solicitações OAuth suspeitas"""
        result = {
            'risk_score': 0,
            'oauth_detected': False,
            'permissions': []
        }
        
        # Procurar por OAuth
        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            
            if 'oauth' in href.lower() or 'authorize' in href.lower():
                result['oauth_detected'] = True
                
                # Verificar permissões excessivas
                if 'scope' in href.lower():
                    result['permissions'].append(href)
                    result['risk_score'] += 15
        
        return result
