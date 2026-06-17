# Repo Completion Plan

Status: Complete

## Objective

Finish the public repository surface without overwriting the existing scaffold: preserve the
single-source build system, add missing OSS health files, document the architecture contract, and
verify all local gates.

## Scope

- Keep the existing `core/`, `adapters/`, `scripts/`, `tests/`, and `dist/` design.
- Add root agent instructions, a contract spec, and an architecture playground.
- Add missing community and GitHub collaboration files.
- Align local development instructions with CI by pinning dev tooling in `requirements-dev.txt`.

## Acceptance Gates

- `python scripts/build.py --check`
- `python -m unittest discover -s tests -v`
- `python -m ruff check .`
- Search for stale scaffolding text or obsolete guidance before handoff.

## Out Of Scope

- Pushing to GitHub.
- Creating tags or releases.
- Changing the generated writing standard text.
- Adding runtime dependencies.
