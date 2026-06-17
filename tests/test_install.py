"""Tests for safe installer behavior."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import install  # noqa: E402


class InstallContract(unittest.TestCase):
    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "SKILL.md"
            result = install.install("claude-ai", dest, force=False, dry_run=True)
            self.assertEqual(result["status"], "copy")
            self.assertFalse(dest.exists())

    def test_copy_then_already_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "SKILL.md"
            result = install.install("claude-ai", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "copy")
            self.assertEqual(
                install.install("claude-ai", dest, force=False, dry_run=False)["status"],
                "already-current",
            )

    def test_refuses_to_overwrite_different_file_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "AGENTS.md"
            dest.write_text("existing instructions\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                install.install("codex", dest, force=False, dry_run=False)


if __name__ == "__main__":
    unittest.main()
