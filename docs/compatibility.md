# Compatibility Matrix

Checked: 2026-06-17

This matrix records what the repo claims for each generated artifact. It is intentionally narrow:
an entry means the artifact shape matches the documented instruction surface as of the checked date,
not that every web or desktop product flow has been manually uploaded and exercised.

| Target | Artifact | Install path or usage | Documented limit checked | Local enforcement | Source |
|---|---|---|---|---|---|
| Claude Code | `dist/claude-code/SKILL.md` | `~/.claude/skills/high-signal-output/SKILL.md` | Agent Skills `name` <= 64; `description` <= 1024. | `description_max = 1024`; unit test checks name and description limits. | [Claude Code skills](https://code.claude.com/docs/en/skills), [Agent Skills specification](https://agentskills.io/specification) |
| Claude.ai | `dist/claude-ai/skill.md` | Uploaded custom skill folder containing lowercase `skill.md`. | `name` <= 64; `description` <= 200. | `description_max = 200`; unit test checks the generated description length. | [Claude.ai custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) |
| OpenAI Codex CLI/app | `dist/codex/AGENTS.md` | Project `AGENTS.md` or global `~/.codex/AGENTS.md`. | Default combined project-doc limit is 32 KiB. | Unit test keeps the Codex artifact below 32 KiB. | [OpenAI Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md) |
| Gemini CLI | `dist/gemini/GEMINI.md` | Project `GEMINI.md` or global `~/.gemini/GEMINI.md`. | No metadata description field for this artifact. | Generated from the same body and covered by the drift gate. | [Gemini CLI GEMINI.md docs](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html) |
| Google Antigravity / Antigravity CLI | `dist/gemini/GEMINI.md` | Use only where Antigravity is configured to load Gemini-style context/rules files. | No repo-enforced product upload or runtime limit. | Documentation-only compatibility note; no product smoke test. | [Antigravity rules docs](https://antigravity.google/docs/rules-workflows), [Gemini CLI to Antigravity CLI transition](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) |
| Generic Markdown | `dist/general/high-signal-output.md` | System prompt, style guide, or agent instruction import. | No platform-specific metadata limit. | Generated from the shared body and covered by the drift gate. | Internal repo contract |

## Notes

- Claude Code and Claude.ai are split because their documented description limits differ.
- Gemini CLI consumer availability is changing: Google's 2026-05-19 migration post says
  Antigravity CLI is available now and Gemini CLI consumer requests stop on 2026-06-18, while
  enterprise and paid API-key access remain available. Keep install copy honest about that shift.
- If a product changes its instruction-file contract, update the matching adapter, this matrix,
  `docs/specs/high-signal-output-contract.md`, and the architecture playground in the same change.
