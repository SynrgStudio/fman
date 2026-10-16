# Review scope and validation

This independent snapshot is based on fman 1.7.6 (9ef5819), with the local
cleanup/navigation changes documented in CHANGELOG.md. The repository history
starts here: no upstream commits, signing material or publishing infrastructure
were imported.

## Validation baseline: Windows x64, Python 3.14

- 248 unit tests passed, including 49 cleanup/navigation/runtime/security/Windows regressions.
- 193 Core tests ran: 189 passed, 4 failed solely with WinError 1314 when creating
  symlinks without Developer Mode/elevation. These are not silently skipped.
- 69 integration tests passed. The harness keeps QApplication on the main thread.
- Total: 510 tests run, 506 passed, 4 environment-blocked locally.
- Source smoke checks: two panels and local files, no registration/modal, no
  metrics files, clean exit; patched socket connects saw no startup attempts.
- Real arrow-key UI checks: Right enters folders, Left goes up, Right on files
  never launches them. No plugin suggestion dialogs.
- Windows feature UI smoke: real Ctrl+P, command/path results, stale response
  rejection, settings persistence, exclusive panels, live text/image preview,
  filter-immune parent navigation, Tab restoration and F5 copy with preview open.
- An empty/unavailable clipboard is handled as no file data, including while
  enumerating palette commands. Both the Windows native and Qt offscreen widget
  smoke checks passed locally. CI widget smoke uses Qt offscreen on Windows to
  avoid relying on an interactive desktop; native window/exit checks run locally.
- Image fitting is checked for portrait/landscape/zero/small sizes and actual
  window/splitter resizing. Preview Ctrl+Shift+C copies original-resolution pixels
  or displayed text, never URLs; regular Ctrl+C still copies files. Stale/loading
  and closed-preview copy attempts leave the clipboard unchanged.
- An optional native clipboard check also verifies Windows DIB/DIBV5/Unicode text
  availability and absence of CF_HDROP for content copies; it restores the prior
  clipboard if the test still owns it. Default/CI checks use isolated offscreen
  clipboard data and never inspect the user's clipboard.
- Live Everything IPC returned results using both source and frozen helpers.
  Its SDK was explicitly installed outside the repo; no DLL is redistributed.
- Standalone PyInstaller build and visible-window/clean-exit smoke passed.
- Interactive standalone shortcuts check sends real Windows Ctrl+comma/F3 only
  to its own temporary-profile process and verifies visible settings/preview with
  UI Automation. Build version is checked against the title, not just startup.
- pip check passed. A dependency database scan of the reference environment
  reported no known vulnerabilities after updating pip; not a native-code audit.

These are local observations, not a security guarantee or a promise of all-green
CI on every platform. Symlink tests need privileges. Retest builds on clean
machines and review CI before release.

## Remaining limitations

- Windows x64 is the only supported target. Legacy cross-platform branches are
  not maintained as product features. Non-Windows requirements were removed.
- Python's legacy plugin loader uses deprecated load_module; Python 3.15 needs
  a separately tested migration. Use Python 3.14 for now.
- Qt5 and tinycss are aging dependencies. Security database checks do not fully
  cover bundled Qt libraries, native components, external 7-Zip or plugins.
- Plugins, external tools and a user-selected native SDK DLL are not sandboxed.
  Basic ZIP checks and preview limits are not a complete hostile-file audit.
  Preview supports text, common raster images and bounded directory statistics;
  PDF, SVG and AVIF are deferred. Directory statistics are not recursive.
- Everything queries run in timeout-bounded child helpers; a single replaceable
  pending query and generation checks prevent stale UI updates. Slow native
  servers or filesystem paths can still delay providers, not the Qt event loop.
- Parent navigation is outside the file model, not a synthetic selectable file.
  This avoids accidentally operating on the parent and makes filters irrelevant.
- The build may warn about optional Windows API-set DLL names in winpty's native
  binaries. Additional manual testing of PTY/terminal behavior is needed.
- Clipboard, drag/drop, network shares, encrypted archives, cancellation and very
  large directories need further manual coverage. File-operation tests use temp
  fixtures, not personal data.
- A GPL-compliant binary release needs corresponding source and a reviewed
  component/notice inventory. No such binary release is part of this source push.
