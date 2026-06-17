## What Changed

- 

## Why

- 

## Verification

Paste the commands you ran and their results:

```bash
python scripts/build.py --check
python -m unittest discover -s tests -v
python -m ruff check .
```

## Checklist

- [ ] I edited `core/` or `adapters/`, not generated `dist/`, unless regenerating output.
- [ ] `dist/` is in sync with the source.
- [ ] User-facing changes are reflected in `CHANGELOG.md`.
- [ ] Docs/spec/playground updates are included when the architecture contract changed.
