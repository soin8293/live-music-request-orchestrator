# Changelog

All notable changes are recorded here.

## [0.1.2] - 2026-08-23

### Documentation

- Put the credential-free quick start and exact feature boundary at the top of
  the README.
- Added a complete setup guide covering release downloads, credentials, OBS,
  TikFinity, configuration, and troubleshooting.

### Fixed

- Runtime health metadata now reads the installed package version instead of a
  stale hard-coded value.

## [0.1.1] - 2026-08-23

### Added

- Verified synthetic demo screenshot and a two-minute reviewer path.
- Cross-platform environment setup.
- Enforced 80% coverage floor and distribution-package verification in CI.
- Dependabot configuration for Python and GitHub Actions.
- Focused contribution guidance, issue forms, and a pull-request checklist.

### Changed

- Security reporting now points directly to GitHub private vulnerability
  reporting.
- Ingress validation returns a closed set of public error codes instead of
  exception text, resolving CodeQL's exception-exposure finding.

## [0.1.0] - 2026-08-23

### Added

- Initial controller-and-overlay release with normalized ingress, bounded and
  deduplicated queue state, native server-sent events, an OBS-ready overlay,
  tests, architecture notes, and a full-history secret scan.

[0.1.2]: https://github.com/soin8293/live-music-request-orchestrator/releases/tag/v0.1.2
[0.1.1]: https://github.com/soin8293/live-music-request-orchestrator/releases/tag/v0.1.1
[0.1.0]: https://github.com/soin8293/live-music-request-orchestrator/releases/tag/v0.1.0
