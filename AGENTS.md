# Agent Instructions

This repository publishes one writing standard into several agent-native instruction formats.
Keep the generated artifacts truthful and in sync.

## Hard Rules

- Edit `core/meta.toml`, `core/body.md`, or `adapters/*.toml`; never hand-edit `dist/`.
- After changing source or adapters, run `python scripts/build.py` and commit the regenerated
  `dist/` files with the source change.
- Keep private plans, specs, and architecture notes out of the public repo; `docs/` is ignored.

## Gates

Run these before handing off a change:

```bash
python scripts/build.py --check
python -m unittest discover -s tests -v
python scripts/eval_examples.py --check
python -m ruff check .
```

`make all` runs the same gates when `make` is available.

## Contract

The CLI exit-code contract is stable:

- `0`: success or in-sync.
- `1`: drift detected by `--check`.
- `2`: invalid source input.

The build contract lives in `scripts/build.py` and is enforced by `tests/test_build.py`.
