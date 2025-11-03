"""
Geolocation Analyzer - Análise de localização geográfica do servidor
Verifica país de hospedagem, ASN e reputação do provedor
"""
import requests
import socket
import dns.resolver

class GeolocationAnalyzer:
    def __init__(self):
        # Países considerados de alto risco para phishing
        self.high_risk_countries = [
            'CN',  # China
            'RU',  # Rússia
            'KP',  # Coreia do Norte
            'IR',  # Irã
            'SY',  # Síria
            'VE',  # Venezuela
            'CU',  # Cuba
            'SD',  # Sudão
            'SO',  # Somália
            'BY',  # Belarus
            'MM'   # Myanmar
        ]
        
        # ASN conhecidos por hospedarem phishing
        self.suspicious_asn = [
            'AS4134',   # China Telecom
            'AS4837',   # China Unicom
            'AS12389',  # Rostelecom (RU)
            'AS8551',   # Bezeq International (IL) - usado em phishing
            'AS9009'    # M247 Europe - VPS barato
        ]
        
        # Provedores VPS/Cloud comuns em phishing
        self.suspicious_hosting = [
            'digitalocean',
            'linode', 
            'vultr',
            'ovh',
            'hetzner',
            'contabo',
            'namecheap',
            'hostinger'
        ]
    
    def get_ip_from_domain(self, domain):
        """
        Resolve o domínio para obter o endereço IP
        """
        try:
            # Remove protocolo se presente
            domain = domain.replace('https://', '').replace('http://', '')
            domain = domain.split('/')[0]
            
            ip = socket.gethostbyname(domain)
            return ip
        except Exception as e:
            return None
    
    def get_geolocation(self, ip):
        """
        Obtém informações de geolocalização usando ip-api.com (gratuito)
        """
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip}',
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            return None
    
    def analyze_hosting_reputation(self, isp):
        """
        Analisa a reputação do provedor de hospedagem
        """
        if not isp:
            return False, 0
        
        isp_lower = isp.lower()
        
        # Verificar se é provedor suspeito
        for provider in self.suspicious_hosting:
            if provider in isp_lower:
                return True, 15
        
        # Verificar se é hospedagem residencial (suspeito)
        residential_keywords = ['dsl', 'cable', 'residential', 'dynamic', 'dhcp']
        if any(keyword in isp_lower for keyword in residential_keywords):
            return True, 20
        
        return False, 0
    
    def analyze(self, domain):
        """
        Análise completa de geolocalização
        """
        result = {
            'ip': None,
            'country': None,
            'country_code': None,
            'city': None,
            'region': None,
            'isp': None,
            'org': None,
            'asn': None,
            'timezone': None,
            'high_risk_location': False,
            'suspicious_hosting': False,
            'suspicious_asn': False,
            'residential_ip': False,
            'risk_score': 0,
            'details': []
        }
        
        try:
            # Obter IP do domínio
            ip = self.get_ip_from_domain(domain)
            if not ip:
                result['details'].append('Não foi possível resolver IP do domínio')
                return result
            
            result['ip'] = ip
            
            # Obter dados de geolocalização
            geo_data = self.get_geolocation(ip)
            if not geo_data:
                result['details'].append('Não foi possível obter dados de geolocalização')
                return result
            
            # Verificar se a API retornou sucesso
            if geo_data.get('status') != 'success':
                result['details'].append(f'Erro na geolocalização: {geo_data.get("message", "Desconhecido")}')
                return result
            
            # Extrair informações
            result['country'] = geo_data.get('country')
            result['country_code'] = geo_data.get('countryCode')
            result['city'] = geo_data.get('city')
            result['region'] = geo_data.get('regionName')
            result['isp'] = geo_data.get('isp')
            result['org'] = geo_data.get('org')
            result['timezone'] = geo_data.get('timezone')
            
            # Extrair ASN
            as_info = geo_data.get('as', '')
            if as_info:
                result['asn'] = as_info.split()[0] if as_info else None
            
            # === ANÁLISE DE RISCO ===
            
            # 1. Verificar país de alto risco
            if result['country_code'] in self.high_risk_countries:
                result['high_risk_location'] = True
                result['risk_score'] += 25
                result['details'].append(
                    f'⚠️ Hospedado em país de alto risco: {result["country"]} ({result["country_code"]})'
                )
            
            # 2. Verificar ASN suspeito
            if result['asn'] in self.suspicious_asn:
                result['suspicious_asn'] = True
                result['risk_score'] += 20
                result['details'].append(
                    f'⚠️ ASN conhecido por hospedar phishing: {result["asn"]}'
                )
            
            # 3. Analisar reputação do hosting
            is_suspicious, risk_points = self.analyze_hosting_reputation(result['isp'])
            if is_suspicious:
                result['suspicious_hosting'] = True
                result['risk_score'] += risk_points
                
                if 'residential' in result['isp'].lower() or 'dynamic' in result['isp'].lower():
                    result['residential_ip'] = True
                    result['details'].append(
                        f'🚨 IP residencial/dinâmico detectado: {result["isp"]}'
                    )
                else:
                    result['details'].append(
                        f'⚠️ Provedor comumente usado em phishing: {result["isp"]}'
                    )
            
            # 4. Verificar se ISP e ORG são diferentes (suspeito)
            if result['isp'] and result['org'] and result['isp'] != result['org']:
                if 'cloud' in result['org'].lower() or 'host' in result['org'].lower():
                    result['risk_score'] += 5
                    result['details'].append(
                        f'ℹ️ Hospedagem em nuvem/VPS: {result["org"]}'
                    )
            
            # 5. Informações úteis (não aumentam risco)
            if not result['details']:
                result['details'].append(
                    f'✓ Hospedado em: {result["country"]}, {result["city"]}'
                )
                result['details'].append(
                    f'ℹ️ Provedor: {result["isp"]}'
                )
            
            return result
            
        except Exception as e:
            result['details'].append(f'Erro na análise de geolocalização: {str(e)}')
            return result

# Teste standalone
if __name__ == '__main__':
    analyzer = GeolocationAnalyzer()
    
    print("=== Testando Geolocalização ===\n")
    
    # Teste com domínio legítimo
    print("1. Google.com:")
    result = analyzer.analyze('google.com')
    print(f"   IP: {result['ip']}")
    print(f"   País: {result['country']} ({result['country_code']})")
    print(f"   ISP: {result['isp']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
    print()
    
    # Teste com domínio suspeito (simulação)
    print("2. Domínio suspeito:")
    result = analyzer.analyze('example.com')
    print(f"   IP: {result['ip']}")
    print(f"   País: {result['country']} ({result['country_code']})")
    print(f"   ISP: {result['isp']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
