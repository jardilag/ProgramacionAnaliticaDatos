import os
import pandas as pd
from scraper import ejecutar_scraping

def test_ejecucion_scraping():
    df = ejecutar_scraping()
    assert not df.empty, "El DataFrame resultado esta vacio."
    assert len(df) >= 10, f"Se esperaban al menos 10 registros, se obtuvieron {len(df)}"
    
    columnas_esperadas = ['Producto', 'Precio', 'Precio_Numerico', 'Vendedor', 'Descuento', 'Enlace']
    for col in columnas_esperadas:
        assert col in df.columns, f"La columna {col} no se encuentra en el DataFrame."
