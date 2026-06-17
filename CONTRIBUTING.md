# Contributing

Thanks for helping improve High-Signal Output. The repo is small and strict — one rule matters most.

## The one hard rule: edit the source, never the build output

The files in [`dist/`](dist/) are **generated**. Never edit them by hand — the change will be
overwritten and CI will reject it.

- To change the **content**, edit [`core/body.md`](core/body.md) (the principles) or
  [`core/meta.toml`](core/meta.toml) (name, title, tagline, trigger description).
- To change a **platform's framing**, edit the relevant file in [`adapters/`](adapters/).
- Then regenerate and verify:

```bash
python scripts/build.py
python scripts/build.py --check   # must print "in sync"
```

Commit the regenerated `dist/` alongside your source change.

## Setup

- Python 3.11+ (the build uses the standard-library `tomllib`). No runtime dependencies.
- Linting uses [ruff](https://docs.astral.sh/ruff/), pinned in `requirements-dev.txt`.

```bash
python -m pip install -r requirements-dev.txt
```

## Tests

```bash
python -m unittest discover -s tests -v
python -m ruff check .
# or run every gate at once:
make all
```

The suite proves the sync gate actually works: the committed `dist/` matches the source, the body
is identical across platforms, and the gate *fails* on stale output, missing output, and bad input.
If you add a platform or change rendering, add the matching test.

## Pull requests

- Branch off `main`; keep each PR focused on one concern.
- Use [Conventional Commits](https://www.conventionalcommits.org) (`feat:`, `fix:`, `docs:`,
  `test:`, `chore:`).
- Fill in the PR template: what changed, why, and how you verified it (commands + output).
- Update [CHANGELOG.md](CHANGELOG.md) under `Unreleased` for any user-facing change.
- CI (build-check + tests + lint) must be green before merge.
