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
    1  drift   — (with --check) dist files are missing, stale, or orphaned
    2  bad input — missing/invalid core or adapter sources
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "core"
ADAPTERS = ROOT / "adapters"
DIST = ROOT / "dist"

WRAP_WIDTH = 98  # 2-space YAML indent + 98 keeps frontmatter under ~100 cols
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AGENT_SKILL_DESCRIPTION_MAX = 1024


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


def _optional_string(mapping: dict, key: str, source: Path) -> str | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{source.relative_to(ROOT)}: key '{key}' must be a non-empty string")
    return value


def _optional_positive_int(mapping: dict, key: str, source: Path) -> int | None:
    value = mapping.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise BuildError(f"{source.relative_to(ROOT)}: key '{key}' must be a positive integer")
    return value


def _validate_output(output: str, source: Path) -> str:
    rel = Path(output)
    if rel.is_absolute() or ".." in rel.parts:
        raise BuildError(f"{source.relative_to(ROOT)}: output must stay inside dist/")
    normalized = rel.as_posix()
    if not normalized or normalized.startswith("/"):
        raise BuildError(f"{source.relative_to(ROOT)}: invalid output path '{output}'")
    return normalized


def _validate_skill_metadata(
    name: str,
    description: str,
    max_description: int,
    source: Path,
) -> None:
    if len(name) > 64 or not SKILL_NAME_RE.fullmatch(name):
        raise BuildError(
            f"{CORE.relative_to(ROOT) / 'meta.toml'}: name must be <=64 lowercase "
            "letters/numbers/hyphens with no leading, trailing, or repeated hyphens"
        )
    if len(description) > max_description:
        raise BuildError(
            f"{source.relative_to(ROOT)}: description is {len(description)} characters; "
            f"limit is {max_description}"
        )


def _yaml_folded(description: str) -> str:
    """Render a one-line string as a YAML `>-` folded block, indented two spaces."""
    wrapped = textwrap.wrap(" ".join(description.split()), width=WRAP_WIDTH)
    body = "\n".join(f"  {line}" for line in wrapped)
    return f"description: >-\n{body}"


def _dist_files() -> set[str]:
    if not DIST.exists():
        return set()
    return {path.relative_to(DIST).as_posix() for path in DIST.rglob("*") if path.is_file()}


def render_all() -> dict[str, str]:
    """Render every platform artifact. Returns {relative dist path: content}."""
    meta = _load_toml(CORE / "meta.toml")
    name = _require(meta, "name", CORE / "meta.toml")
    title = _require(meta, "title", CORE / "meta.toml")
    tagline = _require(meta, "tagline", CORE / "meta.toml")
    default_description = _require(meta, "description", CORE / "meta.toml")
    body = _read_text(CORE / "body.md").strip("\n")

    adapter_files = sorted(ADAPTERS.glob("*.toml"))
    if not adapter_files:
        raise BuildError(f"no adapters found in {ADAPTERS.relative_to(ROOT)}")

    rendered: dict[str, str] = {}
    for adapter_path in adapter_files:
        cfg = _load_toml(adapter_path)
        output = _validate_output(_require(cfg, "output", adapter_path), adapter_path)
        header = _require(cfg, "header", adapter_path)

        if header == "yaml":
            description = _optional_string(cfg, "description", adapter_path) or default_description
            description_max = (
                _optional_positive_int(cfg, "description_max", adapter_path)
                or AGENT_SKILL_DESCRIPTION_MAX
            )
            _validate_skill_metadata(name, description, description_max, adapter_path)
            front = f"---\nname: {name}\n{_yaml_folded(description)}\n---"
            top = f"{front}\n\n# {title}\n\n**{tagline}**"
        elif header == "prose":
            note = _require(cfg, "note", adapter_path)
            top = f"# {title}\n\n**{tagline}**\n\n> {note}"
        else:
            raise BuildError(f"{adapter_path.relative_to(ROOT)}: unknown header '{header}'")

        if output in rendered:
            raise BuildError(f"{adapter_path.relative_to(ROOT)}: duplicate output '{output}'")
        rendered[output] = f"{top}\n\n{body}\n"

    return rendered


def write(rendered: dict[str, str]) -> list[str]:
    written = []
    for rel in sorted(_dist_files() - set(rendered)):
        (DIST / rel).unlink()
    for rel, content in rendered.items():
        dest = DIST / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        # newline="" + explicit \n keeps committed files LF on every OS.
        dest.write_text(content, encoding="utf-8", newline="")
        written.append(rel)
    for directory in sorted((p for p in DIST.rglob("*") if p.is_dir()), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    return written


def drift(rendered: dict[str, str]) -> list[dict[str, str]]:
    """Return stale, missing, or orphaned dist files (empty when in sync)."""
    out = []
    for rel, content in rendered.items():
        dest = DIST / rel
        if not dest.is_file():
            out.append({"file": rel, "reason": "missing"})
        else:
            current = dest.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            if current != content:
                out.append({"file": rel, "reason": "stale"})
    for rel in sorted(_dist_files() - set(rendered)):
        out.append({"file": rel, "reason": "orphan"})
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
