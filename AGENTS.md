# Agent Instructions

This repository publishes one writing standard into several agent-native instruction formats.
Keep the generated artifacts truthful and in sync.

## Hard Rules

- Edit `core/meta.toml`, `core/body.md`, or `adapters/*.toml`; never hand-edit `dist/`.
- After changing source or adapters, run `python scripts/build.py` and commit the regenerated
  `dist/` files with the source change.
- Public docs that describe architecture or contracts belong in `docs/specs/`.
- Work plans belong in `docs/plans/`.
- Architecture playgrounds belong in `docs/playgrounds/architecture/`.

## Gates

Run these before handing off a change:

```bash
python scripts/build.py --check
python -m unittest discover -s tests -v
python -m ruff check .
```

`make all` runs the same gates when `make` is available.

## Contract

The CLI exit-code contract is stable:

- `0`: success or in-sync.
- `1`: drift detected by `--check`.
- `2`: invalid source input.

The canonical design contract is in `docs/specs/high-signal-output-contract.md`; the visual
architecture map is in `docs/playgrounds/architecture/high-signal-output-flow.html`.
