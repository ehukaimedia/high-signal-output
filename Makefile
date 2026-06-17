# Convenience targets. Windows users without `make` can run the python commands directly.
.PHONY: build check test eval lint all install-all install-claude-code install-claude-ai install-codex install-gemini

build:    ## Generate dist/ from the single source of truth
	python scripts/build.py

check:    ## Verify dist/ is in sync with core/ (CI gate)
	python scripts/build.py --check

test:     ## Run the test suite
	python -m unittest discover -s tests -v

eval:     ## Check illustrative high-signal before/after examples
	python scripts/eval_examples.py --check

lint:     ## Lint the build tooling and tests
	python -m ruff check .

install-claude-code: build   ## Install the Claude Code skill in ~/.claude/skills
	python scripts/install.py --target claude-code

install-claude-ai: build     ## Stage a Claude.ai upload folder under build/
	python scripts/install.py --target claude-ai

install-codex: build         ## Install global Codex guidance in ~/.codex/AGENTS.md
	python scripts/install.py --target codex

install-gemini: build        ## Install global Gemini CLI guidance in ~/.gemini/GEMINI.md
	python scripts/install.py --target gemini

install-all: build           ## Install local Claude Code, Codex, and Gemini targets
	python scripts/install.py --all

all: check test eval lint    ## Run every gate (what CI runs)
