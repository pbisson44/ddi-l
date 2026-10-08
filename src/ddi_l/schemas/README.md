# Bundled DDI Lifecycle schemas

This directory ships inside the `ddi_l` package so that validation works
offline, with no network access and no separate download, from a plain
`pip install ddi-l`.

- **Source:** [DDI Alliance](https://ddialliance.org/)
- **Repository:** <https://github.com/ddialliance/ddi-l_3>
- **Bundled versions:** 3.1, 3.2, and 3.3 (3.3 released 2020-04-15)
- **Contents per version:** 24 DDI-L XSDs, 18 XHTML XSDs, 3 ENT entity files
- **License:** Creative Commons Attribution 4.0 International (CC-BY-4.0).
  See `license.txt` for the full terms and `readme.txt` for the DDI Alliance
  release notes. These files are redistributed with the schemas to satisfy the
  attribution requirement, and must stay in the distribution.

## How the schemas are located

Code resolves them through `importlib.resources`, never through a filesystem
path relative to the repository:

```python
from importlib import resources

resources.files("ddi_l.schemas").joinpath("ddi", "v3_3", "instance_3_3.xsd")
```

`src/ddi_l/schema_loader/_constants.py` holds the package name
(`_SCHEMA_PACKAGE`) and `src/ddi_l/_schema_versions.py` maps each supported
version to its resource path. `make release-check` asserts these files are
present in both the sdist and the wheel, and validates a document from a
clean install, so a packaging regression fails the build.

## Refreshing the bundle

`ddi_l.schema_sync.update_schema_package()` downloads an official release
archive and refreshes this directory in place. Checksums for each known
release live in `SCHEMA_ARCHIVE_CHECKSUMS` in `src/ddi_l/_schema_versions.py`
and must be updated alongside any refresh.
