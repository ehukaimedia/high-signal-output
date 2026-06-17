# Convenience targets. Windows users without `make` can run the python commands directly.
.PHONY: build check test lint all

build:    ## Generate dist/ from the single source of truth
	python scripts/build.py

check:    ## Verify dist/ is in sync with core/ (CI gate)
	python scripts/build.py --check

test:     ## Run the test suite
	python -m unittest discover -s tests -v

lint:     ## Lint the build tooling and tests
	python -m ruff check .

all: check test lint   ## Run every gate (what CI runs)
