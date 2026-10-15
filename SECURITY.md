# Security

This is a small independent project, not a security-certified file manager.
Only Windows x64 on Python 3.14 has been tested locally.

- Plugins are arbitrary Python with full user privileges. Install only trusted code.
- Keep Python, dependencies and the separately installed 7-Zip updated.
- Themes and local configuration should also come from trusted sources.
- Dependency database scans and archive guards are not a complete security audit.
- No original signing material, credentials, private infrastructure or Git history
  is included here. Never add secrets, user profiles or certificates to commits.

Use GitHub private vulnerability reporting when available. Do not put credentials,
private files or exploit details affecting users in public issues. If private
reporting is unavailable, open a minimal issue requesting a private contact,
without sensitive material.

Native Qt5 is aging. A clean pip-audit result does not establish that Qt or the
packaged executable has no vulnerabilities. See docs/review.md for test limits.
