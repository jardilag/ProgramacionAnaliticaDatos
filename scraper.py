import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

COLUMNAS = [
    "Producto",
    "Precio",
    "Precio_Numerico",
    "Vendedor",
    "Descuento",
    "Enlace",
]


def _dataframe_desde_api():
    respuesta = requests.get(
        "https://api.mercadolibre.com/sites/MCO/search",
        params={"q": "laptops", "limit": 50},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    respuesta.raise_for_status()
    resultados = respuesta.json().get("results", [])
    datos = []

    for producto in resultados:
        precio = producto.get("price")
        precio_original = producto.get("original_price")
        descuento = "Sin descuento"
        if precio_original and precio and precio_original > precio:
            descuento = f"{round((1 - precio / precio_original) * 100)}% OFF"

        datos.append(
            {
                "Producto": producto.get("title", "No disponible"),
                "Precio": f"$ {precio:,.0f}".replace(",", ".")
                if precio is not None
                else "No disponible",
                "Precio_Numerico": precio,
                "Vendedor": producto.get("seller", {}).get(
                    "nickname", "No especificado"
                ),
                "Descuento": descuento,
                "Enlace": producto.get("permalink", "No disponible"),
            }
        )

    return pd.DataFrame(datos, columns=COLUMNAS)


def ejecutar_scraping():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.get("https://listado.mercadolibre.com.co/laptops")
        WebDriverWait(driver, 20).until(
            lambda navegador: navegador.execute_script(
                "return document.readyState"
            )
            == "complete"
        )
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()

    productos = soup.select("li.ui-search-layout__item, div.poly-card")
    datos = []

    for prod in productos:
        titulo_tag = prod.select_one(
            "a.poly-component__title, h3.poly-component__title-wrapper"
        )
        titulo = titulo_tag.text.strip() if titulo_tag else "No disponible"

        precio_tag = prod.select_one("span.andes-money-amount__fraction")
        precio_texto = (
            f"$ {precio_tag.text.strip()}" if precio_tag else "No disponible"
        )

        precio_num = None
        if precio_tag:
            try:
                precio_num = int(precio_tag.text.strip().replace(".", ""))
            except ValueError:
                precio_num = None

        vendedor_tag = prod.select_one("span.poly-component__seller")
        vendedor = (
            vendedor_tag.text.strip() if vendedor_tag else "No especificado"
        )

        descuento_tag = prod.select_one("span.poly-price__discount-polylabel")
        descuento = (
            descuento_tag.text.strip() if descuento_tag else "Sin descuento"
        )

        enlace_tag = prod.select_one("a.poly-component__title")
        enlace = (
            enlace_tag["href"].split("#")[0]
            if enlace_tag and enlace_tag.get("href")
            else "No disponible"
        )

        datos.append({
            "Producto": titulo,
            "Precio": precio_texto,
            "Precio_Numerico": precio_num,
            "Vendedor": vendedor,
            "Descuento": descuento,
            "Enlace": enlace,
        })

    if datos:
        return pd.DataFrame(datos, columns=COLUMNAS)

    # Mercado Libre puede mostrar una página anti-bot sin tarjetas HTML.
    return _dataframe_desde_api()

if __name__ == "__main__":
    df_resultados = ejecutar_scraping()
    print(f"Total registros extraidos: {len(df_resultados)}")
    df_resultados.to_csv(
        "laptops_mercadolibre.csv", index=False, encoding="utf-8-sig"
    )
