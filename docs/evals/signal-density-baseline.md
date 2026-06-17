# Signal-Density Baseline

Status: Active

This is a small, repo-local evidence check for the writing standard. It is not a broad benchmark
and does not claim model-general superiority. Its job is narrower: prove the examples used in this
repo shrink no-signal prose while retaining named caveats.

## Method

The examples live in `docs/evals/examples.json`. The gate in `scripts/eval_examples.py` computes a
dependency-free token proxy (`words and punctuation`) for each before/after pair, then checks that:

- the high-signal rewrite is smaller than the source text, and
- required caveat strings are still present in the rewrite.

Run it with:

```bash
python scripts/eval_examples.py --check
```

## Baseline Results

The current set covers status updates, PR summaries, handoffs, review findings, and release notes.
Use `python scripts/eval_examples.py --json` for exact counts generated from the checked-in
examples.

## Limits

- The token count is a lightweight proxy, not a model tokenizer.
- The examples are illustrative and public; they are not private transcript data.
- Caveat-retention checks are string-based, so they catch obvious omissions rather than all semantic
  regressions.

This evidence supports the README examples and keeps the repo honest about what is actually
measured here.
