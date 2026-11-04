import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def ejecutar_scraping():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    url = "https://listado.mercadolibre.com.co/laptops"
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    productos = soup.find_all('li', class_='ui-search-layout__item')
    datos = []

    for prod in productos:
        titulo_tag = prod.find('a', class_='poly-component__title') or prod.find('h3', class_='poly-component__title-wrapper')
        titulo = titulo_tag.text.strip() if titulo_tag else "No disponible"

        precio_tag = prod.find('span', class_='andes-money-amount__fraction')
        precio_texto = f"$ {precio_tag.text.strip()}" if precio_tag else "No disponible"
        precio_num = int(precio_tag.text.strip().replace('.', '')) if precio_tag else None

        vendedor_tag = prod.find('span', class_='poly-component__seller')
        vendedor = vendedor_tag.text.strip() if vendedor_tag else "No especificado"

        descuento_tag = prod.find('span', class_='poly-price__discount-polylabel')
        descuento = descuento_tag.text.strip() if descuento_tag else "Sin descuento"

        enlace_tag = prod.find('a', class_='poly-component__title')
        enlace = enlace_tag['href'].split('#')[0] if (enlace_tag and 'href' in enlace_tag.attrs) else "No disponible"

        datos.append({
            'Producto': titulo,
            'Precio': precio_texto,
            'Precio_Numerico': precio_num,
            'Vendedor': vendedor,
            'Descuento': descuento,
            'Enlace': enlace
        })

    df = pd.DataFrame(datos)
    return df

if __name__ == "__main__":
    df_resultados = ejecutar_scraping()
    print(f"Total registros extraidos: {len(df_resultados)}")
    df_resultados.to_csv("laptops_mercadolibre.csv", index=False, encoding='utf-8-sig')
