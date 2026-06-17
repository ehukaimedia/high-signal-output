# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Separate Claude Code and Claude.ai generated artifacts with target-specific metadata limits.
- Compatibility matrix for Claude Code, Claude.ai, Codex, Gemini CLI, Antigravity, and generic
  Markdown.
- Signal-density example eval gate and installer helper for generated artifacts.

### Changed
- The drift gate now fails on orphaned generated files under `dist/`, not only missing or stale
  expected files.
- README now leads with before/after examples and links to measured local evidence instead of
  making unsupported corpus-level provenance claims.

## [0.1.0] - 2026-06-16

### Added
- The High-Signal Output standard as a single source of truth (`core/meta.toml`, `core/body.md`).
- Platform adapters and a dependency-free generator (`scripts/build.py`) producing Claude
  (`SKILL.md`), Codex (`AGENTS.md`), Gemini (`GEMINI.md`), and general Markdown artifacts in
  `dist/`.
- Sync contract with a deterministic exit-code CLI (`0` in sync · `1` drift · `2` bad input) and
  `--json` output, exercised by a `unittest` suite (golden sync plus negative/corruption gates).
- GitHub Actions CI (build-check + tests + lint) and the full set of repo-health files.
- Architecture contract docs, an interactive code-map playground, root agent instructions, and
  GitHub issue/PR templates.

[Unreleased]: https://github.com/ehukaimedia/high-signal-output/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ehukaimedia/high-signal-output/releases/tag/v0.1.0
