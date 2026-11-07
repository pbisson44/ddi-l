"""Time reading, writing and linting one file on the active XML backend.

Run from the project root, once per backend::

    DDI_L_XML_BACKEND=native uv run python benchmarks/backends_bench.py FILE
    DDI_L_XML_BACKEND=lxml uv run python benchmarks/backends_bench.py FILE
    DDI_L_XML_BACKEND=stdlib uv run python benchmarks/backends_bench.py FILE

Each step reports its best time over ``--repeat`` runs, except the first
write (which builds the source index) and the profile lint (run once). On
the native backend the parse is also compared with a copy of the bytes.
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from collections.abc import Callable
from pathlib import Path

try:  # pragma: no cover - helper for direct execution
    from ddi_l import _etree, read_ddi, write_ddi
except ModuleNotFoundError:  # pragma: no cover - development convenience
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from ddi_l import _etree, read_ddi, write_ddi
from ddi_l.lint import COLECTICA_QUESTIONNAIRE_PROFILE, run_profile


def _best(step: Callable[[], object], repeat: int) -> float:
    times = []
    for _ in range(repeat):
        gc.collect()
        start = time.perf_counter()
        step()
        times.append(time.perf_counter() - start)
    return min(times)


def main(argv: list[str] | None = None) -> int:
    """Print one line per step: its name and its time in seconds."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path)
    parser.add_argument("--repeat", type=int, default=5)
    args = parser.parse_args(argv)
    data = args.path.read_bytes()
    megabytes = len(data) / 1e6

    print(f"backend: {_etree.BACKEND}, {megabytes:.1f} MB")
    parse = _best(lambda: _etree.fromstring(data), args.repeat)
    print(f"parse            {parse:8.3f} s  {megabytes / parse:6.0f} MB/s")
    if _etree.NATIVE:
        import ddi_l_native

        raw = _best(lambda: ddi_l_native.parse(data), args.repeat)
        copy = _best(lambda: bytearray(data), args.repeat)
        print(f"  native parse   {raw:8.3f} s  {megabytes / raw:6.0f} MB/s")
        print(f"  copy of bytes  {copy:8.3f} s  {megabytes / copy:6.0f} MB/s")
    print(f"read_ddi         {_best(lambda: read_ddi(data), args.repeat):8.3f} s")

    document = read_ddi(data)
    start = time.perf_counter()
    write_ddi(document)
    print(f"write (first)    {time.perf_counter() - start:8.3f} s")
    print(f"write (again)    {_best(lambda: write_ddi(document), args.repeat):8.3f} s")
    edited = next(document.root.iter())
    edited.set("edited", "yes")
    print(f"write (edited)   {_best(lambda: write_ddi(document), args.repeat):8.3f} s")
    layout = _best(lambda: write_ddi(document, layout="default"), 1)
    print(f"write (layout)   {layout:8.3f} s")

    fresh = read_ddi(data)
    lint = _best(
        lambda: run_profile(
            fresh, COLECTICA_QUESTIONNAIRE_PROFILE, include_schema=False
        ),
        1,
    )
    print(f"lint (profile)   {lint:8.3f} s")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual benchmark
    raise SystemExit(main())
