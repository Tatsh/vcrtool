<!-- markdownlint-configure-file {"MD024": { "siblings_only": true } } -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added

- New public module `vcrtool.sansio` providing sans-I/O protocol codecs: `SIRCSCodec` for SIRCS
  encode and decode and `JLIPCodec` for JLIP frame building and validation, along with `Pulse`,
  `SIRCSCommand`, `SIRCSVariant`, `CommandStatus`, and `checksum`.

### Changed

- Renamed the public JLIP class `JLIP` to `JLIPTransport`, which now delegates framing and
  validation to `JLIPCodec`. This is a breaking public API rename.
- Reworked SIRCS support: the FTDI-based `SIRCS` transport was replaced by `PicoSIRCSTransport`,
  which drives a Raspberry Pi Pico over USB serial.

### Removed

- Removed the FTDI-based `SIRCS` transport and the `pyftdi` runtime dependency.

## [0.0.4] - 2026-05-08

### Changed

- Snapcraft and Flatpak manifests now build from the released git tag instead of the working
  directory, so packaged builds reproduce the exact tagged source.
- AppImage workflow excludes `capture-stereo` and emits the dist artefact under the project name.
- Documentation configuration adds intersphinx mappings for `anyio`, `pyftdi`, `pyrate-limiter`,
  and `pyserial`, fixes the `psutil` URL, and refreshes the repo icon.
- Bumped `click` to 8.3.3 and `ip-address` to 10.1.1; refreshed CodeQL action, markdownlint-cli2,
  and other development dependencies.

### Fixed

- Spelling dictionary updated for new vocabulary used in code and documentation.

## [0.0.3] - 2026-04-26

### Changed

- Removed unnecessary `type: ignore[attr-defined]` comment from `pyrate_limiter` import now that the
  upstream mypy issue is resolved.

### Fixed

- Fixed typo 'exceed' to 'exceeded' in `send_command` and `send_command_fast` docstrings.

## [0.0.2] - 2025-12-20

### Added

- Attestation.

## [0.0.1]

First version.

[unreleased]: https://github.com/Tatsh/vcrtool/compare/v0.0.4...HEAD
[0.0.4]: https://github.com/Tatsh/vcrtool/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/Tatsh/vcrtool/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/Tatsh/vcrtool/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/Tatsh/vcrtool/releases/tag/v0.0.1
