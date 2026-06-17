# High-Signal Output

> A portable, model-neutral writing standard for AI coding agents: **write so every token earns
> its place.** One source of truth, generated into Claude Code, Claude.ai, Codex, Gemini, and
> plain-Markdown formats — so the same standard travels across your tools without drifting.

[![CI](https://github.com/ehukaimedia/high-signal-output/actions/workflows/ci.yml/badge.svg)](https://github.com/ehukaimedia/high-signal-output/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Most "be concise" advice makes an agent drop substance to look short. This standard does the
opposite: it optimizes **signal per token** — cut the filler, keep every caveat, lead with the
verdict — and ships the *same* guidance to every agent you use, in each one's native instruction
format.

## Demo

| Context | Before | High-signal version |
|---|---|---|
| Status | I ran the tests and the build check, and those are both passing. I have not pushed the branch yet because I wanted confirmation before making the remote change. | Build check and tests pass; not pushed yet because the remote change still needs confirmation. |
| PR summary | This pull request updates the generator so generated files are kept in sync with source inputs. It also adds tests for missing or stale outputs. | Tightens the generator drift contract and adds missing/stale output tests; the writing guidance itself is unchanged. |
| Handoff | The main remaining caveat is that Claude.ai skill uploads still need to be tested manually in the web product. | Compatibility docs and adapter notes are in place; Claude.ai upload still needs manual web-product testing. |

The checked-in examples are measured by `scripts/eval_examples.py`: each rewrite must shrink the
token proxy count while retaining required caveats. See
[`docs/evals/signal-density-baseline.md`](docs/evals/signal-density-baseline.md).

## Quickstart

```bash
git clone https://github.com/ehukaimedia/high-signal-output.git
cd high-signal-output
python scripts/build.py        # regenerate dist/ from source — Python 3.11+, zero dependencies
```

The ready-to-use artifacts live in [`dist/`](dist/). Grab the one for your agent:

| Agent | File | Install |
|---|---|---|
| **Claude Code** | [`dist/claude-code/SKILL.md`](dist/claude-code/SKILL.md) | copy to `~/.claude/skills/high-signal-output/SKILL.md` |
| **Claude.ai** | [`dist/claude-ai/skill.md`](dist/claude-ai/skill.md) | use as the `skill.md` in an uploaded custom skill |
| **OpenAI Codex** | [`dist/codex/AGENTS.md`](dist/codex/AGENTS.md) | merge into your project `AGENTS.md` (or `~/.codex/AGENTS.md`) |
| **Gemini CLI / Antigravity** | [`dist/gemini/GEMINI.md`](dist/gemini/GEMINI.md) | copy into your project `GEMINI.md` (or `~/.gemini/GEMINI.md`) |
| **Any agent / human** | [`dist/general/high-signal-output.md`](dist/general/high-signal-output.md) | use as a system prompt or style guide |

For example, to install the Claude Code skill:

```bash
mkdir -p ~/.claude/skills/high-signal-output
cp dist/claude-code/SKILL.md ~/.claude/skills/high-signal-output/SKILL.md
```

Installer shortcuts are available too. They refuse to overwrite a different existing file unless
you pass `--force`.

```bash
python scripts/install.py --target claude-code
python scripts/install.py --target codex --dest ./AGENTS.md
python scripts/install.py --target gemini --dest ./GEMINI.md
```

Platform support is tracked in [`docs/compatibility.md`](docs/compatibility.md), including the
Claude Code vs Claude.ai description-limit split and the Gemini CLI to Antigravity transition.

## What's in it

The standard is short and opinionated. Its spine is one idea — **two registers**:

- a **terse line** for the common case — lead with the result, name the specifics, point at the
  next move; and
- a **full artifact** for high-stakes output — a bolded verdict first, then evidence: paths,
  counts, commit hashes.

…plus the moves that raise density without dropping substance, a guardrail of things to *never*
compress away (the verdict, genuine caveats, honest uncertainty), and a precedence order so it
yields to required formats and safety disclosures. Read the full text in
[`core/body.md`](core/body.md).

## How it stays in sync

```
core/meta.toml + core/body.md      single source of truth
        |   adapters/*.toml          per-platform framing
        v
  scripts/build.py  -->  dist/{claude-ai,claude-code,codex,gemini,general}/...   generated, committed
```

The `dist/` files are generated, never hand-edited. CI runs `python scripts/build.py --check`,
which regenerates in memory and fails if any committed artifact is missing, stale, or orphaned —
so the platform targets can never silently diverge. The body is single-sourced, so a wording fix
lands everywhere at once.

`build.py` is agent-operable: a deterministic exit-code contract (`0` in sync · `1` drift · `2` bad
input) plus `--json` output.

## Develop

```bash
python scripts/build.py --check          # verify dist/ matches the source
python -m unittest discover -s tests -v  # run the gate's tests
python scripts/eval_examples.py --check  # verify example rewrites keep caveats
python -m pip install -r requirements-dev.txt
python -m ruff check .                   # lint
# or run every gate at once:
make all
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the one hard rule (edit `core/`, never `dist/`) and the
PR flow.

The source-of-truth contract is documented in
[`docs/specs/high-signal-output-contract.md`](docs/specs/high-signal-output-contract.md), with a
visual architecture map at
[`docs/playgrounds/architecture/high-signal-output-flow.html`](docs/playgrounds/architecture/high-signal-output-flow.html).

## Evidence

The included evidence is deliberately small and public: a checked set of before/after examples with
token-proxy deltas and caveat-retention checks. It supports the repo's examples; it is not a broad
benchmark over private transcripts. Run `python scripts/eval_examples.py --json` to inspect the
current counts.

## Why this stays useful

Even as models improve, two things don't change: every agent platform keeps its **own** instruction
format (`SKILL.md`, `AGENTS.md`, `GEMINI.md`, …), and a better model still needs to be *told* your
house style. A vendor-neutral single source with generated adapters and a drift gate is the durable
layer over that churn — it gets more useful as you add agents, not less.

## License

MIT © Ehukai Media. See [LICENSE](LICENSE).
