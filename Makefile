.PHONY: example release-check docs-build docs-serve mutation

example:
	python -m ddi_l.examples.build_and_validate --refresh \
	  --output src/ddi_l/examples/example_instance.xml \
	  --fragment-output src/ddi_l/examples/example_fragment.xml

# Build both distributions and check their contents and a clean install. The
# stand-in wheel for ddi-l-native is built and published with them.
release-check:
	rm -rf dist
	python -m build --sdist --wheel
	python -m build --wheel native/fallback --outdir dist
	python scripts/check_distributions.py dist
	python scripts/check_clean_install.py dist

# NO_MKDOCS_2_WARNING silences Material's advisory banner.
docs-build:
	NO_MKDOCS_2_WARNING=1 mkdocs build --strict

docs-serve:
	NO_MKDOCS_2_WARNING=1 mkdocs serve --strict

# Mutation testing, then the check against tests/mutation_baseline.txt.
mutation:
	mutmut run
	python scripts/check_mutation.py
