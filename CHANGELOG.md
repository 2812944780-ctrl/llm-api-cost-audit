# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
semantic versioning.

## [0.1.1] - 2026-10-05

### Added

- Documentation site landing page (`docs/index.md`) plus Jekyll config, so the guides can be published
  on GitHub Pages instead of only being readable as repository files.
- This changelog.

### Changed

- README: added a release badge and a documentation-site link.

## [0.1.0] - 2026-09-16

Initial public version.

### Added

- `audit` package: `UsageLogger` for recording model, token counts, finish reason, request ID and tags
  from any OpenAI-compatible endpoint.
- CLI: `python -m audit report <log.jsonl>` with text and `--json` output, `--window` for retry
  detection, and `python -m audit tail <log.jsonl>`.
- Three detectors: retry double-billing, `prompt_tokens` variance per tag, and context bloat.
  The report exits with code `1` when a `HIGH` finding is present, so it can run as a CI gate.
- Examples for the Python SDK, Python standard library, Node.js 18+, curl and PowerShell, plus
  environment templates that read credentials from environment variables.
- Guides for Claude Code, Codex CLI, CC Switch, Cherry Studio, streaming, HTTP errors, architecture,
  a client matrix and an FAQ.
- CI workflow (`checks`) that compiles the sources, generates a sample log and renders a report.
