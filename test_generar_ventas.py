from datetime import date

import pandas as pd
import pytest

from generar_ventas import generar_ventas


@pytest.fixture
def catalogo():
    return pd.DataFrame([{
        "Producto": "Libro de prueba",
        "Precio_Numerico": 19.99,
        "Moneda": "GBP",
        "Enlace": "https://books.toscrape.com/catalogue/prueba/index.html",
    }])


def test_ventas_reproducibles_marcadas_y_con_ingresos_coherentes(catalogo):
    primera = generar_ventas(catalogo, dias=7)
    pd.testing.assert_frame_equal(primera, generar_ventas(catalogo, dias=7))
    assert len(primera) == 7
    assert primera["Origen_Datos"].eq("SIMULADO").all()
    fechas = pd.date_range("2025-01-01", periods=7).strftime("%Y-%m-%d").tolist()
    assert primera["Fecha"].tolist() == fechas
    assert primera["Unidades_Vendidas"].ge(0).all()
    for fila in primera.to_dict("records"):
        assert fila["Ingresos_GBP"] == round(fila["Unidades_Vendidas"] * 19.99, 2)


def test_semilla_y_fecha_inicial_configurables(catalogo):
    primera = generar_ventas(catalogo, dias=7, semilla=1, inicio=date(2024, 2, 28))
    segunda = generar_ventas(catalogo, dias=7, semilla=2)
    assert not primera["Unidades_Vendidas"].equals(segunda["Unidades_Vendidas"])
    assert primera.iloc[1]["Fecha"] == "2024-02-29"


def test_rechaza_catalogo_vacio():
    with pytest.raises(ValueError, match="catalogo"):
        generar_ventas(pd.DataFrame())


def test_rechaza_dias_invalidos(catalogo):
    with pytest.raises(ValueError, match="dias"):
        generar_ventas(catalogo, dias=0)


def test_rechaza_mezcla_de_monedas(catalogo):
    catalogo.loc[0, "Moneda"] = "USD"
    with pytest.raises(ValueError, match="GBP"):
        generar_ventas(catalogo)
