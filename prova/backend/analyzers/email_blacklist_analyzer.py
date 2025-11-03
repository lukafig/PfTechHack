"""
Email Blacklist Analyzer - Verifica se domínio está em blacklists de spam
Usa DNSBL (DNS-based Blackhole List) para verificar reputação
"""
import socket
import dns.resolver
from urllib.parse import urlparse

class EmailBlacklistAnalyzer:
    def __init__(self):
        # Lista de DNSBLs públicos confiáveis
        self.dnsbl_servers = [
            'zen.spamhaus.org',      # Spamhaus - o mais respeitado
            'bl.spamcop.net',        # SpamCop
            'dnsbl.sorbs.net',       # SORBS
            'b.barracudacentral.org', # Barracuda
            'dnsbl-1.uceprotect.net', # UCEProtect
            'cbl.abuseat.org',       # CBL (Composite Blocking List)
            'psbl.surriel.com',      # Passive Spam Block List
            'bl.mailspike.net'       # Mailspike
        ]
        
        # Pesos por reputação do DNSBL
        self.dnsbl_weights = {
            'zen.spamhaus.org': 30,
            'bl.spamcop.net': 25,
            'dnsbl.sorbs.net': 20,
            'b.barracudacentral.org': 20,
            'dnsbl-1.uceprotect.net': 15,
            'cbl.abuseat.org': 25,
            'psbl.surriel.com': 15,
            'bl.mailspike.net': 20
        }
    
    def get_ip_from_domain(self, domain):
        """
        Resolve o domínio para obter o endereço IP
        """
        try:
            # Limpar domínio
            domain = domain.replace('https://', '').replace('http://', '')
            domain = domain.split('/')[0]
            domain = domain.split(':')[0]
            
            ip = socket.gethostbyname(domain)
            return ip
        except Exception as e:
            return None
    
    def reverse_ip(self, ip):
        """
        Inverte o IP para formato DNSBL
        Ex: 192.168.1.1 -> 1.1.168.192
        """
        try:
            parts = ip.split('.')
            parts.reverse()
            return '.'.join(parts)
        except:
            return None
    
    def check_dnsbl(self, ip, dnsbl_server):
        """
        Verifica se o IP está listado em um DNSBL específico
        """
        try:
            reversed_ip = self.reverse_ip(ip)
            if not reversed_ip:
                return False, None
            
            # Construir query DNSBL: reversed_ip.dnsbl_server
            query = f"{reversed_ip}.{dnsbl_server}"
            
            # Tentar resolver
            resolver = dns.resolver.Resolver()
            resolver.timeout = 2
            resolver.lifetime = 2
            
            try:
                answers = resolver.resolve(query, 'A')
                # Se resolveu, está na blacklist
                return True, str(answers[0])
            except dns.resolver.NXDOMAIN:
                # Não está na blacklist
                return False, None
            except dns.resolver.NoAnswer:
                return False, None
            except dns.resolver.Timeout:
                return False, None
            
        except Exception as e:
            return False, None
    
    def check_domain_reputation(self, domain):
        """
        Verifica reputação do domínio em múltiplas blacklists
        """
        results = {
            'listed_in': [],
            'not_listed_in': [],
            'failed_checks': []
        }
        
        ip = self.get_ip_from_domain(domain)
        if not ip:
            return None, results
        
        for dnsbl in self.dnsbl_servers:
            is_listed, response = self.check_dnsbl(ip, dnsbl)
            
            if is_listed:
                results['listed_in'].append({
                    'dnsbl': dnsbl,
                    'response': response
                })
            elif response is None and not is_listed:
                # Conseguiu verificar, não está listado
                results['not_listed_in'].append(dnsbl)
            else:
                # Falha na verificação
                results['failed_checks'].append(dnsbl)
        
        return ip, results
    
    def analyze(self, domain):
        """
        Análise completa de blacklist de email
        """
        result = {
            'ip': None,
            'checked': False,
            'listed_count': 0,
            'blacklists': [],
            'is_blacklisted': False,
            'reputation': 'unknown',
            'risk_score': 0,
            'details': []
        }
        
        try:
            # Limpar domínio
            if domain.startswith('http'):
                parsed = urlparse(domain)
                domain = parsed.netloc
            
            # Obter IP e verificar
            ip, check_results = self.check_domain_reputation(domain)
            
            if not ip:
                result['details'].append('⚠️ Não foi possível resolver IP para verificação de blacklist')
                return result
            
            result['ip'] = ip
            result['checked'] = True
            
            # Processar resultados
            result['listed_count'] = len(check_results['listed_in'])
            result['blacklists'] = [item['dnsbl'] for item in check_results['listed_in']]
            
            if result['listed_count'] > 0:
                result['is_blacklisted'] = True
                
                # Calcular risk score baseado nos DNSBLs em que está listado
                for item in check_results['listed_in']:
                    dnsbl = item['dnsbl']
                    weight = self.dnsbl_weights.get(dnsbl, 15)
                    result['risk_score'] += weight
                
                # Limitar a 100
                result['risk_score'] = min(100, result['risk_score'])
                
                # Determinar reputação
                if result['listed_count'] >= 3:
                    result['reputation'] = 'very_bad'
                    result['details'].append(
                        f'🚨 ALTA REPUTAÇÃO NEGATIVA: Listado em {result["listed_count"]} blacklists'
                    )
                elif result['listed_count'] >= 2:
                    result['reputation'] = 'bad'
                    result['details'].append(
                        f'⚠️ Reputação negativa: Listado em {result["listed_count"]} blacklists'
                    )
                else:
                    result['reputation'] = 'suspicious'
                    result['details'].append(
                        f'⚠️ Reputação suspeita: Listado em 1 blacklist'
                    )
                
                # Listar blacklists específicas
                major_lists = ['zen.spamhaus.org', 'bl.spamcop.net', 'cbl.abuseat.org']
                major_found = [bl for bl in result['blacklists'] if bl in major_lists]
                
                if major_found:
                    result['details'].append(
                        f'🔴 Listado em blacklists principais: {", ".join(major_found)}'
                    )
                
            else:
                result['reputation'] = 'good'
                result['details'].append(
                    f'✓ IP não encontrado em {len(check_results["not_listed_in"])} blacklists verificadas'
                )
            
            # Informações adicionais
            if check_results['failed_checks']:
                result['details'].append(
                    f'ℹ️ {len(check_results["failed_checks"])} verificações falharam (timeout/erro)'
                )
            
            return result
            
        except Exception as e:
            result['details'].append(f'Erro na verificação de blacklist: {str(e)}')
            return result

# Teste standalone
if __name__ == '__main__':
    analyzer = EmailBlacklistAnalyzer()
    
    print("=== Testando Email Blacklist Analyzer ===\n")
    
    # Teste com domínio legítimo
    print("1. Google.com:")
    result = analyzer.analyze('google.com')
    print(f"   IP: {result['ip']}")
    print(f"   Blacklisted: {result['is_blacklisted']}")
    print(f"   Listed in: {result['listed_count']} blacklists")
    print(f"   Reputação: {result['reputation']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
    print()
    
    # Teste com domínio conhecido
    print("2. Example.com:")
    result = analyzer.analyze('example.com')
    print(f"   IP: {result['ip']}")
    print(f"   Blacklisted: {result['is_blacklisted']}")
    print(f"   Listed in: {result['listed_count']} blacklists")
    print(f"   Reputação: {result['reputation']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
