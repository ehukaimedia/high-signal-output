# Signal-Density Baseline

Status: Active

This is a small, repo-local evidence check for the writing standard. It is not a broad benchmark
and does not claim model-general superiority. Its job is narrower: prove the examples used in this
repo shrink no-signal prose while retaining named caveats.

## Private Source Material

The agnostic examples were refreshed from aggregate review of a private local JSONL corpus on
2026-06-17. No raw transcript text, project names, paths, or private task details are included in
this repository.

Aggregate scan:

- 421 JSONL files under the local Claude data directory.
- 70,032 parsed JSONL events.
- 5,048 target-model assistant events.
- 546 assistant-visible text records from 41 sessions.
- 1,799 thinking blocks found and excluded from the public distillation.

Observed public-safe patterns:

- Short status updates often fit `state -> evidence -> next/open loop`.
- Good progress notes name useful concurrency: what is running and what is checked meanwhile.
- Strong closes preserve open loops such as not pushed, not deployed, manual smoke test pending, or
  missing credentials.
- Useful recommendations lead with the choice, then attach the reason and deferred alternative.
- Audit updates can report accumulating findings before the final artifact, as long as they name the
  next gate.

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

The current set covers status updates, PR summaries, handoffs, review findings, release notes,
running-work updates, recommendations, blocked states, and accumulating audit findings. Use
`python scripts/eval_examples.py --json` for exact counts generated from the checked-in examples.

## Limits

- The token count is a lightweight proxy, not a model tokenizer.
- The examples are illustrative and public; they are synthetic, agnostic examples distilled from
  private-source patterns rather than copied transcript data.
- Caveat-retention checks are string-based, so they catch obvious omissions rather than all semantic
  regressions.

This evidence supports the README examples and keeps the repo honest about what is actually
measured here.
