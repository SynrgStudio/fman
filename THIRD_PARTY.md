# Third-party software and notices

Original application source: fman 1.7.6 by Michael Herrmann, MIT.
See NOTICE and LICENSES/fman-MIT.txt. New project contributions: GPL-3.0-only.

## Runtime dependencies (Windows reference environment)

| Component | Version | Declared licensing / notices |
| --- | --- | --- |
| Python | 3.14 | PSF license and included third-party notices |
| PyQt5 | 5.15.11 | GPLv3 (public package); separate commercial option from Riverbank |
| PyQt5-Qt5 | 5.15.2 | LGPLv3 as declared by the wheel; review individual Qt components |
| PyQt5_sip | 12.20.0 | BSD-2-Clause |
| tinycss | 0.4 | BSD |
| requests | 2.34.2 | Apache-2.0; preserve its NOTICE |
| urllib3 | 2.8.0 | MIT |
| certifi | 2026.7.22 | MPL-2.0 |
| charset-normalizer | 3.5.2 | MIT |
| idna | 3.20 | BSD-3-Clause |
| Send2Trash | 1.8.3 | BSD |
| pywin32 | 312 | PSF and included component notices |
| pywinpty | 3.0.5 | MIT and notices for bundled native components |

The traceback formatting helper also adapts Python standard-library code;
Python's license and notices are retained in LICENSES/Python-notices.txt.

Build tooling includes PyInstaller (GPL with bootloader exception), its hook
collection, altgraph, pefile, pywin32-ctypes, packaging and setuptools. These have
independent license terms. Python and Qt also contain third-party code beyond
this summary. Non-Windows requirements include osxtrash/pyobjc or distro.

This is a reference inventory, not a substitute for inspecting the actual
binary payload. `requirements/windows-build.lock.txt` pins the tested Python
packages; it is not a cross-platform lock or a complete native SBOM.

## Resources

Open Sans.ttf and Roboto Bold.ttf declare Apache License 2.0 in their embedded
name tables. Copyright attribution is in NOTICE; full license in
LICENSES/Apache-2.0.txt. Other upstream icons/resources are retained under the
upstream grant unless accompanied by more specific notices.

The historical upstream notices are kept in
LICENSES/upstream-third-party-notices.txt for attribution only. They mention
outdated versions and formerly bundled tools; they are not the current bill
of materials. No historical 7-Zip/p7zip executables are included. Users install
a maintained 7-Zip separately; this repository does not redistribute it.

## Local executable builds

The build copies project notices and generates `dependency-notices/` with
available license files and package metadata from the build environment.
A missing notice is reported in that inventory; it is NOT permission to omit
third-party compliance. PyQt5 wheels do not themselves provide all needed
corresponding source or license materials. See docs/licensing.md before sharing
executables. No binary release is prepared or published by this source push.
