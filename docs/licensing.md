# Licencias y distribucion

## Alcance

El proyecto modificado como conjunto y las nuevas contribuciones de SynrgStudio
se ofrecen bajo **GNU General Public License version 3 solamente**
(`GPL-3.0-only`). El texto completo esta en `LICENSE`. No se da garantia.

El fman original es copyright (c) 2026 Michael Herrmann y esta bajo MIT.
`LICENSES/fman-MIT.txt` conserva literalmente su permiso y descargo. La licencia
GPL de este proyecto no elimina la concesion MIT sobre las partes originales.
`NOTICE` identifica procedencia, cambios de titularidad por contribucion y
fuentes tipograficas. Ninguna licencia implica patrocinio o derechos de marca.

Los archivos Python modificados o nuevos llevan una cabecera GPL y, cuando
corresponde, una referencia al codigo original MIT. Las partes upstream no
modificadas siguen cubiertas por la atribucion MIT anterior. Los demas formatos
se rigen por estas indicaciones de procedencia y las excepciones documentadas.

## PyQt5 y Qt

Se mantiene PyQt5. Sus paquetes publicos se distribuyen bajo GPLv3; no se afirma
que este ejecutable sea MIT-only. El paquete PyQt5-Qt5 declara LGPLv3 para sus
bibliotecas Qt; componentes particulares y dependencias tienen sus propios
avisos. Las licencias GPLv3/LGPLv3 de referencia estan en `LICENSES`.

Las dependencias no se revenden ni sublicencian como si fueran todas GPL o MIT.
Ver `THIRD_PARTY.md`, sus paquetes fuente y los avisos del entorno de build.
Las fuentes Open Sans y Roboto incluidas declaran Apache-2.0 en su metadata.

## Publicacion de fuentes

Este repositorio contiene el codigo fuente mantenido aqui, scripts y pruebas;
no contiene entornos Python, wheels, instaladores ni el historial original.
Los requisitos se descargan separadamente desde PyPI al instalarlos.

La copia historica `LICENSES/upstream-third-party-notices.txt` se conserva para
no perder atribuciones; sus versiones antiguas y ofertas de fuente/contacto no
son una descripcion vigente de esta distribucion ni una promesa de terceros.

## Antes de publicar binarios

1. Usar un entorno limpio y registrar versiones exactas de Python, librerias,
   Qt, plugins Qt y demas componentes efectivamente empaquetados.
2. Incluir `LICENSE`, `NOTICE`, `THIRD_PARTY.md` y los textos/avisos aplicables.
   `tools/collect_licenses.py` recopila archivos de licencia e inventario de los
   paquetes del entorno, pero requiere revision humana.
3. Preparar y ofrecer el **codigo fuente correspondiente** de lo distribuido,
   con scripts de construccion y modificaciones, conforme a GPLv3 seccion 6.
   Un enlace a nuestro repositorio no cubre por si solo el fuente de Python,
   PyQt5, Qt ni otros componentes incorporados. Reunir el fuente exacto y las
   condiciones LGPL pertinentes, incluidas las relativas a sustitucion/enlace.
4. Verificar tambien condiciones de bibliotecas nativas, certificados CA,
   fuentes y herramientas. PyInstaller tiene excepcion para su bootloader,
   pero esa excepcion no anula las licencias de las librerias empaquetadas.
5. Validar en otra maquina. No usar claves/certificados del proyecto base.

No se publica automaticamente ningun binario mediante CI. El primer push es
solo de fuentes. Esta guia tecnica no sustituye asesoramiento juridico.
