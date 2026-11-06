# Datos del ejercicio

Los CSV se generan al ejecutar los scripts y no se incluyen en Git por defecto.
GitHub Actions los publica como artefacto `datasets-libros` en las ejecuciones manuales exitosas.

| Archivo | Procedencia | Uso |
| --- | --- | --- |
| `libros_books_to_scrape.csv` | Catalogo extraido de https://books.toscrape.com/ | Practica de extraccion y limpieza; precios ficticios del sitio en GBP. |
| `ventas_simuladas.csv` | Generado por `generar_ventas.py` | Historico sintetico para futuros ejercicios de prediccion. Todas las filas llevan `Origen_Datos=SIMULADO`. |

El catalogo no contiene ventas historicas. El generador inventa unidades vendidas
con una semilla fija, tendencia, un componente periodico y un efecto de fin de semana.
Usa el precio del catalogo como precio fijo durante todo el periodo simulado.
Los ingresos calculados y las fechas no representan operaciones reales.

Valores por defecto: 180 dias desde 2025-01-01 y semilla 42. Una misma entrada,
orden de productos y parametros generan las mismas ventas. Si cambia el catalogo,
tambien puede cambiar la simulacion.
