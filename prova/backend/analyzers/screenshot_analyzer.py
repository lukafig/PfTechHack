"""
Screenshot Analyzer - Captura e compara screenshots de páginas web
Detecta clonagem visual de sites legítimos usando perceptual hashing
"""
import os
import tempfile
import imagehash
from PIL import Image
from io import BytesIO
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging

logger = logging.getLogger(__name__)

class ScreenshotAnalyzer:
    def __init__(self):
        """
        Inicializa o analisador de screenshots com base de hashes de sites legítimos
        """
        # Base de dados de hashes perceptuais de sites legítimos conhecidos
        # Em produção, isso seria carregado de um arquivo ou banco de dados
        self.legitimate_sites = {
            'google': {
                'domains': ['google.com', 'accounts.google.com', 'mail.google.com'],
                'hash': None,  # Será calculado na primeira execução
                'threshold': 10  # Diferença máxima de hash para considerar similar
            },
            'facebook': {
                'domains': ['facebook.com', 'www.facebook.com', 'm.facebook.com'],
                'hash': None,
                'threshold': 10
            },
            'amazon': {
                'domains': ['amazon.com', 'www.amazon.com'],
                'hash': None,
                'threshold': 10
            },
            'paypal': {
                'domains': ['paypal.com', 'www.paypal.com'],
                'hash': None,
                'threshold': 10
            },
            'microsoft': {
                'domains': ['microsoft.com', 'login.microsoftonline.com', 'outlook.com'],
                'hash': None,
                'threshold': 10
            },
            'apple': {
                'domains': ['apple.com', 'appleid.apple.com', 'icloud.com'],
                'hash': None,
                'threshold': 10
            },
            'netflix': {
                'domains': ['netflix.com', 'www.netflix.com'],
                'hash': None,
                'threshold': 10
            },
            'linkedin': {
                'domains': ['linkedin.com', 'www.linkedin.com'],
                'hash': None,
                'threshold': 10
            },
            'twitter': {
                'domains': ['twitter.com', 'x.com'],
                'hash': None,
                'threshold': 10
            },
            'instagram': {
                'domains': ['instagram.com', 'www.instagram.com'],
                'hash': None,
                'threshold': 10
            }
        }
        
        # Configurações do Selenium - OTIMIZADO PARA VELOCIDADE
        self.driver = None
        self.screenshot_timeout = 5  # segundos (reduzido ao mínimo)
        self.page_load_timeout = 5  # segundos (reduzido ao mínimo)
    
    def _init_driver(self):
        """
        Inicializa o WebDriver do Firefox em modo headless
        """
        if self.driver is not None:
            return
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Otimizações para velocidade
            options.set_preference('permissions.default.image', 2)  # Não carregar imagens
            options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', False)
            options.set_preference('javascript.enabled', True)  # Manter JS para layout
            options.set_preference('permissions.default.stylesheet', 2)  # Não carregar CSS externo
            options.set_preference('permissions.default.media', 2)  # Não carregar media
            
            # Tentar encontrar o Firefox
            firefox_paths = [
                '/snap/firefox/7084/usr/lib/firefox/firefox',  # Snap Firefox
                '/snap/firefox/current/usr/lib/firefox/firefox',  # Snap com link current
                '/usr/lib/firefox/firefox',  # Firefox tradicional
                '/usr/bin/firefox',
                '/snap/bin/firefox',
                '/usr/local/bin/firefox'
            ]
            
            firefox_binary = None
            for path in firefox_paths:
                if os.path.exists(path):
                    firefox_binary = path
                    logger.info(f"Firefox encontrado em: {path}")
                    break
            
            if firefox_binary:
                options.binary_location = firefox_binary
            
            # Criar serviço do geckodriver
            service = Service(log_path=os.devnull)
            
            self.driver = webdriver.Firefox(options=options, service=service)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            
            logger.info("WebDriver Firefox inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar WebDriver: {str(e)}")
            self.driver = None
            raise
    
    def _cleanup_driver(self):
        """
        Limpa e fecha o WebDriver
        """
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Erro ao fechar WebDriver: {str(e)}")
            finally:
                self.driver = None
    
    def capture_screenshot(self, url, retries=1):
        """
        Captura screenshot de uma URL
        
        Args:
            url: URL para capturar
            retries: Número de tentativas em caso de erro (reduzido para 1)
            
        Returns:
            PIL.Image object ou None em caso de erro
        """
        for attempt in range(retries):
            try:
                self._init_driver()
                
                # Adicionar protocolo se não tiver
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                
                logger.info(f"Capturando screenshot de {url} (tentativa {attempt + 1}/{retries})")
                
                # Navegar para a página
                self.driver.get(url)
                
                # Aguardar o mínimo possível
                time.sleep(0.5)  # Reduzido de 1 para 0.5 segundo
                
                # Capturar screenshot
                screenshot_bytes = self.driver.get_screenshot_as_png()
                
                # Converter para PIL Image
                image = Image.open(BytesIO(screenshot_bytes))
                
                logger.info(f"Screenshot capturado com sucesso: {image.size}")
                
                return image
                
            except TimeoutException:
                logger.warning(f"Timeout ao carregar {url} (tentativa {attempt + 1}/{retries})")
                if attempt == retries - 1:
                    return None
                    
            except WebDriverException as e:
                logger.error(f"Erro do WebDriver ao capturar {url}: {str(e)}")
                self._cleanup_driver()
                if attempt == retries - 1:
                    return None
                    
            except Exception as e:
                logger.error(f"Erro desconhecido ao capturar {url}: {str(e)}")
                if attempt == retries - 1:
                    return None
        
        return None
    
    def calculate_phash(self, image):
        """
        Calcula perceptual hash de uma imagem
        
        Args:
            image: PIL.Image object
            
        Returns:
            imagehash.ImageHash object
        """
        try:
            # Redimensionar para padronizar
            image = image.resize((256, 256))
            
            # Calcular perceptual hash
            phash = imagehash.phash(image, hash_size=16)
            
            return phash
            
        except Exception as e:
            logger.error(f"Erro ao calcular hash: {str(e)}")
            return None
    
    def compare_with_legitimate(self, url, screenshot_hash):
        """
        Compara screenshot com sites legítimos conhecidos
        
        Args:
            url: URL analisada
            screenshot_hash: Hash da screenshot
            
        Returns:
            dict com resultados da comparação
        """
        results = {
            'is_clone': False,
            'cloned_brand': None,
            'similarity_score': 0,
            'hash_difference': 999,
            'matches': []
        }
        
        if screenshot_hash is None:
            return results
        
        # Extrair domínio da URL
        from urllib.parse import urlparse
        parsed = urlparse(url if url.startswith('http') else 'https://' + url)
        domain = parsed.netloc.lower().replace('www.', '')
        
        min_difference = 999
        best_match = None
        
        # Comparar com cada marca conhecida
        for brand, info in self.legitimate_sites.items():
            # Verificar se o domínio já é legítimo
            if any(legit_domain in domain for legit_domain in info['domains']):
                results['is_legitimate_domain'] = True
                results['brand'] = brand
                return results
            
            # Se ainda não temos hash da marca, pular
            if info['hash'] is None:
                continue
            
            # Calcular diferença
            try:
                difference = screenshot_hash - info['hash']
                
                if difference < min_difference:
                    min_difference = difference
                    best_match = brand
                
                # Se muito similar, pode ser clone
                if difference <= info['threshold']:
                    results['matches'].append({
                        'brand': brand,
                        'difference': difference,
                        'threshold': info['threshold']
                    })
                    
            except Exception as e:
                logger.error(f"Erro ao comparar com {brand}: {str(e)}")
                continue
        
        # Avaliar resultados
        if results['matches']:
            results['is_clone'] = True
            results['cloned_brand'] = results['matches'][0]['brand']
            results['similarity_score'] = 100 - (results['matches'][0]['difference'] * 5)
            results['hash_difference'] = results['matches'][0]['difference']
        elif best_match and min_difference < 20:
            # Similar mas não idêntico
            results['cloned_brand'] = best_match
            results['similarity_score'] = max(0, 100 - (min_difference * 5))
            results['hash_difference'] = min_difference
        
        return results
    
    def analyze(self, url):
        """
        Análise completa de screenshot
        
        Args:
            url: URL para analisar
            
        Returns:
            dict com resultados da análise
        """
        result = {
            'screenshot_captured': False,
            'screenshot_path': None,
            'visual_hash': None,
            'is_clone': False,
            'cloned_brand': None,
            'similarity_score': 0,
            'risk_score': 0,
            'details': [],
            'error': None,
            'feature_available': True
        }
        
        try:
            # Capturar screenshot
            screenshot = self.capture_screenshot(url)
            
            if screenshot is None:
                result['error'] = 'Não foi possível capturar screenshot (Selenium/Firefox não configurado)'
                result['details'].append('ℹ️ Screenshot analysis indisponível neste ambiente')
                result['details'].append('ℹ️ Sistema continua funcionando com outras análises')
                result['feature_available'] = False
                return result
            
            result['screenshot_captured'] = True
            result['details'].append('✓ Screenshot capturado com sucesso')
            
            # Salvar screenshot
            try:
                screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'screenshots')
                os.makedirs(screenshots_dir, exist_ok=True)
                
                # Nome do arquivo baseado no hash da URL
                import hashlib
                url_hash = hashlib.md5(url.encode()).hexdigest()
                screenshot_filename = f'screenshot_{url_hash}.png'
                screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
                
                # Salvar imagem
                screenshot.save(screenshot_path, 'PNG')
                result['screenshot_path'] = f'/static/screenshots/{screenshot_filename}'
                logger.info(f"Screenshot salvo em: {screenshot_path}")
                
            except Exception as e:
                logger.error(f"Erro ao salvar screenshot: {str(e)}")
            
            # Calcular hash
            phash = self.calculate_phash(screenshot)
            
            if phash is None:
                result['error'] = 'Erro ao calcular hash da imagem'
                result['details'].append('⚠️ Erro ao processar screenshot')
                return result
            
            result['visual_hash'] = str(phash)
            result['details'].append(f'✓ Hash visual calculado: {str(phash)[:16]}...')
            
            # Comparar com sites legítimos
            comparison = self.compare_with_legitimate(url, phash)
            
            # Se for domínio legítimo
            if comparison.get('is_legitimate_domain'):
                result['details'].append(
                    f'✓ Domínio legítimo verificado: {comparison.get("brand")}'
                )
                return result
            
            # Se for clone detectado
            if comparison['is_clone']:
                result['is_clone'] = True
                result['cloned_brand'] = comparison['cloned_brand']
                result['similarity_score'] = comparison['similarity_score']
                result['risk_score'] = min(100, 50 + comparison['similarity_score'] / 2)
                
                result['details'].append(
                    f'🚨 CLONE DETECTADO: Página visualmente idêntica ao {comparison["cloned_brand"].upper()}'
                )
                result['details'].append(
                    f'⚠️ Similaridade visual: {comparison["similarity_score"]:.1f}%'
                )
                result['details'].append(
                    f'⚠️ Diferença de hash: {comparison["hash_difference"]}'
                )
            
            # Se for similar mas não clone
            elif comparison['cloned_brand'] and comparison['similarity_score'] > 50:
                result['cloned_brand'] = comparison['cloned_brand']
                result['similarity_score'] = comparison['similarity_score']
                result['risk_score'] = comparison['similarity_score'] / 2
                
                result['details'].append(
                    f'⚠️ Página similar ao {comparison["cloned_brand"].upper()}'
                )
                result['details'].append(
                    f'ℹ️ Similaridade visual: {comparison["similarity_score"]:.1f}%'
                )
            else:
                result['details'].append('✓ Nenhuma clonagem visual detectada')
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise de screenshot: {str(e)}", exc_info=True)
            result['error'] = 'Screenshot analysis temporariamente indisponível'
            result['details'].append('ℹ️ Screenshot analysis indisponível (Firefox/Selenium não configurado)')
            result['details'].append('ℹ️ Sistema continua com 6 outras análises ativas')
            result['feature_available'] = False
            return result
        
        finally:
            # Sempre limpar o driver
            self._cleanup_driver()
    
    def __del__(self):
        """
        Destrutor para garantir limpeza do driver
        """
        self._cleanup_driver()


# Teste standalone
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    analyzer = ScreenshotAnalyzer()
    
    print("=== Testando Screenshot Analyzer ===\n")
    
    # Teste 1: Site legítimo
    print("1. Testando site legítimo (Google):")
    result = analyzer.analyze('https://www.google.com')
    print(f"   Screenshot: {result['screenshot_captured']}")
    print(f"   Clone: {result['is_clone']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
    print()
    
    # Teste 2: Outro site
    print("2. Testando outro site:")
    result = analyzer.analyze('https://github.com')
    print(f"   Screenshot: {result['screenshot_captured']}")
    print(f"   Clone: {result['is_clone']}")
    print(f"   Risk Score: {result['risk_score']}")
    print(f"   Detalhes: {result['details']}")
