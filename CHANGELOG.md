# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `freecad_cli/core.py` — Core CLI module with 20+ command groups (part, sketch, draft, arch, mesh, export, info, document, boolean, assembly, etc.)
- `freecad_cli/ai_integration.py` — AI integration helpers for natural language to CLI command conversion
- `freecad_cli/freecad_integration.py` — FreeCAD wrapper with mock mode for environments without FreeCAD
- `freecad_cli/formatter.py` — Multi-format output (JSON, YAML, text, table)
- `freecad_cli/decorators.py` — Reusable decorators and `NonEmptyString` validator
- `tests/test_freecad_wrapper.py` — Unit tests for FreeCADWrapper (27 tests)
- `tests/test_core.py` — Unit tests for CLI command layer (27 tests)
- `commitlint.config.js` — Conventional commit configuration
- `scripts/validate-commit-msg.sh` — Git commit-msg hook installer
- `CHANGELOG.md` — This changelog
- Dockerfile, `setup.py`, `package.json`, `requirements.txt` — Project distribution files

### Fixed
- `decorators.py` — `NonEmptyString` validator now rejects empty and whitespace-only names on all `--name` options
- `core.py` — CLI help text now documents that global flags (`--format`, `--pretty`, `--verbose`) must precede subcommands
- `requirements.txt` — Added `pytest>=7.0.0` (was missing, blocking test execution)
- `core.py` — All `--name` options (38 total) now use `type=NonEmptyString()` validation

### Changed
- `core.py` — All docstrings and help text migrated from Chinese to English for broader accessibility
- `decorators.py` — All docstrings migrated from Chinese to English
