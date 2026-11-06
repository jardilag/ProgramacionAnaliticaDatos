"""Extrae el catalogo de demostracion de Books to Scrape."""

import argparse
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL_BASE = "https://books.toscrape.com/"
ARCHIVO_CSV = Path("data/libros_books_to_scrape.csv")
COLUMNAS = [
    "Producto", "Precio", "Precio_Numerico", "Moneda",
    "Disponibilidad", "Calificacion", "Enlace",
]
CALIFICACIONES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def _extraer_producto(tarjeta, url_pagina):
    titulo = tarjeta.select_one("h3 a")
    precio = tarjeta.select_one(".price_color")
    disponibilidad = tarjeta.select_one(".availability")
    calificacion = tarjeta.select_one(".star-rating")
    if titulo is None or precio is None or not titulo.get("href"):
        raise ValueError("Tarjeta de libro sin titulo, precio o enlace.")

    precio_texto = precio.get_text(strip=True)
    if not precio_texto.startswith("£"):
        raise ValueError(f"Moneda inesperada: {precio_texto!r}")
    try:
        precio_numero = Decimal(precio_texto[1:])
    except InvalidOperation as error:
        raise ValueError(f"Precio invalido: {precio_texto!r}") from error
    if not precio_numero.is_finite() or precio_numero < 0:
        raise ValueError(f"Precio invalido: {precio_texto!r}")

    estrellas = None
    if calificacion is not None:
        estrellas = next(
            (
                CALIFICACIONES[clase]
                for clase in calificacion.get("class", [])
                if clase in CALIFICACIONES
            ),
            None,
        )

    return {
        "Producto": titulo.get("title") or titulo.get_text(strip=True),
        "Precio": precio_texto,
        "Precio_Numerico": float(precio_numero),
        "Moneda": "GBP",
        "Disponibilidad": (
            disponibilidad.get_text(" ", strip=True)
            if disponibilidad is not None else "No disponible"
        ),
        "Calificacion": estrellas,
        "Enlace": urljoin(url_pagina, titulo["href"]),
    }


def ejecutar_scraping(max_paginas=1, pausa=1.0):
    """Descarga hasta max_paginas y falla si la fuente no devuelve libros."""
    if max_paginas < 1:
        raise ValueError("max_paginas debe ser mayor que cero.")
    if pausa < 0:
        raise ValueError("pausa no puede ser negativa.")

    datos = []
    url = URL_BASE
    for pagina in range(max_paginas):
        respuesta = requests.get(url, timeout=30)
        respuesta.raise_for_status()
        # Los bytes conservan la codificacion declarada en el HTML.
        soup = BeautifulSoup(respuesta.content, "html.parser")
        tarjetas = soup.select("article.product_pod")
        if not tarjetas:
            raise RuntimeError(f"No se encontraron libros en {url}.")
        datos.extend(_extraer_producto(tarjeta, url) for tarjeta in tarjetas)

        siguiente = soup.select_one("li.next a")
        if siguiente is None or not siguiente.get("href") or pagina + 1 >= max_paginas:
            break
        url = urljoin(url, siguiente["href"])
        if pausa:
            time.sleep(pausa)

    return pd.DataFrame(datos, columns=COLUMNAS).drop_duplicates(
        subset="Enlace", ignore_index=True
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paginas", type=int, default=1)
    parser.add_argument("--salida", type=Path, default=ARCHIVO_CSV)
    argumentos = parser.parse_args(argv)
    if argumentos.paginas < 1:
        parser.error("--paginas debe ser mayor que cero")
    resultados = ejecutar_scraping(max_paginas=argumentos.paginas)
    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    resultados.to_csv(argumentos.salida, index=False, encoding="utf-8-sig")
    print(f"Se extrajeron {len(resultados)} libros de {URL_BASE}")
    print(f"CSV guardado en: {argumentos.salida.resolve()}")
    print("Catalogo de demostracion: precios ficticios; no son ventas.")


if __name__ == "__main__":
    main()
