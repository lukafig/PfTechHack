#!/usr/bin/env python3
"""Teste rápido do Selenium"""
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

try:
    print("Inicializando Firefox headless...")
    opts = Options()
    opts.add_argument('--headless')
    opts.binary_location = '/snap/firefox/7084/usr/lib/firefox/firefox'
    driver = webdriver.Firefox(options=opts)
    
    print("Navegando para Google...")
    driver.get('https://www.google.com')
    
    print(f"✓ Selenium funcionando! Título: {driver.title}")
    
    driver.quit()
    print("✓ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"✗ Erro: {e}")
    import traceback
    traceback.print_exc()
