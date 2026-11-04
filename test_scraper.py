from unittest.mock import patch

from scraper import ejecutar_scraping
import scraper


def test_ejecucion_scraping_parsea_tarjetas_html():
    html = """
    <div class="poly-card">
      <a class="poly-component__title" href="https://mercadolibre.com.co/item#detalle">
        Laptop de prueba
      </a>
      <span class="andes-money-amount__fraction">1.999.000</span>
      <span class="poly-component__seller">Vendedor prueba</span>
      <span class="poly-price__discount-polylabel">10% OFF</span>
    </div>
    """

    class DriverFalso:
        page_source = html

        def execute_script(self, *_):
            return "complete"

        def get(self, *_):
            pass

        def quit(self):
            pass

    with patch("scraper.webdriver.Chrome", return_value=DriverFalso()), patch(
        "scraper.ChromeDriverManager.install", return_value="/tmp/chromedriver"
    ):
        df = ejecutar_scraping()

    assert len(df) == 1
    assert list(df.columns) == scraper.COLUMNAS
    assert df.iloc[0]["Producto"] == "Laptop de prueba"
    assert df.iloc[0]["Precio_Numerico"] == 1999000
