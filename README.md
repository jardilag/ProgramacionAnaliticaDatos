# Análisis de scraping de laptops en Mercado Libre

## Descripción general
Este repositorio contiene un notebook de Jupyter con un ejercicio de scraping sobre el listado de laptops en Mercado Libre Colombia.

Archivo principal:
- `Ruiz_Guzman_Edwin_Alberto_Analizando_EA1.ipynb`

## Objetivo del análisis
Extraer información de productos publicados en `https://listado.mercadolibre.com.co/laptops`, estructurarla en un `DataFrame` y exportarla a CSV para su revisión.

## Fuente y alcance de los datos
- **Fuente**: página pública de resultados de búsqueda de Mercado Libre Colombia para laptops.
- **URL trabajada**: `https://listado.mercadolibre.com.co/laptops`.
- **Alcance en la ejecución mostrada**: se detectan y procesan todos los productos encontrados en la página cargada en ese momento (60 registros en la salida del notebook).

## Herramientas y bibliotecas utilizadas
Según el notebook, se usan estas bibliotecas y herramientas:
- `selenium`
- `webdriver_manager` (ChromeDriver)
- `BeautifulSoup` (`bs4`)
- `pandas`
- `requests`
- `subprocess`
- `os`
- `time`

También se ejecuta una prueba con `scrapy` mediante `subprocess.run`.

## Proceso de extracción y limpieza
1. Configuración de Chrome con Selenium y opciones para reducir señales de automatización.
2. Carga de la URL de laptops y espera de 10 segundos.
3. Parseo del HTML con BeautifulSoup.
4. Selección de productos usando `li.ui-search-layout__item`.
5. Extracción de campos por producto.
6. Limpieza y transformación:
   - Conversión del precio a texto (`Precio`) y a entero (`Precio_Numerico`) removiendo separadores de miles.
   - Asignación de valores por defecto cuando no hay dato (`No disponible`, `No especificado`, `Sin descuento`).
   - Limpieza de enlaces removiendo fragmentos (`split('#')[0]`).
7. Construcción de `DataFrame` y exportación a CSV.

## Variables/campos analizados
El dataset generado incluye las columnas:
- `Producto`
- `Precio`
- `Precio_Numerico`
- `Vendedor`
- `Descuento`
- `Enlace`

## Resultados observados en el notebook
- Se imprime `Productos encontrados: 60`.
- Se reporta `Se extrajeron 60 registros`.
- Se visualiza una tabla con columnas de producto, precio, vendedor y descuento.
- El CSV se guarda como `laptops_mercadolibre.csv` en el escritorio del entorno donde se ejecuta el notebook.

## Pruebas adicionales incluidas en el notebook
- **Prueba con `requests`**: se imprime el tamaño de la respuesta y `False` para la presencia de `ui-search-layout`, lo que sugiere que la respuesta no trae el mismo contenido esperado para parseo directo.
- **Prueba con `scrapy`**: se intenta ejecutar un spider (`laptops`) y el notebook contempla el caso de que no se genere CSV, indicando bloqueo.

## Cómo reproducir el notebook
1. Abrir el archivo `Ruiz_Guzman_Edwin_Alberto_Analizando_EA1.ipynb` en Jupyter.
2. Instalar dependencias necesarias (por ejemplo, en un entorno virtual):

```bash
pip install pandas selenium webdriver-manager beautifulsoup4 requests scrapy
```

3. Ejecutar las celdas en orden.
4. Verificar la salida en consola y el archivo CSV exportado.

## Consideraciones y limitaciones
- El scraping depende de la estructura HTML actual del sitio; cambios en clases o etiquetas pueden romper la extracción.
- Los resultados pueden variar por fecha, sesión, ubicación o contenido dinámico de la plataforma.
- El notebook evidencia diferencias entre enfoques (`requests`, `scrapy`, Selenium) frente a mecanismos anti-bot del sitio.
- La ruta de exportación del CSV y la ruta del proyecto Scrapy están definidas de forma local y pueden requerir ajuste en otro equipo.
