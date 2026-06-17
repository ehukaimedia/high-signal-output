#!/usr/bin/env python3
"""Install or stage generated High-Signal Output artifacts."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANAGED_START = "<!-- high-signal-output:start -->"
MANAGED_END = "<!-- high-signal-output:end -->"
MANAGED_BLOCK_RE = re.compile(
    rf"{re.escape(MANAGED_START)}\n.*?\n{re.escape(MANAGED_END)}",
    re.DOTALL,
)
SKILL_NAME_RE = re.compile(r"^name:\s*high-signal-output\s*$", re.MULTILINE)
LOCAL_TARGETS = ("claude-code", "codex", "gemini")


def _home(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


TARGETS = {
    "claude-code": {
        "source": ROOT / "dist" / "claude-code" / "SKILL.md",
        "dest": _home(".claude", "skills", "high-signal-output", "SKILL.md"),
        "mode": "copy",
        "note": "Claude Code local skill path",
    },
    "claude-ai": {
        "source": ROOT / "dist" / "claude-ai" / "skill.md",
        "dest": ROOT / "build" / "claude-ai" / "high-signal-output" / "skill.md",
        "mode": "copy",
        "note": "staged upload folder for Claude.ai custom skills",
    },
    "codex": {
        "source": ROOT / "dist" / "codex" / "AGENTS.md",
        "dest": _home(".codex", "AGENTS.md"),
        "mode": "merge",
        "note": "global Codex instructions; use --dest for a project-level AGENTS.md",
    },
    "gemini": {
        "source": ROOT / "dist" / "gemini" / "GEMINI.md",
        "dest": _home(".gemini", "GEMINI.md"),
        "mode": "merge",
        "note": "global Gemini CLI context; use --dest for a project-level GEMINI.md",
    },
}


def _managed_block(source_text: str) -> str:
    return f"{MANAGED_START}\n{source_text.rstrip()}\n{MANAGED_END}\n"


def _append_block(existing: str, block: str) -> str:
    if not existing.strip():
        return block
    return f"{existing.rstrip()}\n\n{block}"


def _looks_like_unmanaged_install(existing: str) -> bool:
    return "# High-Signal Output" in existing and "Write so every token earns its place" in existing


def _looks_like_same_skill(existing: str) -> bool:
    if not existing.startswith("---\n"):
        return False
    frontmatter_end = existing.find("\n---", 4)
    if frontmatter_end == -1:
        return False
    return bool(SKILL_NAME_RE.search(existing[:frontmatter_end]))


def _merge_text(existing: str, source_text: str) -> tuple[str, str]:
    block = _managed_block(source_text)
    matches = list(MANAGED_BLOCK_RE.finditer(existing))

    if matches:
        parts = []
        last = 0
        changed = False
        inserted = False
        replacement = block.rstrip("\n")
        for match in matches:
            parts.append(existing[last : match.start()])
            if not inserted:
                parts.append(replacement)
                inserted = True
                changed = match.group(0) != replacement
            else:
                changed = True
            last = match.end()
        parts.append(existing[last:])
        merged = "".join(parts)
        if not merged.endswith("\n"):
            merged += "\n"
        if not changed and merged == existing:
            return existing, "already-current"
        return merged, "update"

    if existing.rstrip() == source_text.rstrip():
        return block, "update"
    if _looks_like_unmanaged_install(existing):
        raise FileExistsError(
            "found unmanaged High-Signal Output content; refusing to duplicate it. "
            f"Wrap the existing block with {MANAGED_START} / {MANAGED_END}, then rerun."
        )
    return _append_block(existing, block), "merge"


def install(target: str, dest: Path | None, force: bool, dry_run: bool) -> dict:
    cfg = TARGETS[target]
    source = cfg["source"]
    custom_dest = dest is not None
    destination = dest or cfg["dest"]
    if not source.is_file():
        raise FileNotFoundError(f"missing generated artifact: {source.relative_to(ROOT)}")

    mode = cfg["mode"]
    if mode == "merge":
        source_text = source.read_text(encoding="utf-8")
        if destination.exists():
            dest_text = destination.read_text(encoding="utf-8")
            output, action = _merge_text(dest_text, source_text)
        else:
            output = _managed_block(source_text)
            action = "copy"

        if not dry_run and action != "already-current":
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output, encoding="utf-8", newline="")

        return {
            "status": action,
            "target": target,
            "mode": mode,
            "source": str(source),
            "destination": str(destination),
            "note": cfg["note"],
        }

    source_text = source.read_text(encoding="utf-8")
    action = "copy"
    if destination.exists():
        dest_text = destination.read_text(encoding="utf-8")
        if source_text == dest_text:
            action = "already-current"
        elif not custom_dest and target in {"claude-ai", "claude-code"}:
            action = "update"
        elif _looks_like_same_skill(dest_text):
            action = "update"
        elif not force:
            raise FileExistsError(f"refusing to overwrite different file: {destination}")
        else:
            action = "overwrite"

    if not dry_run and action in {"copy", "overwrite", "update"}:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    return {
        "status": action,
        "target": target,
        "mode": mode,
        "source": str(source),
        "destination": str(destination),
        "note": cfg["note"],
    }


def _parse_targets(value: str) -> list[str]:
    targets = [item.strip() for item in value.split(",") if item.strip()]
    if not targets:
        raise ValueError("at least one target is required")

    unknown = sorted(set(targets) - set(TARGETS))
    if unknown:
        raise ValueError(f"unknown target(s): {', '.join(unknown)}")

    unique = []
    seen = set()
    for target in targets:
        if target not in seen:
            unique.append(target)
            seen.add(target)
    return unique


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install generated high-signal-output artifacts.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--target", choices=sorted(TARGETS))
    group.add_argument("--targets", help="comma-separated targets, e.g. claude-code,codex,gemini")
    group.add_argument("--all", action="store_true", help="install Claude Code, Codex, and Gemini")
    parser.add_argument("--dest", type=Path, help="override the default destination file")
    parser.add_argument("--force", action="store_true", help="overwrite an existing different file")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    try:
        if args.all:
            targets = list(LOCAL_TARGETS)
        elif args.targets:
            targets = _parse_targets(args.targets)
        else:
            targets = [args.target]
        if args.dest and len(targets) != 1:
            parser.error("--dest can only be used with a single target")
        results = [install(target, args.dest, args.force, args.dry_run) for target in targets]
    except ValueError as exc:
        parser.error(str(exc))
    except (FileExistsError, FileNotFoundError) as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results[0] if len(results) == 1 else {"status": "ok", "results": results}))
    else:
        for result in results:
            print(f"{result['status']}: {result['source']} -> {result['destination']}")
            print(result["note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
