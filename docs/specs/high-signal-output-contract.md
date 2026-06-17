# High-Signal Output Contract

Status: Active
Owner: Ehukai Media
Architecture playground: `docs/playgrounds/architecture/high-signal-output-flow.html`

## Purpose

High-Signal Output is a portable writing standard for AI coding agents. The repository keeps one
canonical body and emits platform-native artifacts for Claude, Codex, Gemini, and generic Markdown.

The system exists to prevent instruction drift: a style fix should land once in `core/` and then be
proved identical across all generated platform bodies.

## Six-Month Usefulness Thesis

Even if major agent platforms improve their native instruction systems over the next six months,
they are still likely to keep distinct file names, metadata surfaces, and loading rules. This repo
stays useful because it is adapter-first: it owns a small source-of-truth contract, generated
platform wrappers, and a drift gate rather than competing with any one agent.

## Durable Wedge

- User/workflow: developers and teams who want one prose standard across multiple AI coding agents.
- Recurring pain: every platform wants instructions in a different shape, so manual copies drift.
- Dogfoodable slice: edit `core/body.md`, run `python scripts/build.py`, and install from `dist/`.
- Compounding layer: each new adapter increases the value of the shared body and tests.

## Sources Of Truth

| Source | Responsibility | Evidence |
|---|---|---|
| `core/meta.toml` | Name, title, tagline, and trigger description. | `core/meta.toml:5`, `core/meta.toml:6`, `core/meta.toml:7`, `core/meta.toml:11` |
| `core/body.md` | Canonical writing guidance shared by every artifact. | `core/body.md:1`, `core/body.md:13`, `core/body.md:31`, `core/body.md:42`, `core/body.md:55`, `core/body.md:87` |
| `adapters/*.toml` | Per-platform output path and wrapper mode. | `adapters/claude.toml:4`, `adapters/codex.toml:4`, `adapters/gemini.toml:4`, `adapters/general.toml:4` |
| `scripts/build.py` | Rendering, writing, drift detection, and exit codes. | `scripts/build.py:71`, `scripts/build.py:104`, `scripts/build.py:115`, `scripts/build.py:129` |
| `dist/` | Generated, committed install artifacts. | Enforced by `python scripts/build.py --check`. |
| `tests/test_build.py` | Golden sync, determinism, body identity, and bad-input coverage. | `tests/test_build.py:29`, `tests/test_build.py:57`, `tests/test_build.py:87` |

## Build Contract

`scripts/build.py` renders all adapters from `core/meta.toml`, `core/body.md`, and
`adapters/*.toml`. Rendering normalizes newlines so generated files are byte-stable across
platforms.

Stable exit codes:

- `0`: build/write succeeded, or `--check` found `dist/` in sync.
- `1`: `--check` found missing or stale generated output.
- `2`: source input is missing or invalid.

`--json` emits machine-readable status for agent callers. The status values are `written`,
`in_sync`, `drift`, and `bad_input`.

## Adapter Contract

Adapters use one of two header modes:

- `yaml`: emits Claude-style YAML frontmatter plus the shared body.
- `prose`: emits a Markdown title, tagline, note, and the shared body.

Unknown header modes, missing adapter keys, invalid TOML, missing core files, or an empty adapter
directory are bad input and must return exit code `2`.

## Verification Gates

Run all gates before release or handoff:

```bash
python scripts/build.py --check
python -m unittest discover -s tests -v
python -m ruff check .
```

CI runs the same gates on Python 3.11, 3.12, and 3.13 through
`.github/workflows/ci.yml`.

## Non-Goals

- No runtime package, daemon, hosted service, or network dependency.
- No platform-specific edits to the shared body.
- No generated-output hand edits.
- No claim that this replaces a platform's own instruction loader.

## Change Protocol

1. Edit `core/` for content or identity changes.
2. Edit `adapters/` only when a platform wrapper changes.
3. Run `python scripts/build.py` to regenerate `dist/`.
4. Run all verification gates.
5. Update this spec and the architecture playground when the source-of-truth contract changes.
