# Búsqueda unificada en Windows

Ctrl+P abre una sola paleta; los comandos legacy `go_to` y `command_palette`
redirigen al mismo lugar. Ctrl+Shift+P ya no tiene un buscador separado.

- Entrada normal: comandos, ubicaciones recientes, rutas escritas, coincidencias
  en la carpeta actual y, opcionalmente, nombres/rutas del índice Everything.
- `>`: solo comandos. No consulta discos ni Everything.
- Tab: completar una carpeta sugerida. Enter: ejecutar el comando o navegar a la
  ruta seleccionada. Los archivos se revelan en su carpeta, no se ejecutan.
- No se busca contenido de documentos, no se indexan discos desde fman y no se
  lanza una búsqueda recursiva por todo el disco como fallback.

## Proveedores y concurrencia

El catálogo de comandos es local. Las operaciones de archivos/índice se hacen
fuera del hilo Qt. Los resultados locales se muestran antes de esperar al índice.
Hay un debounce de 150 ms, un trabajo activo y uno pendiente reemplazable; las
respuestas de generaciones anteriores se ignoran. La navegación explícita del
usuario por la lista se conserva al añadir resultados del índice.

Las sugerencias de directorio se limitan a 500 entradas inspeccionadas y 50 rutas
mostradas. No es una búsqueda exhaustiva sin Everything. Las rutas de red o un
sistema de archivos que no responde aún pueden demorar al proveedor local, pero
no deberían bloquear el hilo de la interfaz. No se promete cancelar llamadas
bloqueadas del sistema de archivos en un hilo Python.

## Everything

La integración usa el SDK x64 vía IPC local con el cliente Everything que ya
esté ejecutándose. El programa conserva y actualiza su propio índice. No usa
Windows Search ni lee el archivo de base de datos directamente.

Se solicitan solo nombres/rutas y tipo carpeta/archivo. El buscador global usa
la sintaxis de consulta de Everything, por ejemplo `*.stl`; no interpreta nada
como comando de shell. Las rutas locales usan coincidencia flexible.

La DLL nativa se carga únicamente en un helper separado con límite de 4 segundos;
una DLL seleccionada por el usuario es código de confianza, no datos inofensivos.
El helper comunica resultados por un archivo temporal privado y se termina si
vence el timeout. Tiene además un watchdog de 6 segundos por si la aplicación
principal ya salió. No abre puertos, no usa HTTP y fman no se eleva para consultar.

El conector se instala solo al ejecutar explícitamente `tools/setup_everything.py`.
Se descarga el SDK oficial por HTTPS y se valida un SHA-256 fijado para el archivo
revisado. Si cambia, la instalación falla hasta revisar la nueva versión; no se
omite el hash. La DLL no se incorpora al repositorio ni al ejecutable generado.
Su licencia MIT (David Carpenter) está en LICENSES/Everything-SDK-MIT.txt y se
copia junto a la instalación local del conector. Everything como aplicación
externa conserva sus propios términos.

Prueba opcional del índice real (Everything debe estar abierto):

```powershell
.\.venv\Scripts\python.exe tests/everything_smoke.py
.\.venv\Scripts\python.exe tests/everything_smoke.py --frozen
```

No forma parte de CI: las demás pruebas sustituyen el proveedor para ser
reproducibles sin indexar archivos del runner ni instalar componentes nativos.
