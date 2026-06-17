---
name: high-signal-output
description: >-
  Use when tightening PR bodies, status updates, handoffs, summaries, or other long-form coding-
  agent prose without dropping caveats or evidence.
---

# High-Signal Output

**Write so every token earns its place.**

## Overview

**Optimize signal per token.** A token is *signal* if removing it changes what the reader believes
or does. Everything else is fat. Cut the fat; keep all the muscle.

Frugality and quality are the same discipline, not a trade-off. "Be shorter" truncates substance
and fakes confidence. "Raise signal density" forces decisiveness, precision, and verifiability —
quality properties — while deleting tokens that never carried signal. **Shortening that drops
signal is a bug, not frugality.**

Baseline tone: **terse and direct** — a senior engineer briefing a peer who owns the decision.

## Two registers — pick one, skip the mush

Strong output is **bimodal**: either a **terse line** or a **full artifact**, rarely in between.
The terse line covers the large majority of turns; the full artifact is the exception you reserve
for genuine weight.

- **Terse line** (the default) — one or two plain sentences. *No* headers or bullets; structure on
  a one-liner is noise. Lead with the result, name the specifics, point at the next move.
  > `All 38 tests pass; lint flags one fixable issue — fixing and re-running.`

- **Full artifact** (high stakes: a review, recommendation, audit, handoff, PR body) — open with a
  **bolded one-line verdict or recommendation**, then bolded topic-sentences leading each
  paragraph, lists or tables only where they aid navigation, every claim anchored to a `path`,
  count, or commit hash. If an open loop remains, name it in the opener.

The trap is the **mushy middle**: padding a status line into a paragraph to look thorough, or
crushing a real analysis into one dense line. First pick the register the stakes demand, then
maximize signal inside it.

## When to use

- Composing a user-facing long-form artifact: PR/commit body, status update, handoff, release
  note, multi-paragraph summary.
- The reader asks for denser / tighter / sharper / less-verbose output, or to "tighten this".
- As an opt-in self-edit on a long draft before sending.

**Do not apply to:** routine Q&A and short answers; exploratory brainstorming or thinking aloud;
emotionally sensitive replies where warmth matters more than density; anywhere a required format or
safety constraint already governs length (see **Precedence**).

## The moves

Each move cuts no-signal tokens **and** protects a quality property — density never costs substance.

| Move | Cuts | Protects |
|---|---|---|
| **Lead with the verdict** | buildup, throat-clearing | decisiveness — state the conclusion first, then recommend and defend it; reject weaker options by name instead of listing them neutrally |
| **Specifics, made checkable** | vague qualifiers ("robust", "should work") | correctness — backtick identifiers, link files `[name](path)`, cite counts and hashes ("574 tests, 80% cov", `5d66495`) so every claim is verifiable |
| **Cut no-signal tokens** | "Great!", preamble, restatement, reflexive hedging, contentless narration | precision — signal stands out once filler is gone |
| **Pack the sentence; em-dash the qualifier** | padding clauses, weak second sentences | completeness — `claim — why / caveat / consequence` attaches the reason or the caveat without spending a new sentence |
| **Expose the live state** | vague progress narration | coordination — say what is done, what is running, and what you are doing next ("tests running; checking docs while they finish") |
| **Name the open loop** | false completion, buried blockers | trust — surface `not pushed`, `manual smoke test pending`, `auth missing`, or `waiting on approval` where the reader will see it |
| **Structure only when long** | bullets and headers on short output | findability — the terse line stays plain prose; reserve bold topic-sentences and lists for the full artifact |
| **Action-forward close** | recap/summary endings | actionability — end on the next step, what you need, or what you'll do ("not pushed — say the word") |

## Status shape — state, evidence, next

For agent-status prose, use only the slots that change the reader's action:

`state` → `evidence` → `next/open loop`

- `Local gates are green: build, tests, lint. Not pushed — awaiting remote choice.`
- `Integration tests are still running; while they finish, checking docs links and stale refs.`
- `Blocked: remote auth is missing; branch is ready once credentials are fixed.`
- `Findings so far: stale badge, missing security contact, no bad-input test — continuing the audit.`

This keeps progress updates useful without turning them into diary entries.

## Quality guardrail — never compress away

- The **verdict** / recommendation.
- Genuine **caveats, risks, failure modes**.
- **Disambiguating detail** that changes the reader's action.
- The **reasoning** a non-obvious decision rests on.
- Any **open loop** the reader owns or needs to trust: unpushed work, pending manual checks,
  missing credentials, waiting approvals, partial verification.
- **Honest uncertainty** — name it precisely and resolve it ("likely a stale process holding the
  port — checking"), never reflexive hedging, never faked confidence.

**Rule:** if cutting a token changes what the reader believes or does, it was signal — keep it.

**"No disclaimers" means no *empty boilerplate*** (blanket hedges, reflexive "this may not be
perfect", generic safety throat-clearing) — **not** cutting operational caveats, limitations, or
risk-changing detail. Cut boilerplate; keep load-bearing caveats.

## Pre-send pass (opt-in, on a long draft)

1. **Register** — is this the right register for the stakes, or am I in the mushy middle?
2. **Frugality** — can I delete any token without losing a fact, a caveat, or the conclusion?
3. **Quality** — verdict first? every claim specific and traceable? every necessary caveat present?
   next action clear?

## Anti-patterns

- **Bloat:** preamble, restating the prompt, "Great!/Sure!", hedging stacks, narrating obvious
  steps, summary-of-a-summary, vague adjectives.
- **Over-compression:** dropping caveats to look clean, false confidence, ambiguous brevity,
  cutting the reasoning a decision needs, truncating substance to hit a length.
- **Fake closure:** saying "done" while a push, deploy, CI run, approval, or manual smoke test is
  still pending.
- **Diary updates:** "I am going to start by..." / "I will now proceed to..." when the useful fact is
  the current state or next gate.
- **Mushy middle:** a status ping inflated to a paragraph, or a real analysis crushed into one
  line — the wrong register for the stakes.
- **Decoration:** bullets, headers, or bold on output too short to need navigating.

## Precedence

This guidance **yields** to anything that mandates structure or length. Highest first:

1. Reader-required output formats and explicit length requests.
2. Safety constraints and required disclosures — never compress away a needed warning.
3. Domain-specific completeness — audits, legal/compliance, incident reports, post-mortems.
4. Code-review / structured-output / tool / developer-instruction formats.

Apply density *inside* what those mandate, never against it.

## Examples

**Terse register — bloated vs. high-signal (same facts):**
> ❌ Great question! I dug into the failing job and after some investigation I think it should be
> working now — I made a few changes that should address it. Let me know if you need anything else!

> ✅ **Fixed: the job failed on a missing timeout, now set in the config loader.** Tests pass (12/12).
> Caveat: I couldn't reproduce the original failure — treat this as a likely fix, watch the next run
> before closing.

Verdict first; specifics (what failed, where, 12/12); the **caveat kept** (unconfirmed —
load-bearing); action-forward close. Cut: "Great question!", the buildup, the reflexive hedging.

**Full-artifact register — a verdict-first opener:**
> ✅ **Review complete: no blockers, seven should-fix findings found and fixed, one flagged for you,
> all checks re-run green.** Fixes landed as `5d66495` on the branch (not pushed — say the word).

The verdict leads and is quantified; every claim is checkable (`5d66495`, the counts); the open
question is surfaced, not buried ("one flagged for you"); it closes on the decision the reader owns
("not pushed — say the word"). **Keep caveats and specifics; cut filler.**

**Status register — live state without diary prose:**
> ❌ I am now running the tests and will also take a look through the documentation to see whether
> there are any links that might need to be updated while the tests are executing.

> ✅ Tests are running; while they finish, checking docs links and stale references.

The high-signal version gives the reader the state and next useful action. It drops the process
narration.
