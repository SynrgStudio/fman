# fman Clean · Windows

Administrador de archivos de doble panel para **Windows x64**, mantenido por
SynrgStudio. Basado en fman de Michael Herrmann; proyecto independiente, no oficial.

**GPLv3** para el proyecto modificado. El código base conserva MIT y sus créditos.
Ver [NOTICE](NOTICE), [licencias](docs/licensing.md) y [terceros](THIRD_PARTY.md).

## Atajos

| Atajo | Acción |
| --- | --- |
| Flechas ↑ / ↓ | Recorrer archivos |
| Flechas ← / → | Subir de carpeta / entrar en carpeta (no ejecutar archivos) |
| Enter | Abrir archivo |
| Tab | Cambiar de panel |
| **F5 / F6** | Copiar / mover directamente al otro panel |
| **Ctrl+C / X / V** | Copiar / cortar / pegar con portapapeles |
| **Ctrl+P** | Buscar carpetas, archivos y comandos en un solo lugar |
| **Ctrl+,** | Panel de configuración |
| **F3** | Preview en el panel opuesto; navegar actualiza el contenido |
| Escape | Cerrar el panel auxiliar o filtro |
| Ctrl+. | Mostrar/ocultar archivos ocultos |
| Shift+F6 / F7 | Renombrar / crear carpeta |

En `Ctrl+P`, escribir `>` limita a comandos; por ejemplo `> compress`.
Las rutas recientes/locales y los resultados de Everything aparecen como carpetas
u archivos, separados visualmente de los comandos. Un resultado de archivo se
**revela y selecciona en su carpeta**, sin ejecutar nada. Tab completa rutas.
Comprimir también está en el menú contextual; el atajo Alt+F5 sigue disponible.

Configuración reúne fuente/tamaño, ocultos, fila de navegación `..`, editor,
terminal y conector Everything. Los paneles de configuración y preview son
mutuamente excluyentes; nunca destruyen la segunda carpeta ni alteran el destino
real de F5/F6. `..` es una fila de navegación independiente: no se puede copiar,
borrar ni seleccionar como archivo y no la ocultan los filtros.

Preview inicial: texto plano, PNG/JPG/GIF/BMP/WEBP/ICO y estadísticas no recursivas
de carpetas. Lectura en segundo plano, con límites de bytes/píxeles/entradas.
PDF, SVG y AVIF **no están implementados** en esta versión. Sin editor de temas
ni undo/redo. No hay promesa de recuperar borrados o sobrescrituras.

## Ejecutar

Requisitos: **Windows x64, Python 3.14 x64**. Desde el repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/windows.txt
.\.venv\Scripts\python.exe build.py run
```

Después puede usarse `run-clean.cmd`. Para reproducir el entorno de desarrollo y
build: `requirements/windows-build.lock.txt`. macOS/Linux no son objetivos de
este proyecto; quedan algunos componentes heredados, sin soporte ni validación.

7-Zip actualizado, instalado aparte, es necesario para ZIP/7z/tar y extraer
plugins. Se detecta `Program Files/7-Zip/7z.exe` o un ejecutable en PATH;
`FMAN_7ZIP` permite elegir otro de confianza. No se incluyen binarios antiguos.

## Everything opcional

Se consulta el índice de **Everything de voidtools**, no Windows Search ni un
caché del Explorador. Everything debe estar instalado y ejecutándose en segundo
plano. Para instalar explícitamente su conector SDK x64 oficial:

```powershell
.\.venv\Scripts\python.exe tools/setup_everything.py
```

El script valida el hash del archivo oficial y coloca únicamente la DLL y su
licencia en `%LOCALAPPDATA%/fman-clean/tools/everything/`, fuera del repositorio.
No descarga nada al arrancar. No instala Everything ni pide elevar fman.
También puede elegirse una DLL SDK de confianza desde configuración.

Sin Everything o sin conector, Ctrl+P conserva comandos, recientes y rutas
locales sin ventanas de error. Consultas con debounce, trabajo pendiente acotado,
respuestas viejas descartadas y helper nativo con timeout. No usamos HTTP ni
leemos `Everything.db`. Ver [detalles de búsqueda](docs/search.md).

## Pruebas y build local

```powershell
.\.venv\Scripts\python.exe build.py test
.\.venv\Scripts\python.exe tests/smoke.py
.\.venv\Scripts\python.exe tests/navigation_smoke.py
.\.venv\Scripts\python.exe tests/windows_features_smoke.py
.\.venv\Scripts\python.exe -m pip install -r requirements/build.txt
.\.venv\Scripts\python.exe build.py freeze
.\.venv\Scripts\python.exe tests/frozen_smoke.py
```

Salida: `target/fman-clean/fman-clean.exe`, junto a `_internal`.
Las pruebas de symlinks requieren privilegios o Modo desarrollador; no cambiamos
esa política en tu máquina. CI la habilita solo en el runner descartable.

El build incluye avisos e inventario del entorno, pero **no completa por sí solo
las obligaciones de distribuir fuentes correspondientes** de los binarios GPL.
Este repositorio publica fuentes, no un instalador listo para redistribución.
Consultar [guía de distribución](docs/licensing.md).

## Seguridad

Sin registro, pantallas de compra, sugerencias de plugins al navegar, telemetría
remota, identificadores ni envío de errores. Configuración independiente en
`fman-clean`, sin modificar instalaciones del fman original.

Los plugins y las DLL/herramientas elegidas ejecutan código con los permisos del
usuario: **no son un sandbox**. Los límites de preview y de archivos de plugins
no equivalen a una auditoría completa. Ver [SECURITY.md](SECURITY.md) y
[alcance de pruebas](docs/review.md).
