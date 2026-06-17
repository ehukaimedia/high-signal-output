"""Tests for the build/sync contract.

Two layers:
  * RealRepoContract — the committed dist/ must match what core/ regenerates
    (the golden gate CI relies on), plus the single-source invariants.
  * FixtureContract — a throwaway source tree exercises every way the gate can
    fail: stale output, missing output, and each bad-input path (exit code 2).
"""
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build  # noqa: E402

EXPECTED = {
    "claude/SKILL.md",
    "codex/AGENTS.md",
    "gemini/GEMINI.md",
    "general/high-signal-output.md",
}


class RealRepoContract(unittest.TestCase):
    """Exercise the real repository sources and committed dist/."""

    def test_committed_dist_is_in_sync(self):
        # The gate CI runs: regenerate in memory, diff against committed files.
        self.assertEqual(build.drift(build.render_all()), [])

    def test_render_is_deterministic(self):
        self.assertEqual(build.render_all(), build.render_all())

    def test_all_four_platforms_present(self):
        self.assertEqual(set(build.render_all()), EXPECTED)

    def test_body_identical_across_platforms(self):
        bodies = {
            path: content[content.index("## Overview"):]
            for path, content in build.render_all().items()
        }
        self.assertEqual(len(set(bodies.values())), 1, "body must be single-sourced")

    def test_check_cli_returns_zero(self):
        out = StringIO()
        with redirect_stdout(out):
            code = build.main(["--check", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "in_sync")


class FixtureContract(unittest.TestCase):
    """Redirect the build at a controlled temp source tree."""

    def setUp(self):
        self._saved = (build.ROOT, build.CORE, build.ADAPTERS, build.DIST)
        self.tmp = Path(tempfile.mkdtemp())
        build.ROOT = self.tmp
        build.CORE = self.tmp / "core"
        build.ADAPTERS = self.tmp / "adapters"
        build.DIST = self.tmp / "dist"
        (self.tmp / "core").mkdir()
        (self.tmp / "adapters").mkdir()
        (build.CORE / "meta.toml").write_text(
            'name = "x"\ntitle = "X"\ntagline = "t"\ndescription = "d"\n', encoding="utf-8"
        )
        (build.CORE / "body.md").write_text("## Overview\n\nBody.\n", encoding="utf-8")
        (build.ADAPTERS / "claude.toml").write_text(
            'output = "claude/SKILL.md"\nheader = "yaml"\n', encoding="utf-8"
        )
        (build.ADAPTERS / "general.toml").write_text(
            'output = "general/x.md"\nheader = "prose"\nnote = "n"\n', encoding="utf-8"
        )

    def tearDown(self):
        build.ROOT, build.CORE, build.ADAPTERS, build.DIST = self._saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _adapter(self, name, text):
        (build.ADAPTERS / name).write_text(text, encoding="utf-8")

    def test_write_then_check_is_clean(self):
        build.write(build.render_all())
        self.assertEqual(build.drift(build.render_all()), [])
        self.assertEqual(build.main(["--check"]), 0)

    def test_stale_output_is_detected(self):
        build.write(build.render_all())
        target = build.DIST / "claude/SKILL.md"
        target.write_text(target.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        stale = build.drift(build.render_all())
        self.assertEqual([d["reason"] for d in stale], ["stale"])
        self.assertEqual(build.main(["--check"]), 1)

    def test_missing_output_is_detected(self):
        build.write(build.render_all())
        (build.DIST / "claude/SKILL.md").unlink()
        reasons = {d["reason"] for d in build.drift(build.render_all())}
        self.assertEqual(reasons, {"missing"})
        self.assertEqual(build.main(["--check"]), 1)

    def test_missing_core_is_bad_input(self):
        (build.CORE / "meta.toml").unlink()
        self.assertEqual(build.main([]), 2)

    def test_adapter_missing_required_key_is_bad_input(self):
        self._adapter("broken.toml", 'header = "prose"\n')  # no output
        self.assertEqual(build.main([]), 2)

    def test_unknown_header_is_bad_input(self):
        self._adapter("weird.toml", 'output = "weird/x.md"\nheader = "xml"\n')
        self.assertEqual(build.main([]), 2)

    def test_no_adapters_is_bad_input(self):
        for f in build.ADAPTERS.glob("*.toml"):
            f.unlink()
        self.assertEqual(build.main([]), 2)


if __name__ == "__main__":
    unittest.main()
