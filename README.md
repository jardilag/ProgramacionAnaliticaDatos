# Extraccion de libros y datos simulados para un ejercicio DevOps

El flujo actual obtiene el catalogo de [Books to Scrape](https://books.toscrape.com/)
con requests y BeautifulSoup, lo exporta a CSV y genera por separado un historico
de ventas **SIMULADAS**. No requiere Chrome, Selenium, cuentas ni tokens.

Books to Scrape es un sitio de demostracion para practicar scraping. Sus precios
y calificaciones son ficticios. El catalogo no es un historico de ventas y no
permite por si solo predecir ventas reales.

## Estructura

- `scraper.py`: descarga, parseo, paginacion y exportacion del catalogo.
- `generar_ventas.py`: generador reproducible de ventas sinteticas.
- `test_scraper.py` y `test_generar_ventas.py`: pruebas sin acceso a la red.
- `requirements.txt`: dependencias directas con versiones fijadas.
- `.github/workflows/main.yml`: CI en GitHub y extraccion manual en Windows.
- `data/README.md`: procedencia y limites de los datos.
- `Ruiz_Guzman_Edwin_Alberto_Analizando_EA1.ipynb`: referencia del ejercicio
  anterior de Mercado Libre. Conserva sus dependencias y rutas antiguas; el
  pipeline actual no lo ejecuta.

## Ejecucion local en Windows

Usa Python 3.10, la misma version configurada en CI:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe scraper.py
.\.venv\Scripts\python.exe generar_ventas.py
```

Se generan `data/libros_books_to_scrape.csv` y `data/ventas_simuladas.csv`.
Los CSV estan excluidos de Git; se regeneran con los scripts y se publican como
artefactos en las ejecuciones manuales exitosas.

Por defecto se descarga solo la primera pagina. Para obtener hasta tres paginas:

```powershell
.\.venv\Scripts\python.exe scraper.py --paginas 3
```

Hay una pausa de un segundo entre paginas y un timeout HTTP de 30 segundos.
La extraccion se detiene al llegar al limite o cuando no hay pagina siguiente.
Los errores HTTP, los precios invalidos y las paginas sin libros hacen fallar la
ejecucion; no se sustituyen por datos ficticios ni por resultados anteriores.

## Columnas del catalogo

| Columna | Contenido |
| --- | --- |
| Producto | Titulo completo del libro |
| Precio | Texto con el simbolo de libra |
| Precio_Numerico | Precio decimal |
| Moneda | GBP; no se convierte a pesos colombianos |
| Disponibilidad | Texto mostrado por el sitio |
| Calificacion | Estrellas de 1 a 5; vacio si no esta disponible |
| Enlace | URL absoluta del libro |

## Historico de ventas SIMULADAS

`generar_ventas.py` utiliza los productos y precios del catalogo e inventa las
unidades vendidas por dia. Cada fila contiene fecha, producto, enlace, unidades,
precio unitario, ingresos y `Origen_Datos=SIMULADO`.

Por defecto genera 180 dias desde 2025-01-01 con semilla 42. Con un catalogo de
20 libros se obtienen 3600 filas. La reproducibilidad depende de conservar el
mismo catalogo, su orden y los parametros.

```powershell
.\.venv\Scripts\python.exe generar_ventas.py --dias 365 --semilla 42 --inicio 2025-01-01
```

Los datos sirven para un ejercicio academico. No son ventas observadas de
Books to Scrape. El entrenamiento y la evaluacion de un modelo quedan pendientes.

## GitHub Actions

El workflow se llama **CI y scraping manual de libros**.

- Push a `main` o `feature/**`, y pull requests hacia `main`: ejecutan pytest
  en Ubuntu alojado por GitHub. Las pruebas no dependen del sitio externo.
- Ejecucion manual: primero ejecuta CI; si pasa, extrae el catalogo y genera
  ventas simuladas en el runner con etiquetas `self-hosted, Windows, X64`.
- El trabajo local tiene un limite de 15 minutos y publica ambos CSV en el
  artefacto **datasets-libros**.

Sube los cambios a tu repositorio. Con el runner local conectado, abre
**Actions → CI y scraping manual de libros → Run workflow**. El workflow debe
estar en la rama predeterminada para que aparezca el boton manual.

La configuracion de Python en Windows puede requerir iniciar el runner desde
una sesion que permita ejecutar los scripts de instalacion. El problema de
politica de PowerShell es independiente de la fuente de datos.

## Alcance DevOps actual

Este cambio cubre extraccion, datos simulados y pruebas en CI. Siguen pendientes
linting, modelo predictivo, contenedores, despliegue a staging, E2E, monitoreo,
logging centralizado, aprovisionamiento con IaC y demostracion de rollback.
