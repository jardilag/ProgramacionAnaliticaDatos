"""Genera un historico SIMULADO; no representa ventas de Books to Scrape."""

import argparse
import math
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd

from scraper import ARCHIVO_CSV

ARCHIVO_VENTAS = Path("data/ventas_simuladas.csv")


def generar_ventas(catalogo, dias=180, semilla=42, inicio=date(2025, 1, 1)):
    """Simula unidades por libro con semilla fija, tendencia y estacionalidad."""
    requeridas = {"Producto", "Precio_Numerico", "Moneda", "Enlace"}
    if catalogo.empty or not requeridas.issubset(catalogo.columns):
        raise ValueError("Se necesita un catalogo no vacio con producto, precio, moneda y enlace.")
    if dias < 1:
        raise ValueError("dias debe ser mayor que cero.")
    if not catalogo["Moneda"].eq("GBP").all():
        raise ValueError("El catalogo debe usar GBP.")
    precios = [Decimal(str(precio)) for precio in catalogo["Precio_Numerico"]]
    if any(not precio.is_finite() or precio < 0 for precio in precios):
        raise ValueError("El catalogo contiene precios invalidos.")

    rng = random.Random(semilla)
    factores = [rng.uniform(0.5, 1.5) for _ in precios]
    productos = catalogo.to_dict("records")
    datos = []
    for dia in range(dias):
        fecha = inicio + timedelta(days=dia)
        demanda = 7 + dia * 0.02 + 2 * math.sin(2 * math.pi * dia / 30)
        if fecha.weekday() >= 5:
            demanda += 2
        for producto, precio, factor in zip(productos, precios, factores):
            unidades = max(0, round(rng.gauss(demanda * factor, 2)))
            datos.append({
                "Fecha": fecha.isoformat(),
                "Producto": producto["Producto"],
                "Enlace": producto["Enlace"],
                "Unidades_Vendidas": unidades,
                "Precio_Unitario_GBP": float(precio),
                "Ingresos_GBP": float((precio * unidades).quantize(Decimal("0.01"))),
                "Origen_Datos": "SIMULADO",
            })
    return pd.DataFrame(datos)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogo", type=Path, default=ARCHIVO_CSV)
    parser.add_argument("--salida", type=Path, default=ARCHIVO_VENTAS)
    parser.add_argument("--dias", type=int, default=180)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--inicio", type=date.fromisoformat, default=date(2025, 1, 1))
    argumentos = parser.parse_args(argv)
    catalogo = pd.read_csv(argumentos.catalogo, encoding="utf-8-sig")
    ventas = generar_ventas(catalogo, argumentos.dias, argumentos.semilla, argumentos.inicio)
    argumentos.salida.parent.mkdir(parents=True, exist_ok=True)
    ventas.to_csv(argumentos.salida, index=False, encoding="utf-8-sig")
    print(f"Se generaron {len(ventas)} filas de ventas SIMULADAS.")
    print(f"CSV guardado en: {argumentos.salida.resolve()}")


if __name__ == "__main__":
    main()
