.PHONY: example release-check docs-build docs-serve mutation

example:
	python -m ddi_l.examples.build_and_validate --refresh \
	  --output src/ddi_l/examples/example_instance.xml \
	  --fragment-output src/ddi_l/examples/example_fragment.xml

# Build both distributions and check their contents and a clean install. The
# stand-in wheel for ddi-l-native is built and published with them. Every step
# is a Python command, so the target runs from Windows too (`uv run make
# release-check`), where make hands recipes to cmd.exe and `rm` does not exist.
release-check:
	python -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"
	python -m build --sdist --wheel
	python -m build --wheel native/fallback --outdir dist
	python scripts/check_distributions.py dist
	python scripts/check_clean_install.py dist

# Both languages into site/; `serve` previews English (add `--lang fr`).
docs-build:
	python scripts/docs.py build --strict

docs-serve:
	python scripts/docs.py serve

# Mutation testing, then the check against tests/mutation_baseline.txt.
mutation:
	mutmut run
	python scripts/check_mutation.py
