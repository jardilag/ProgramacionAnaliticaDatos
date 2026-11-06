"""Pruebas sin red: HTML y respuestas HTTP controlados localmente."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

import scraper

HTML = """
<html><head><meta charset="utf-8"></head><body>
  <article class="product_pod">
    <p class="star-rating Three"></p>
    <h3><a href="catalogue/libro-de-prueba_1/index.html"
      title="Libro de prueba: edición completa">Libro de prueba...</a></h3>
    <p class="price_color">£19.99</p>
    <p class="instock availability"><i></i> In stock </p>
  </article>
</body></html>
"""
PAGINACION = '<li class="next"><a href="catalogue/page-2.html">next</a></li>'


def respuesta_html(html):
    respuesta = Mock()
    respuesta.content = html.encode("utf-8")
    return respuesta


def test_extrae_titulo_completo_precio_moneda_y_enlace():
    with patch("scraper.requests.get", return_value=respuesta_html(HTML)) as get:
        df = scraper.ejecutar_scraping()
    get.assert_called_once_with(scraper.URL_BASE, timeout=30)
    assert list(df.columns) == scraper.COLUMNAS
    assert len(df) == 1
    assert df.iloc[0].to_dict() == {
        "Producto": "Libro de prueba: edición completa",
        "Precio": "£19.99",
        "Precio_Numerico": 19.99,
        "Moneda": "GBP",
        "Disponibilidad": "In stock",
        "Calificacion": 3,
        "Enlace": "https://books.toscrape.com/catalogue/libro-de-prueba_1/index.html",
    }


def test_sigue_paginacion_y_detiene_al_final():
    primera = HTML.replace("</body>", PAGINACION + "</body>")
    segunda = HTML.replace("catalogue/libro-de-prueba_1", "otro-libro_2")
    with patch(
        "scraper.requests.get",
        side_effect=[respuesta_html(primera), respuesta_html(segunda)],
    ) as get:
        df = scraper.ejecutar_scraping(max_paginas=5, pausa=0)
    assert get.call_count == 2
    assert get.call_args_list[1].args[0] == "https://books.toscrape.com/catalogue/page-2.html"
    assert len(df) == 2
    assert df.iloc[1]["Enlace"] == "https://books.toscrape.com/catalogue/otro-libro_2/index.html"


def test_respeta_limite_de_paginas():
    html = HTML.replace("</body>", PAGINACION + "</body>")
    with patch("scraper.requests.get", return_value=respuesta_html(html)) as get:
        scraper.ejecutar_scraping(max_paginas=1)
    assert get.call_count == 1


def test_no_oculta_errores_http():
    respuesta = respuesta_html(HTML)
    respuesta.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
    with patch("scraper.requests.get", return_value=respuesta):
        with pytest.raises(requests.HTTPError, match="403"):
            scraper.ejecutar_scraping()


def test_pagina_sin_libros_falla():
    with patch("scraper.requests.get", return_value=respuesta_html("<h1>Acceso restringido</h1>")):
        with pytest.raises(RuntimeError, match="No se encontraron libros"):
            scraper.ejecutar_scraping()


@pytest.mark.parametrize("precio", ["USD 19.99", "£sin precio", "£-1.00", "£NaN"])
def test_rechaza_precios_invalidos(precio):
    html = HTML.replace("£19.99", precio)
    with patch("scraper.requests.get", return_value=respuesta_html(html)):
        with pytest.raises(ValueError):
            scraper.ejecutar_scraping()


def test_rechaza_limite_invalido_sin_consultar_la_red():
    with patch("scraper.requests.get") as get:
        with pytest.raises(ValueError):
            scraper.ejecutar_scraping(max_paginas=0)
    get.assert_not_called()


def test_cli_exporta_csv_con_acentos_y_precio(tmp_path):
    salida = tmp_path / "data" / "libros.csv"
    with patch("scraper.requests.get", return_value=respuesta_html(HTML)):
        scraper.main(["--salida", str(salida)])
    df = pd.read_csv(salida, encoding="utf-8-sig")
    assert df.iloc[0]["Precio_Numerico"] == 19.99
    assert df.iloc[0]["Producto"] == "Libro de prueba: edición completa"
