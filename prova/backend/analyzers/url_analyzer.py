"""
Analisador de URLs - Heurísticas Avançadas
"""

import re
import requests
import whois
import socket
import ssl
import dns.resolver
from urllib.parse import urlparse
from datetime import datetime, timedelta
from Levenshtein import distance as levenshtein_distance
import json
import os

class URLAnalyzer:
    def __init__(self):
        self.phishing_databases = []
        self.load_phishing_databases()
        self.whitelist = self.load_whitelist()
        self.known_brands = self.load_known_brands()
        
    def load_phishing_databases(self):
        """Carregar bancos de dados de phishing"""
        # PhishTank
        try:
            response = requests.get(
                'https://data.phishtank.com/data/online-valid.json',
                timeout=10
            )
            if response.status_code == 200:
                self.phishing_databases.extend([entry['url'] for entry in response.json()])
        except:
            pass
    
    def load_whitelist(self):
        """Carregar lista de domínios confiáveis"""
        whitelist_file = 'data/whitelist.json'
        if os.path.exists(whitelist_file):
            with open(whitelist_file, 'r') as f:
                return json.load(f)
        return []
    
    def load_known_brands(self):
        """Carregar lista de marcas conhecidas para comparação"""
        return [
            'google', 'facebook', 'amazon', 'microsoft', 'apple',
            'netflix', 'paypal', 'ebay', 'instagram', 'twitter',
            'linkedin', 'dropbox', 'adobe', 'spotify', 'zoom',
            'github', 'stackoverflow', 'reddit', 'wikipedia', 'youtube',
            'whatsapp', 'telegram', 'discord', 'slack', 'shopify',
            'wordpress', 'salesforce', 'oracle', 'ibm', 'samsung',
            'bankofamerica', 'chase', 'wellsfargo', 'citibank', 'hsbc',
            'santander', 'bradesco', 'itau', 'nubank', 'bb'
        ]
    
    def analyze(self, url):
        """Executar análise completa de URL"""
        results = {
            'url': url,
            'risk_score': 0,
            'checks': {}
        }
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 1. Verificar se está em whitelist
        if domain in self.whitelist:
            results['whitelisted'] = True
            results['risk_score'] = 0
            return results
        
        # 2. Verificar em listas de phishing conhecidas
        blacklist_check = self.check_blacklists(url)
        results['checks']['blacklist'] = blacklist_check
        if blacklist_check['found']:
            results['risk_score'] += 50
            results['blacklisted'] = True
        
        # 3. Análise de características do domínio
        domain_analysis = self.analyze_domain(domain)
        results['checks']['domain'] = domain_analysis
        results['risk_score'] += domain_analysis['risk_score']
        
        # 4. Verificar similaridade com marcas conhecidas
        brand_similarity = self.check_brand_similarity(domain)
        results['checks']['brand_similarity'] = brand_similarity
        results['risk_score'] += brand_similarity['risk_score']
        
        # 5. Análise WHOIS (idade do domínio)
        whois_analysis = self.analyze_whois(domain)
        results['checks']['whois'] = whois_analysis
        results['risk_score'] += whois_analysis['risk_score']
        
        # 6. Verificação de certificado SSL
        ssl_analysis = self.analyze_ssl(domain)
        results['checks']['ssl'] = ssl_analysis
        results['risk_score'] += ssl_analysis['risk_score']
        results['ssl_issues'] = ssl_analysis.get('has_issues', False)
        
        # 7. Análise de DNS
        dns_analysis = self.analyze_dns(domain)
        results['checks']['dns'] = dns_analysis
        results['risk_score'] += dns_analysis['risk_score']
        
        # 8. Verificar redirecionamentos suspeitos
        redirect_analysis = self.analyze_redirects(url)
        results['checks']['redirects'] = redirect_analysis
        results['risk_score'] += redirect_analysis['risk_score']
        
        # 9. Análise de URL encurtada
        shortener_check = self.check_url_shortener(url)
        results['checks']['url_shortener'] = shortener_check
        results['risk_score'] += shortener_check['risk_score']
        
        # 10. Características da URL
        url_features = self.extract_url_features(url)
        results['checks']['url_features'] = url_features
        results['risk_score'] += url_features['risk_score']
        
        results['suspicious_domain'] = results['risk_score'] > 30
        results['young_domain'] = whois_analysis.get('young_domain', False)
        
        # Normalizar score (máximo 100)
        results['risk_score'] = min(100, results['risk_score'])
        
        return results
    
    def check_blacklists(self, url):
        """Verificar URL em listas de phishing"""
        result = {
            'found': False,
            'sources': []
        }
        
        # PhishTank
        if url in self.phishing_databases:
            result['found'] = True
            result['sources'].append('PhishTank')
        
        # Google Safe Browsing (simplificado)
        # Em produção, usar API oficial
        try:
            # Simulação - em produção usar API key real
            pass
        except:
            pass
        
        return result
    
    def analyze_domain(self, domain):
        """Analisar características do domínio"""
        result = {
            'risk_score': 0,
            'issues': []
        }
        
        # Números substituindo letras (ex: g00gle.com)
        if re.search(r'\d', domain):
            result['risk_score'] += 10
            result['issues'].append('Números no domínio')
        
        # Excesso de subdomínios
        subdomain_count = len(domain.split('.')) - 2
        if subdomain_count > 2:
            result['risk_score'] += 15
            result['issues'].append(f'Excesso de subdomínios ({subdomain_count})')
        
        # Caracteres especiais suspeitos
        if re.search(r'[-_]{2,}', domain):
            result['risk_score'] += 10
            result['issues'].append('Múltiplos hífens/underscores')
        
        # Domínio muito longo
        if len(domain) > 40:
            result['risk_score'] += 10
            result['issues'].append('Domínio muito longo')
        
        # @ na URL (técnica de phishing)
        if '@' in domain:
            result['risk_score'] += 20
            result['issues'].append('Símbolo @ no domínio')
        
        return result
    
    def check_brand_similarity(self, domain):
        """Verificar similaridade com marcas conhecidas usando Levenshtein"""
        result = {
            'risk_score': 0,
            'similar_brands': []
        }
        
        domain_base = domain.split('.')[0].lower()
        
        for brand in self.known_brands:
            distance = levenshtein_distance(domain_base, brand)
            similarity = 1 - (distance / max(len(domain_base), len(brand)))
            
            # Se muito similar mas não idêntico = suspeito
            if 0.7 < similarity < 1.0:
                result['risk_score'] += 20
                result['similar_brands'].append({
                    'brand': brand,
                    'similarity': round(similarity * 100, 2),
                    'domain_checked': domain_base
                })
        
        return result
    
    def analyze_whois(self, domain):
        """Análise WHOIS - idade do domínio"""
        result = {
            'risk_score': 0,
            'young_domain': False,
            'info': {}
        }
        
        try:
            w = whois.whois(domain)
            
            # Data de criação
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if creation_date:
                age = datetime.now() - creation_date
                result['info']['age_days'] = age.days
                result['info']['creation_date'] = creation_date.isoformat()
                
                # Domínio criado há menos de 6 meses é suspeito
                if age < timedelta(days=180):
                    result['risk_score'] += 20
                    result['young_domain'] = True
                    result['info']['warning'] = 'Domínio recém-criado'
                
                # Domínio muito novo (menos de 30 dias)
                elif age < timedelta(days=30):
                    result['risk_score'] += 30
                    result['young_domain'] = True
                    result['info']['warning'] = 'Domínio muito novo'
            
            # Registrar informações adicionais
            if w.registrar:
                result['info']['registrar'] = w.registrar
            if w.country:
                result['info']['country'] = w.country
                
        except Exception as e:
            result['info']['error'] = 'Não foi possível obter informações WHOIS'
        
        return result
    
    def analyze_ssl(self, domain):
        """Análise de certificado SSL"""
        result = {
            'risk_score': 0,
            'has_issues': False,
            'details': {}
        }
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Verificar validade
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    result['details']['expires_in_days'] = days_until_expiry
                    result['details']['issuer'] = dict(x[0] for x in cert['issuer'])
                    result['details']['subject'] = dict(x[0] for x in cert['subject'])
                    
                    # Certificado expirando em breve
                    if days_until_expiry < 30:
                        result['risk_score'] += 15
                        result['has_issues'] = True
                        result['details']['warning'] = 'Certificado expirando em breve'
                    
                    # Verificar se o domínio corresponde ao certificado
                    cert_domain = result['details']['subject'].get('commonName', '')
                    if cert_domain != domain and not cert_domain.startswith('*.'):
                        result['risk_score'] += 20
                        result['has_issues'] = True
                        result['details']['warning'] = 'Domínio não corresponde ao certificado'
                        
        except ssl.SSLError:
            result['risk_score'] += 30
            result['has_issues'] = True
            result['details']['error'] = 'Erro no certificado SSL'
        except:
            result['details']['error'] = 'Não foi possível verificar SSL'
        
        return result
    
    def analyze_dns(self, domain):
        """Análise de DNS - detectar DNS dinâmico"""
        result = {
            'risk_score': 0,
            'details': {}
        }
        
        dynamic_dns_providers = ['no-ip', 'dyndns', 'ddns', 'changeip', 'afraid']
        
        try:
            # Verificar se usa DNS dinâmico
            for provider in dynamic_dns_providers:
                if provider in domain.lower():
                    result['risk_score'] += 25
                    result['details']['dynamic_dns'] = True
                    result['details']['provider'] = provider
                    break
            
            # Resolver DNS
            answers = dns.resolver.resolve(domain, 'A')
            ips = [str(rdata) for rdata in answers]
            result['details']['ip_addresses'] = ips
            
        except:
            result['details']['error'] = 'Erro ao resolver DNS'
        
        return result
    
    def analyze_redirects(self, url):
        """Verificar redirecionamentos suspeitos"""
        result = {
            'risk_score': 0,
            'redirects': []
        }
        
        try:
            response = requests.get(url, allow_redirects=True, timeout=5)
            
            if len(response.history) > 0:
                result['redirects'] = [r.url for r in response.history]
                
                # Múltiplos redirecionamentos
                if len(response.history) > 2:
                    result['risk_score'] += 15
                    result['warning'] = 'Múltiplos redirecionamentos'
                
                # Redirecionamento para domínio diferente
                original_domain = urlparse(url).netloc
                final_domain = urlparse(response.url).netloc
                
                if original_domain != final_domain:
                    result['risk_score'] += 10
                    result['warning'] = 'Redirecionamento para domínio diferente'
                    
        except:
            pass
        
        return result
    
    def check_url_shortener(self, url):
        """Verificar se é URL encurtada"""
        result = {
            'risk_score': 0,
            'is_shortened': False
        }
        
        shorteners = ['bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd', 'buff.ly', 'adf.ly']
        
        domain = urlparse(url).netloc
        
        for shortener in shorteners:
            if shortener in domain:
                result['is_shortened'] = True
                result['risk_score'] += 15
                result['shortener'] = shortener
                break
        
        return result
    
    def extract_url_features(self, url):
        """Extrair características da URL"""
        result = {
            'risk_score': 0,
            'features': {}
        }
        
        # Comprimento da URL
        url_length = len(url)
        result['features']['length'] = url_length
        
        if url_length > 100:
            result['risk_score'] += 10
        
        # Número de caracteres especiais
        special_chars = len(re.findall(r'[^a-zA-Z0-9]', url))
        result['features']['special_chars'] = special_chars
        
        if special_chars > 15:
            result['risk_score'] += 10
        
        # Uso de IP ao invés de domínio
        if re.search(r'\d+\.\d+\.\d+\.\d+', url):
            result['risk_score'] += 30
            result['features']['uses_ip'] = True
        
        # HTTPS
        if url.startswith('http://'):
            result['risk_score'] += 15
            result['features']['no_https'] = True
        
        return result
    
    def get_whitelist(self):
        """Obter whitelist"""
        return self.whitelist
    
    def add_to_whitelist(self, domain):
        """Adicionar domínio à whitelist"""
        if domain not in self.whitelist:
            self.whitelist.append(domain)
            self.save_whitelist()
    
    def remove_from_whitelist(self, domain):
        """Remover domínio da whitelist"""
        if domain in self.whitelist:
            self.whitelist.remove(domain)
            self.save_whitelist()
    
    def save_whitelist(self):
        """Salvar whitelist"""
        os.makedirs('data', exist_ok=True)
        with open('data/whitelist.json', 'w') as f:
            json.dump(self.whitelist, f, indent=2)
