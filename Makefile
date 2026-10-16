VENV := .venv
PYTHON := $(VENV)/bin/python
MKDOCS := $(VENV)/bin/mkdocs

# Sibling checkouts live next to the main clone locally and are checked out
# side by side in CI. $(COMMON_DIR) is the main clone's .git directory in
# both cases: the main checkout itself, or the worktree's common dir.
COMMON_DIR := $(shell git rev-parse --git-common-dir 2>/dev/null || echo .git)
SIBLING_DIR := $(abspath $(COMMON_DIR)/../..)
SIBLINGS := epic-cc epic-hal epic-platformio epic-tools

.PHONY: install build serve pre-pr-check check-siblings validate test clean

install: $(MKDOCS)

$(MKDOCS): requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

build: install
	$(MKDOCS) build --strict

serve: install
	$(MKDOCS) serve

check-siblings:
	for repo in $(SIBLINGS); do \
		test -d $(SIBLING_DIR)/$$repo || { echo "missing sibling checkout: $(SIBLING_DIR)/$$repo"; exit 1; }; \
	done

pre-pr-check: check-siblings validate test build

# Section 12 gates. The scripts use stdlib only, so they run on system
# python without the venv; readme_budget only reports, each repository
# enforces its own README.
validate: check-siblings
	python3 scripts/prose_lint.py
	python3 scripts/snippet_sources.py
	python3 scripts/readme_budget.py

test:
	python3 -m unittest discover -t . -s tests

clean:
	rm -rf site $(VENV)
