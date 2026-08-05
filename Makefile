PYTHON ?= .venv/bin/python
MKDOCS ?= .venv/bin/mkdocs

.PHONY: build test

build:
	$(MKDOCS) build --strict

test: build
	$(PYTHON) tests/test_site.py
