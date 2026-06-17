"""Tests for safe installer behavior."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import install  # noqa: E402


class InstallContract(unittest.TestCase):
    def _source_text(self, target: str) -> str:
        return install.TARGETS[target]["source"].read_text(encoding="utf-8")

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

    def test_claude_skill_updates_stale_same_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "SKILL.md"
            dest.write_text(
                "---\nname: high-signal-output\ndescription: old\n---\n\nold body\n",
                encoding="utf-8",
            )

            result = install.install("claude-code", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "update")
            self.assertEqual(dest.read_text(encoding="utf-8"), self._source_text("claude-code"))

    def test_claude_default_skill_path_is_owned(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "SKILL.md"
            dest.write_text("malformed stale skill\n", encoding="utf-8")
            old_dest = install.TARGETS["claude-code"]["dest"]
            install.TARGETS["claude-code"]["dest"] = dest
            try:
                result = install.install("claude-code", None, force=False, dry_run=False)
            finally:
                install.TARGETS["claude-code"]["dest"] = old_dest

            self.assertEqual(result["status"], "update")
            self.assertEqual(dest.read_text(encoding="utf-8"), self._source_text("claude-code"))

    def test_refuses_to_overwrite_different_file_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skill.md"
            dest.write_text("existing instructions\n", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                install.install("claude-ai", dest, force=False, dry_run=False)

    def test_merge_appends_managed_block_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "AGENTS.md"
            dest.write_text("# Existing Project Rules\n\nKeep this.\n", encoding="utf-8")

            result = install.install("codex", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "merge")
            text = dest.read_text(encoding="utf-8")
            self.assertIn("# Existing Project Rules", text)
            self.assertEqual(text.count(install.MANAGED_START), 1)
            self.assertEqual(text.count(install.MANAGED_END), 1)

            second = install.install("codex", dest, force=False, dry_run=False)
            self.assertEqual(second["status"], "already-current")
            self.assertEqual(dest.read_text(encoding="utf-8"), text)

    def test_merge_updates_stale_managed_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "GEMINI.md"
            dest.write_text(
                "# Existing\n\n"
                f"{install.MANAGED_START}\nold guidance\n{install.MANAGED_END}\n\n"
                "Keep after.\n",
                encoding="utf-8",
            )

            result = install.install("gemini", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "update")
            text = dest.read_text(encoding="utf-8")
            self.assertIn("# Existing", text)
            self.assertIn("Keep after.", text)
            self.assertIn(self._source_text("gemini").splitlines()[0], text)
            self.assertNotIn("old guidance", text)
            self.assertEqual(text.count(install.MANAGED_START), 1)

    def test_merge_collapses_duplicate_managed_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "AGENTS.md"
            block = install._managed_block(self._source_text("codex"))
            dest.write_text(f"{block}\n# Middle\n\n{block}", encoding="utf-8")

            result = install.install("codex", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "update")
            text = dest.read_text(encoding="utf-8")
            self.assertIn("# Middle", text)
            self.assertEqual(text.count(install.MANAGED_START), 1)
            self.assertEqual(text.count("# High-Signal Output"), 1)

    def test_merge_migrates_exact_unmanaged_copy_to_managed_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "AGENTS.md"
            dest.write_text(self._source_text("codex"), encoding="utf-8")

            result = install.install("codex", dest, force=False, dry_run=False)
            self.assertEqual(result["status"], "update")
            text = dest.read_text(encoding="utf-8")
            self.assertEqual(text.count(install.MANAGED_START), 1)
            self.assertEqual(text.count("# High-Signal Output"), 1)

    def test_merge_refuses_unmanaged_high_signal_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "AGENTS.md"
            dest.write_text(
                "# Existing\n\n# High-Signal Output\n\n**Write so every token earns its place.**\n",
                encoding="utf-8",
            )

            with self.assertRaises(FileExistsError):
                install.install("codex", dest, force=False, dry_run=False)

    def test_parse_targets_deduplicates(self):
        self.assertEqual(
            install._parse_targets("codex, gemini, codex"),
            ["codex", "gemini"],
        )


if __name__ == "__main__":
    unittest.main()
