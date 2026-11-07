"""Write the schema IR the native validator reads.

Run from the project root after changing a bundled schema or upgrading
xmlschema::

    uv run python -m codegen.schema_ir

Each version's IR goes to ``src/ddi_l/schemas/ir/v3_X.json.gz``; CI checks
that regenerating it changes nothing.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from ddi_l._schema_versions import SUPPORTED_SCHEMA_VERSIONS
from ddi_l.schema_loader._cache import get_schema
from ddi_l.schema_loader._ir import build

OUTPUT = Path(__file__).resolve().parents[1] / "src" / "ddi_l" / "schemas" / "ir"


def ir_path(version: str, root: Path = OUTPUT) -> Path:
    return root / f"v{version.replace('.', '_')}.json.gz"


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for version in SUPPORTED_SCHEMA_VERSIONS:
        data = build(get_schema(version)).data
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        # mtime=0: the same IR is the same bytes.
        ir_path(version).write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
        print(f"{version}: {ir_path(version).name}, digest {data['digest'][:12]}")
    return 0


if __name__ == "__main__":  # pragma: no cover - a build step
    raise SystemExit(main())
