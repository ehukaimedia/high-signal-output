# Compatibility Evidence Pass

Status: Complete

## Objective

Address the external review findings by proving platform metadata limits, demonstrating the writing
benefit, and tightening generated-artifact hygiene without changing the canonical guidance body.

## Changes

- Split the ambiguous Claude artifact into Claude Code and Claude.ai targets.
- Add adapter-level description overrides and metadata length validation.
- Make `scripts/build.py --check` fail on orphaned files under `dist/`.
- Add installer shortcuts through `scripts/install.py` and `Makefile`.
- Add a compatibility matrix and a small signal-density eval gate.
- Refresh README, the contract spec, and the architecture playground.

## Acceptance Gates

- `python scripts/build.py --check`
- `python -m unittest discover -s tests -v`
- `python scripts/eval_examples.py --check`
- `python -m ruff check .`
- local Markdown link check
