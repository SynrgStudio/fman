# Review scope and validation

This independent snapshot is based on fman 1.7.6 (9ef5819), with the local
cleanup/navigation changes documented in CHANGELOG.md. The repository history
starts here: no upstream commits, signing material or publishing infrastructure
were imported.

## Validation baseline: Windows x64, Python 3.14

- 214 unit tests passed, including 15 cleanup/navigation/runtime/security regressions.
- 193 Core tests ran: 189 passed, 4 failed solely with WinError 1314 when creating
  symlinks without Developer Mode/elevation. These are not silently skipped.
- 69 integration tests passed. The harness keeps QApplication on the main thread.
- Total baseline: 476 tests run, 472 passed, 4 environment-blocked.
- Source smoke checks: two panels and local files, no registration/modal, no
  metrics files, clean exit; patched socket connects saw no startup attempts.
- Real arrow-key UI checks: Right enters folders, Left goes up, Right on files
  never launches them. No plugin suggestion dialogs.
- Standalone PyInstaller build and visible-window/clean-exit smoke passed.
- pip check passed. A dependency database scan of the reference environment
  reported no known vulnerabilities after updating pip; not a native-code audit.

These are local observations, not a security guarantee or a promise of all-green
CI on every platform. Symlink tests need privileges. Retest builds on clean
machines and review CI before release.

## Remaining limitations

- Only Windows x64 was validated. macOS/Linux native integration and packaging
  are not certified. The old optional pgi source dependency is not included.
- Python's legacy plugin loader uses deprecated load_module; Python 3.15 needs
  a separately tested migration. Use Python 3.14 for now.
- Qt5 and tinycss are aging dependencies. Security database checks do not fully
  cover bundled Qt libraries, native components, external 7-Zip or plugins.
- Plugins are not sandboxed. Basic ZIP traversal/symlink/size checks do not
  constitute a complete hostile-archive audit. All plugins/themes must be trusted.
- The build may warn about optional Windows API-set DLL names in winpty's native
  binaries. Additional manual testing of PTY/terminal behavior is needed.
- Clipboard, drag/drop, network shares, encrypted archives, cancellation and very
  large directories need further manual coverage. File-operation tests use temp
  fixtures, not personal data.
- A GPL-compliant binary release needs corresponding source and a reviewed
  component/notice inventory. No such binary release is part of this source push.
