# Core plugin

Core implements file operations, navigation, archives and default shortcuts for
fman Clean. It is loaded by the same plugin mechanism used for user plugins.

- `Key Bindings*.json`: default and platform-specific shortcuts.
- `Theme*.css`: appearance.
- `Core Settings*.json`: settings and archive handlers.
- `core/commands`: commands, including built-in arrow navigation.
- `core/fs`: local files and archive backends using an external 7-Zip.
- `core/tests`: temporary-fixture regression tests; excluded from local executables.

Plugin API implementation: `src/main/python/fman/__init__.py` and `fs.py` in the
repository. Third-party plugins run with full user privileges, not in a sandbox.

Based on the original fman Core by Michael Herrmann (MIT). New SynrgStudio
contributions and this modified project as a whole are GPLv3. See the repository
LICENSE, NOTICE and LICENSES/fman-MIT.txt; third-party components retain their terms.
