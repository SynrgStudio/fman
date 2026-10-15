# fman Clean

Administrador de archivos de doble panel, centrado en teclado y extensible con
plugins Python. Mantenido por **SynrgStudio**, basado en fman de Michael Herrmann.
Proyecto independiente: no es una version oficial del autor original.

**Licencia del proyecto: GPLv3.** El codigo base conserva su licencia MIT y sus
creditos. Ver [NOTICE](NOTICE), [licencias](docs/licensing.md) y
[componentes de terceros](THIRD_PARTY.md).

## Que cambia

- Sin registro, pantallas de compra ni sugerencias de instalar plugins al navegar.
- Sin telemetria remota, identificadores de usuario ni envio de errores.
- Flechas integradas: **arriba/abajo** seleccionan, **izquierda** sube de carpeta,
  **derecha** entra en una carpeta. Derecha nunca ejecuta archivos; **Enter** abre.
- **Tab** cambia de panel; **Ctrl+P** busca ubicaciones;
  **Ctrl+Shift+P** abre la paleta de comandos (Windows).
- Copiar/mover/renombrar, papelera, ZIP/7z/tar, temas y plugins.
- Build local sin fbs Pro, servidores del autor ni credenciales de publicacion.
- Configuracion independiente en `fman-clean`; no modifica instalaciones de fman.

## Ejecutar en Windows

Requisito: **Python 3.14 x64**. Desde la carpeta del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements/windows.txt
.\.venv\Scripts\python.exe build.py run
```

Despues se puede usar `run-clean.cmd`.
Para reproducir el entorno Windows de desarrollo/build, en lugar de los
requisitos anteriores se puede instalar `requirements/windows-build.lock.txt`.

Para archivos comprimidos e instalacion de plugins se necesita un **7-Zip
actualizado**, instalado aparte. Se detecta `Program Files/7-Zip/7z.exe`, o
`7zz`/`7z`/`7za` en PATH. `FMAN_7ZIP` permite elegir otro ejecutable de confianza.
No incluimos ni descargamos automaticamente herramientas de compresion.

macOS/Linux tienen requisitos en `requirements/mac.txt` y `requirements/linux.txt`,
pero esta version solo fue validada en Windows x64. Los iconos GTK son opcionales;
si no esta disponible su integracion se usa el proveedor de iconos de Qt.

## Pruebas y build

```powershell
.\.venv\Scripts\python.exe build.py test
.\.venv\Scripts\python.exe tests/smoke.py
.\.venv\Scripts\python.exe tests/navigation_smoke.py
.\.venv\Scripts\python.exe -m pip install -r requirements/build.txt
.\.venv\Scripts\python.exe build.py freeze
.\.venv\Scripts\python.exe tests/frozen_smoke.py
```

Salida local: `target/fman-clean/fman-clean.exe` junto a su carpeta `_internal`.
No se necesita administrador para navegar; crear symlinks y sus pruebas puede
requerir privilegios o Modo desarrollador. No cambiamos esa politica local.

El build incluye un inventario y avisos de las dependencias instaladas. Eso no
sustituye las obligaciones de proporcionar el codigo fuente correspondiente
al distribuir binarios GPL. Este repositorio publica **fuentes**, no un release
binario listo para redistribucion. Ver [guia de distribucion](docs/licensing.md).

## Seguridad y limites

Los plugins ejecutan Python con todos los permisos del usuario: **no son un
sandbox**. La instalacion pide confirmacion y valida limites/rutas basicos.
No instalar plugins o temas que no sean de confianza.

Ayuda y descargas solicitadas por el usuario pueden usar red. El arranque
probado no realizo conexiones de sockets; no se promete que todas las funciones
sean offline. Consultar [revision](docs/review.md) y [seguridad](SECURITY.md).

## Estructura

- `src/main`: aplicacion y recursos.
- `src/unittest`, `src/integrationtest`, `tests`: pruebas y smoke tests.
- `build.py`, `tools`: comandos locales y avisos de dependencias.
- `requirements`: dependencias por plataforma y lock Windows.
- `LICENSES`, `NOTICE`, `THIRD_PARTY.md`: licencias y atribuciones.
