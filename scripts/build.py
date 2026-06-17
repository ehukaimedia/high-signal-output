#!/usr/bin/env python3
"""Generate the per-platform skill artifacts from the single source of truth.

One canonical document (`core/meta.toml` + `core/body.md`) is rendered into each
platform's idiomatic format under `dist/`. The generated files are committed so
they can be grabbed directly; CI runs `--check` to prove they never drift from the
source.

Usage:
    python scripts/build.py            # write dist/ from core/ + adapters/
    python scripts/build.py --check    # verify dist/ matches the source (no writes)
    python scripts/build.py --json     # machine-readable result (combine with --check)

Exit codes (stable contract):
    0  success — written, or (with --check) everything in sync
    1  drift   — (with --check) one or more dist files are stale
    2  bad input — missing/invalid core or adapter sources
"""
from __future__ import annotations

import argparse
import json
import sys
import textwrap
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "core"
ADAPTERS = ROOT / "adapters"
DIST = ROOT / "dist"

WRAP_WIDTH = 98  # 2-space YAML indent + 98 keeps frontmatter under ~100 cols


class BuildError(Exception):
    """Raised for malformed or missing source input (maps to exit code 2)."""


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise BuildError(f"missing required source: {path.relative_to(ROOT)}")
    # Normalize newlines so output is byte-identical regardless of host OS.
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def _load_toml(path: Path) -> dict:
    if not path.is_file():
        raise BuildError(f"missing required source: {path.relative_to(ROOT)}")
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        raise BuildError(f"invalid TOML in {path.relative_to(ROOT)}: {exc}") from exc


def _require(mapping: dict, key: str, source: Path) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{source.relative_to(ROOT)}: missing/empty key '{key}'")
    return value


def _yaml_folded(description: str) -> str:
    """Render a one-line string as a YAML `>-` folded block, indented two spaces."""
    wrapped = textwrap.wrap(" ".join(description.split()), width=WRAP_WIDTH)
    body = "\n".join(f"  {line}" for line in wrapped)
    return f"description: >-\n{body}"


def render_all() -> dict[str, str]:
    """Render every platform artifact. Returns {relative dist path: content}."""
    meta = _load_toml(CORE / "meta.toml")
    name = _require(meta, "name", CORE / "meta.toml")
    title = _require(meta, "title", CORE / "meta.toml")
    tagline = _require(meta, "tagline", CORE / "meta.toml")
    description = _require(meta, "description", CORE / "meta.toml")
    body = _read_text(CORE / "body.md").strip("\n")

    adapter_files = sorted(ADAPTERS.glob("*.toml"))
    if not adapter_files:
        raise BuildError(f"no adapters found in {ADAPTERS.relative_to(ROOT)}")

    rendered: dict[str, str] = {}
    for adapter_path in adapter_files:
        cfg = _load_toml(adapter_path)
        output = _require(cfg, "output", adapter_path)
        header = _require(cfg, "header", adapter_path)

        if header == "yaml":
            front = f"---\nname: {name}\n{_yaml_folded(description)}\n---"
            top = f"{front}\n\n# {title}\n\n**{tagline}**"
        elif header == "prose":
            note = _require(cfg, "note", adapter_path)
            top = f"# {title}\n\n**{tagline}**\n\n> {note}"
        else:
            raise BuildError(f"{adapter_path.relative_to(ROOT)}: unknown header '{header}'")

        rendered[output] = f"{top}\n\n{body}\n"

    return rendered


def write(rendered: dict[str, str]) -> list[str]:
    written = []
    for rel, content in rendered.items():
        dest = DIST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        # newline="" + explicit \n keeps committed files LF on every OS.
        dest.write_text(content, encoding="utf-8", newline="")
        written.append(rel)
    return written


def drift(rendered: dict[str, str]) -> list[dict[str, str]]:
    """Return a list of stale/missing dist files (empty when in sync)."""
    out = []
    for rel, content in rendered.items():
        dest = DIST / rel
        if not dest.is_file():
            out.append({"file": rel, "reason": "missing"})
        else:
            current = dest.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            if current != content:
                out.append({"file": rel, "reason": "stale"})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build per-platform skill artifacts.")
    parser.add_argument("--check", action="store_true", help="verify dist/ is in sync")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    try:
        rendered = render_all()
    except BuildError as exc:
        if args.json:
            print(json.dumps({"status": "bad_input", "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    files = sorted(rendered)
    if args.check:
        stale = drift(rendered)
        status = "in_sync" if not stale else "drift"
        if args.json:
            print(json.dumps({"status": status, "files": files, "drift": stale}))
        elif stale:
            print("dist/ is out of sync with core/ — run: python scripts/build.py")
            for d in stale:
                print(f"  {d['reason']:7} {d['file']}")
        else:
            print(f"in sync: {len(files)} artifacts match the source")
        return 1 if stale else 0

    written = write(rendered)
    if args.json:
        print(json.dumps({"status": "written", "files": written}))
    else:
        print(f"wrote {len(written)} artifacts to dist/")
        for rel in written:
            print(f"  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
