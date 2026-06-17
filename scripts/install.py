#!/usr/bin/env python3
"""Install or stage generated High-Signal Output artifacts."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _home(*parts: str) -> Path:
    return Path.home().joinpath(*parts)


TARGETS = {
    "claude-code": {
        "source": ROOT / "dist" / "claude-code" / "SKILL.md",
        "dest": _home(".claude", "skills", "high-signal-output", "SKILL.md"),
        "note": "Claude Code local skill path",
    },
    "claude-ai": {
        "source": ROOT / "dist" / "claude-ai" / "skill.md",
        "dest": ROOT / "build" / "claude-ai" / "high-signal-output" / "skill.md",
        "note": "staged upload folder for Claude.ai custom skills",
    },
    "codex": {
        "source": ROOT / "dist" / "codex" / "AGENTS.md",
        "dest": _home(".codex", "AGENTS.md"),
        "note": "global Codex instructions; use --dest for a project-level AGENTS.md",
    },
    "gemini": {
        "source": ROOT / "dist" / "gemini" / "GEMINI.md",
        "dest": _home(".gemini", "GEMINI.md"),
        "note": "global Gemini CLI context; use --dest for a project-level GEMINI.md",
    },
}


def install(target: str, dest: Path | None, force: bool, dry_run: bool) -> dict:
    cfg = TARGETS[target]
    source = cfg["source"]
    destination = dest or cfg["dest"]
    if not source.is_file():
        raise FileNotFoundError(f"missing generated artifact: {source.relative_to(ROOT)}")

    action = "copy"
    if destination.exists():
        source_text = source.read_text(encoding="utf-8")
        dest_text = destination.read_text(encoding="utf-8")
        if source_text == dest_text:
            action = "already-current"
        elif not force:
            raise FileExistsError(f"refusing to overwrite different file: {destination}")
        else:
            action = "overwrite"

    if not dry_run and action in {"copy", "overwrite"}:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    return {
        "status": action,
        "target": target,
        "source": str(source),
        "destination": str(destination),
        "note": cfg["note"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install generated high-signal-output artifacts.")
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument("--dest", type=Path, help="override the default destination file")
    parser.add_argument("--force", action="store_true", help="overwrite an existing different file")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    try:
        result = install(args.target, args.dest, args.force, args.dry_run)
    except (FileExistsError, FileNotFoundError) as exc:
        if args.json:
            print(json.dumps({"status": "error", "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result))
    else:
        print(f"{result['status']}: {result['source']} -> {result['destination']}")
        print(result["note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
