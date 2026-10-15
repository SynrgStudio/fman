# Contributing

Use Python 3.14 and an isolated virtual environment. See README.md for commands.
Run unit/Core/integration tests and the relevant smoke tests before submitting.
Do not fix a failing test by silently skipping it; describe environment limits.

Keep file operations, clipboard, plugins and native interop changes focused.
Use temporary fixtures, never personal files, in tests. No credentials, signing
material, generated executables, local environments or personal paths in commits.

New contributions are submitted under GPL-3.0-only. Preserve upstream MIT and
all third-party notices. Add an SPDX header to new Python files. Contribution
licensing does not change the original licenses of third-party portions.

Do not publish binaries without completing docs/licensing.md's checklist.
