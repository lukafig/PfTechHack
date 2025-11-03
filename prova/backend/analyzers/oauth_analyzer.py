"""
OAuth Analyzer - Detecta aplicações OAuth falsas
Verifica legitimidade de páginas de autorização OAuth/SSO
"""
import re
from urllib.parse import urlparse, parse_qs

class OAuthAnalyzer:
    def __init__(self):
        # Domínios legítimos de OAuth por provedor
        self.legitimate_oauth_domains = {
            'google': [
                'accounts.google.com',
                'oauth.google.com',
                'accounts.youtube.com'
            ],
            'facebook': [
                'www.facebook.com',
                'facebook.com',
                'm.facebook.com'
            ],
            'microsoft': [
                'login.microsoftonline.com',
                'login.live.com',
                'account.microsoft.com'
            ],
            'github': [
                'github.com',
                'api.github.com'
            ],
            'twitter': [
                'api.twitter.com',
                'twitter.com',
                'x.com'
            ],
            'linkedin': [
                'www.linkedin.com',
                'linkedin.com'
            ],
            'apple': [
                'appleid.apple.com',
                'idmsa.apple.com'
            ],
            'amazon': [
                'www.amazon.com',
                'amazon.com',
                'signin.aws.amazon.com'
            ]
        }
        
        # Padrões de URL OAuth
        self.oauth_patterns = [
            r'oauth',
            r'authorize',
            r'consent',
            r'permissions',
            r'scope',
            r'login',
            r'signin',
            r'auth'
        ]
        
        # Scopes suspeitos (permissões excessivas)
        self.excessive_scopes = [
            'read_all',
            'write_all',
            'admin',
            'full_access',
            'delete',
            'manage_account',
            'financial',
            'payment'
        ]
    
    def detect_oauth_page(self, soup, url):
        """
        Detecta se a página é uma interface OAuth/SSO
        """
        # Verificar padrões na URL
        url_lower = url.lower()
        has_oauth_url = any(pattern in url_lower for pattern in self.oauth_patterns)
        
        # Verificar botões de login social
        social_login_patterns = [
            r'sign\s+in\s+with',
            r'login\s+with',
            r'continue\s+with',
            r'connect\s+with',
            r'authorize\s+with'
        ]
        
        social_buttons = []
        for pattern in social_login_patterns:
            buttons = soup.find_all(['button', 'a'], 
                string=re.compile(pattern, re.I))
            social_buttons.extend(buttons)
        
        # Verificar formulários de permissão/consentimento
        permission_keywords = ['allow', 'grant', 'permission', 'consent', 'authorize']
        permission_forms = soup.find_all('form')
        has_permission_form = False
        
        for form in permission_forms:
            form_text = form.get_text().lower()
            if any(keyword in form_text for keyword in permission_keywords):
                has_permission_form = True
                break
        
        # Verificar inputs de OAuth (client_id, redirect_uri, etc)
        oauth_inputs = soup.find_all('input', attrs={
            'name': re.compile(r'(client_id|redirect_uri|response_type|scope|state)', re.I)
        })
        
        return {
            'is_oauth': has_oauth_url or len(social_buttons) > 0 or has_permission_form or len(oauth_inputs) > 0,
            'oauth_url': has_oauth_url,
            'social_buttons': len(social_buttons),
            'permission_form': has_permission_form,
            'oauth_inputs': len(oauth_inputs)
        }
    
    def identify_provider(self, url, soup):
        """
        Tenta identificar o provedor OAuth (Google, Facebook, etc)
        """
        url_lower = url.lower()
        page_text = soup.get_text().lower()
        
        # Verificar na URL
        for provider, domains in self.legitimate_oauth_domains.items():
            if any(provider in url_lower for provider in [provider]):
                return provider
        
        # Verificar no conteúdo da página
        for provider in self.legitimate_oauth_domains.keys():
            if provider in page_text:
                return provider
        
        return None
    
    def verify_oauth_legitimacy(self, url, provider):
        """
        Verifica se a URL OAuth pertence ao domínio legítimo do provedor
        """
        if not provider or provider not in self.legitimate_oauth_domains:
            return False
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. para comparação
        domain_without_www = domain.replace('www.', '')
        
        legitimate_domains = self.legitimate_oauth_domains[provider]
        
        # Verificar se o domínio é exatamente um dos legítimos
        # ou é subdomínio de um legítimo
        for legit_domain in legitimate_domains:
            legit_without_www = legit_domain.replace('www.', '')
            
            if (domain == legit_domain or 
                domain == legit_without_www or
                domain.endswith('.' + legit_domain) or
                domain.endswith('.' + legit_without_www)):
                return True
        
        return False
    
    def check_excessive_permissions(self, url, soup):
        """
        Verifica se há solicitação de permissões excessivas
        """
        excessive = []
        
        # Verificar parâmetro scope na URL
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'scope' in params:
            scopes = params['scope'][0].split()
            
            for scope in scopes:
                scope_lower = scope.lower()
                for suspicious in self.excessive_scopes:
                    if suspicious in scope_lower:
                        excessive.append(scope)
        
        # Verificar no conteúdo da página
        page_text = soup.get_text().lower()
        suspicious_permissions = [
            'access to all',
            'full access',
            'delete your',
            'manage your account',
            'payment information',
            'credit card'
        ]
        
        for perm in suspicious_permissions:
            if perm in page_text:
                excessive.append(perm)
        
        return list(set(excessive))  # Remove duplicatas
    
    def analyze(self, soup, url):
        """
        Análise completa de OAuth
        """
        result = {
            'is_oauth_page': False,
            'is_legitimate': True,
            'provider': None,
            'provider_claimed': None,
            'domain_mismatch': False,
            'excessive_permissions': [],
            'suspicious': False,
            'risk_score': 0,
            'details': []
        }
        
        try:
            # 1. Detectar se é página OAuth
            oauth_detection = self.detect_oauth_page(soup, url)
            result['is_oauth_page'] = oauth_detection['is_oauth']
            
            if not result['is_oauth_page']:
                return result
            
            result['details'].append(
                f'ℹ️ Página OAuth detectada (botões: {oauth_detection["social_buttons"]}, '
                f'inputs: {oauth_detection["oauth_inputs"]})'
            )
            
            # 2. Identificar provedor
            provider = self.identify_provider(url, soup)
            result['provider_claimed'] = provider
            
            if provider:
                result['details'].append(
                    f'ℹ️ Provedor identificado: {provider.title()}'
                )
                
                # 3. Verificar legitimidade do domínio
                is_legitimate = self.verify_oauth_legitimacy(url, provider)
                result['is_legitimate'] = is_legitimate
                
                parsed = urlparse(url)
                result['provider'] = parsed.netloc
                
                if not is_legitimate:
                    result['suspicious'] = True
                    result['domain_mismatch'] = True
                    result['risk_score'] += 50
                    result['details'].append(
                        f'🚨 OAUTH FALSO DETECTADO: Simula {provider.title()} '
                        f'mas domínio é {parsed.netloc}'
                    )
                else:
                    result['details'].append(
                        f'✓ Domínio OAuth legítimo: {parsed.netloc}'
                    )
            else:
                # OAuth genérico sem provedor identificado
                result['details'].append(
                    '⚠️ Página OAuth sem provedor claramente identificado'
                )
                result['risk_score'] += 10
            
            # 4. Verificar permissões excessivas
            excessive = self.check_excessive_permissions(url, soup)
            if excessive:
                result['excessive_permissions'] = excessive
                result['risk_score'] += min(30, len(excessive) * 10)
                result['details'].append(
                    f'⚠️ Permissões excessivas solicitadas: {", ".join(excessive[:3])}'
                )
            
            # 5. Verificar se há formulário de senha em página OAuth
            # (OAuth real não pede senha diretamente na página de autorização)
            password_inputs = soup.find_all('input', attrs={'type': 'password'})
            if password_inputs and oauth_detection['permission_form']:
                result['risk_score'] += 20
                result['suspicious'] = True
                result['details'].append(
                    '⚠️ Formulário de senha em página OAuth (suspeito)'
                )
            
            return result
            
        except Exception as e:
            result['details'].append(f'Erro na análise OAuth: {str(e)}')
            return result

# Teste standalone
if __name__ == '__main__':
    from bs4 import BeautifulSoup
    
    analyzer = OAuthAnalyzer()
    
    print("=== Testando OAuth Analyzer ===\n")
    
    # Teste 1: OAuth legítimo (Google)
    print("1. OAuth Legítimo (Google):")
    html = '''
    <html>
        <body>
            <h1>Sign in with Google</h1>
            <button>Continue with Google</button>
            <form>
                <input name="scope" value="email profile">
                <input name="client_id" value="abc123">
            </form>
        </body>
    </html>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = analyzer.analyze(soup, 'https://accounts.google.com/oauth/authorize')
    print(f"   OAuth: {result['is_oauth_page']}")
    print(f"   Legítimo: {result['is_legitimate']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
    print()
    
    # Teste 2: OAuth falso
    print("2. OAuth FALSO:")
    result = analyzer.analyze(soup, 'https://fake-google-login.tk/oauth/authorize')
    print(f"   OAuth: {result['is_oauth_page']}")
    print(f"   Legítimo: {result['is_legitimate']}")
    print(f"   Suspeito: {result['suspicious']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
