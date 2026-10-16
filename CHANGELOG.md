# Changelog

## 1.7.6+synrg.4

- Fit image previews to the available space with preserved aspect ratio and no scrollbars.
- Refit automatically on window/splitter resizing; keep small images at native size.
- Copy preview content with Ctrl+Shift+C or a visible button: original-resolution
  decoded image pixels or displayed plain text, never a file URL or panel screenshot.
- Keep Ctrl+C file copying unchanged. Disable preview copying while loading or closed.
- Retain bounded original image data for copying; release idle worker result references.
- Add geometry, full-resolution clipboard MIME and real Windows clipboard format tests.

## 1.7.6+synrg.3

- Display the exact build version in the title to distinguish stale local executables.
- Add visible View menu entries for Search, Settings and Preview as alternatives to shortcuts.
- Keep the most recently focused file pane when commands are invoked from menus.
- Check the expected build version in the standalone smoke test.

## 1.7.6+synrg.2

- Windows x64 is now the only supported product/build target.
- Unified Ctrl+P for commands, recent/direct paths and optional Everything IPC search.
- Bounded/debounced background queries, stale-result rejection and native helper timeout.
- Settings panel (Ctrl+,): fonts, hidden files, safe parent row and external tools.
- Shared panel manager with exclusive settings/live preview in the opposite pane.
- F3 read-only text/image/directory-stat preview with resource limits.
- Parent navigation row stays outside file operations, selections and filters.
- F5/F6 and Ctrl+C/X/V are retained; compression is available in palette/context menu.
- Filter removal is idempotent. An empty clipboard no longer breaks palette visibility checks.
- UI smoke checks use canonical Windows temp paths and wait for readiness;
  hosted Windows widget smoke runs offscreen.
  Native Windows/source/frozen UI is also checked locally.
- Everything SDK is installed explicitly outside the repo; no DLL is redistributed.

## 1.7.6+synrg.1

Initial independent SynrgStudio source snapshot, based on fman 1.7.6.

- Removed commercial registration checks and purchase screens.
- Removed remote metrics, identifiers and Sentry reporting.
- Added arrow navigation; unknown shortcuts no longer suggest plugins.
- Kept tutorials available on demand rather than forcing onboarding.
- Replaced fbs Pro with independent local compatibility helpers and PyInstaller.
- Isolated the profile, hardened basic plugin download/extraction checks.
- Removed bundled obsolete archive binaries; use external maintained 7-Zip.
- Added local tests, build scripts, dependency notices and licensing guidance.
- No upstream Git history or release/signing infrastructure imported.
- Adopted GPL-3.0-only for new contributions/the combined project; preserved
  upstream MIT and third-party notices.
- Added offline shortcut help and redirected support to this repository.
