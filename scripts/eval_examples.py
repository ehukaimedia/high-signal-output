#!/usr/bin/env python3
"""Evaluate the repo's illustrative high-signal before/after examples."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "tests" / "fixtures" / "signal_density_examples.json"
TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class EvalError(Exception):
    """Raised when the example file is missing or malformed."""


def token_proxy(text: str) -> int:
    """Dependency-free token proxy for comparing local examples."""
    return len(TOKEN_RE.findall(text))


def _load_examples() -> list[dict]:
    if not EXAMPLES.is_file():
        raise EvalError(f"missing examples file: {EXAMPLES.relative_to(ROOT)}")
    try:
        data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvalError(f"invalid JSON in {EXAMPLES.relative_to(ROOT)}: {exc}") from exc
    examples = data.get("examples")
    if not isinstance(examples, list) or not examples:
        raise EvalError("examples.json must contain a non-empty 'examples' list")
    return examples


def evaluate() -> list[dict]:
    rows = []
    for item in _load_examples():
        name = item.get("name")
        before = item.get("before")
        after = item.get("after")
        caveats = item.get("required_caveats", [])
        if not isinstance(name, str) or not isinstance(before, str) or not isinstance(after, str):
            raise EvalError("each example needs string fields: name, before, after")
        if not isinstance(caveats, list) or not all(isinstance(c, str) for c in caveats):
            raise EvalError(f"{name}: required_caveats must be a list of strings")

        before_tokens = token_proxy(before)
        after_tokens = token_proxy(after)
        missing_caveats = [c for c in caveats if c.lower() not in after.lower()]
        rows.append(
            {
                "name": name,
                "before_tokens": before_tokens,
                "after_tokens": after_tokens,
                "delta_tokens": before_tokens - after_tokens,
                "reduction_percent": round((before_tokens - after_tokens) / before_tokens * 100, 1),
                "missing_caveats": missing_caveats,
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check illustrative high-signal examples.")
    parser.add_argument("--check", action="store_true", help="fail if an example loses signal")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    try:
        rows = evaluate()
    except EvalError as exc:
        if args.json:
            print(json.dumps({"status": "bad_input", "error": str(exc)}))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 2

    failures = [
        row
        for row in rows
        if row["delta_tokens"] <= 0 or row["missing_caveats"]
    ]
    status = "pass" if not failures else "fail"
    if args.json:
        print(json.dumps({"status": status, "examples": rows, "failures": failures}))
    else:
        for row in rows:
            print(
                f"{row['name']}: {row['before_tokens']} -> {row['after_tokens']} "
                f"({row['reduction_percent']}% smaller)"
            )
        if failures:
            print("failed: examples must shrink while retaining required caveats")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
