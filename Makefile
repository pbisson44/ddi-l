.PHONY: example release-check docs-build docs-serve

example:
	python -m ddi_l.examples.build_and_validate --refresh

# Build both distributions and check their contents and a clean install.
release-check:
	rm -rf dist
	python -m build --sdist --wheel
	python scripts/check_distributions.py dist
	python scripts/check_clean_install.py dist

# NO_MKDOCS_2_WARNING silences Material's advisory banner.
docs-build:
	NO_MKDOCS_2_WARNING=1 mkdocs build --strict

docs-serve:
	NO_MKDOCS_2_WARNING=1 mkdocs serve --strict
