# Local JSONL Distillation Refresh

Status: Complete

## Objective

Research the local JSONL corpus and improve High-Signal Output as a model-agnostic writing standard
without publishing raw private transcript content.

## Method

- Scanned local JSONL files structurally for model counts and assistant-visible text records.
- Excluded thinking blocks and tool payloads from the public distillation.
- Used aggregate patterns only; no raw transcript text, project names, paths, or task details were
  copied into the repo.
- Converted recurring patterns into synthetic, platform-agnostic examples.

## Findings

- Strong status updates use `state -> evidence -> next/open loop`.
- Good progress notes name useful concurrency instead of narrating intent.
- High-signal closes keep unresolved work visible: not pushed, not deployed, pending manual smoke
  test, missing auth, or waiting approval.
- Recommendations are strongest when they name the preferred path first and attach the reason plus
  deferred alternative.
- Audit updates can be useful before the final artifact when they report accumulating findings and
  the next gate.

## Changes

- Added status-shape guidance to `core/body.md`.
- Replaced platform-specific examples in `docs/evals/examples.json` with agnostic synthetic
  examples distilled from corpus patterns.
- Updated `docs/evals/signal-density-baseline.md` with aggregate source counts and privacy limits.
- Regenerated `dist/` artifacts from the single source of truth.

## Acceptance Gates

- `python scripts/build.py --check`
- `python -m unittest discover -s tests -v`
- `python scripts/eval_examples.py --check`
- `python -m ruff check .`
