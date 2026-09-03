# Changelog

All notable changes to Bansoko are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-09-03

A modernization release. The game itself is unchanged — same 62 levels, same
rules, same art — but everything underneath it was brought up to date.

### Changed

- **Python 3.11 or newer is now required.** This is what makes the release a
  major version: Pyxel 2.9.9 requires it, so `pip install bansoko` no longer
  works on Python 3.8, 3.9 or 3.10. Earlier releases advertised Python 3.8,
  which reached end of life in October 2024.
- Migrated to Pyxel 2.9.9 (from 2.0.9) and regenerated the game resources in
  Pyxel's current resource format.
- Packaging moved from `setup.py` and Pipfile to `pyproject.toml`; development
  uses [uv](https://docs.astral.sh/uv/).
- Linux builds are produced against glibc 2.28, so they run on any
  distribution from 2018 onwards. The previous build required a much newer
  glibc than the game actually needs.
- Standalone builds are published as `.tar.gz` (Linux) and `.zip` (Windows)
  archives instead of bare executables.
- Linux installation no longer needs SDL2 system packages; Pyxel ships its own.

### Added

- A test suite covering the Sokoban rules, every game screen, the resource
  builder and the save file format, run against Python 3.11 to 3.14 on both
  Linux and Windows.
- Standalone Windows and Linux builds are now produced and verified
  automatically, and attached to each release.
- A readable message when OpenGL cannot be initialised, in place of an
  unhandled Rust panic.

### Removed

- The `docopt` dependency, unmaintained since 2014, replaced by the standard
  library's `argparse`. Command lines are unchanged.

### Fixed

- Resource metadata is written with LF newlines regardless of the platform it
  was built on, so the generated files are reproducible.
- `transparency_color` is correctly typed as optional; it was always nullable
  at runtime.

### Compatibility

Player profiles from 1.x are read unchanged. Progress is keyed by a checksum
of the level data, and that checksum has not changed.

## [1.2.1] - 2024-03-27

### Changed

- Migrated to Pyxel 2.0.9. This replaced Pyxel's pure-Python renderer with a
  Rust core using shaders, which raised the OpenGL requirements considerably.
- Updated dependencies.

## [1.1.0] - 2022-08-14

### Changed

- Migrated to Pyxel 1.7.2.
- Updated dependencies and resolved new linter warnings.

## [1.0.0] - 2020-12-24

First stable release, built on Pyxel 1.4.3.

### Added

- 62 levels, level browser, per-level statistics and undo.
- Player profile storing progress and best scores.
- Resource builder allowing the game to be modified.

[2.0.0]: https://github.com/kfurtak1024/bansoko/releases/tag/v2.0.0
[1.2.1]: https://github.com/kfurtak1024/bansoko/releases/tag/v1.2.1
[1.1.0]: https://github.com/kfurtak1024/bansoko/releases/tag/v1.1.0
[1.0.0]: https://github.com/kfurtak1024/bansoko/releases/tag/v1.0.0
