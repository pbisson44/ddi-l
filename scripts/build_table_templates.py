"""Write the spreadsheet templates offered on the documentation site.

Run after changing the tables in ``ddi_l.tables``; ``tests/test_tables.py``
fails while the committed downloads differ from what this writes.

    uv run python scripts/build_table_templates.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from ddi_l.tables import write_table_templates

DOWNLOADS = Path(__file__).resolve().parent.parent / "docs" / "downloads"

# File name -> write_table_templates() arguments.
FILES: dict[str, dict[str, object]] = {
    "ddi-tables-template.xlsx": {"layout": "xlsx"},
    "ddi-tables-template.zip": {"layout": "zip"},
    "ddi-tables-example.xlsx": {"layout": "xlsx", "example": True},
    "ddi-tables-example.zip": {"layout": "zip", "example": True},
}


def build(destination: Path = DOWNLOADS) -> list[Path]:
    """Write every download into ``destination``."""
    return [
        write_table_templates(destination / name, **arguments)  # type: ignore[arg-type]
        for name, arguments in FILES.items()
    ]


if __name__ == "__main__":
    for path in build():
        print(path.relative_to(DOWNLOADS.parent.parent), file=sys.stderr)
