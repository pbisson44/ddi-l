"""Runtime benchmarks for the streaming DDI parsers."""

from __future__ import annotations

import argparse
import gc
import io
import statistics
import sys
import textwrap
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

try:
    from ddi_l import iter_variables, iterparse_ddi
except ModuleNotFoundError:  # pragma: no cover - dev helper
    project_root = Path(__file__).resolve().parents[1]
    src_path = project_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    from ddi_l import iter_variables, iterparse_ddi


@dataclass
class BenchmarkResult:
    """Captured metrics for a single benchmark variant."""

    label: str
    maintainables: int
    durations: Sequence[float]
    peaks: Sequence[int]

    @property
    def median_duration(self) -> float:
        return statistics.median(self.durations)

    @property
    def best_duration(self) -> float:
        return min(self.durations)

    @property
    def median_peak(self) -> int:
        return int(statistics.median(self.peaks))


def _format_bytes(num_bytes: float) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:,.2f} {unit}"
        value /= 1024.0
    return f"{value:,.2f} {units[-1]}"


def build_payload(logical_products: int, variables_per_product: int) -> bytes:
    """Construct a synthetic DDI instance with repeated logical products."""

    if logical_products <= 0:
        raise ValueError("At least one logical product is required.")
    if variables_per_product <= 0:
        raise ValueError("Each logical product must include at least one variable.")

    variable_template = textwrap.dedent(
        """
        <l:Variable>
          <r:Agency>benchmark.agency</r:Agency>
          <r:ID>var-{product}-{variable}</r:ID>
          <r:Version>1.0</r:Version>
          <l:VariableName>
            <r:String xml:lang="en">Benchmark variable {product}-{variable}</r:String>
          </l:VariableName>
        </l:Variable>
        """
    ).strip()

    logical_products_xml: list[str] = []
    for product in range(logical_products):
        variables = "\n".join(
            variable_template.format(product=product, variable=index)
            for index in range(variables_per_product)
        )
        logical_product = textwrap.dedent(
            """
            <l:LogicalProduct>
              <r:Agency>benchmark.agency</r:Agency>
              <r:ID>logical-{product}</r:ID>
              <r:Version>1.0</r:Version>
              <l:VariableScheme>
                <r:Agency>benchmark.agency</r:Agency>
                <r:ID>logical-{product}-variable-scheme</r:ID>
                <r:Version>1.0</r:Version>
                {variables}
              </l:VariableScheme>
            </l:LogicalProduct>
            """
        ).format(product=product, variables=variables)
        logical_products_xml.append(logical_product.strip())

    body = "\n  ".join(logical_products_xml)
    document = textwrap.dedent(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <DDIInstance xmlns="ddi:instance:3_3"
                     xmlns:l="ddi:logicalproduct:3_3"
                     xmlns:r="ddi:reusable:3_3"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <r:Agency>benchmark.agency</r:Agency>
          <r:ID>benchmark-instance</r:ID>
          <r:Version>1.0</r:Version>
          {body}
        </DDIInstance>
        """
    ).strip()
    return document.encode("utf-8")


def _consume(
    iterator: Callable[[io.BytesIO], Iterable[object]], payload: bytes
) -> tuple[int, float, int]:
    import tracemalloc

    tracemalloc.start()
    start = time.perf_counter()
    count = 0
    for _ in iterator(io.BytesIO(payload)):
        count += 1
    duration = time.perf_counter() - start
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return count, duration, peak


def verify_payload(payload: bytes, *, expected_variables: int) -> None:
    """Check the streamed objects are complete, not just correctly counted."""

    streamed = sum(1 for _ in iter_variables(io.BytesIO(payload)))
    nested = sum(
        len(item.variables)
        for item in iterparse_ddi(io.BytesIO(payload))
        if type(item).__name__ == "LogicalProduct"
    )
    if streamed != expected_variables or nested != expected_variables:
        raise RuntimeError(
            f"Expected {expected_variables} variables; iter_variables yielded "
            f"{streamed} and the streamed LogicalProducts held {nested}."
        )


def run_benchmark(
    *,
    payload: bytes,
    label: str,
    iterator: Callable[[io.BytesIO], Iterable[object]],
    warmup: int,
    trials: int,
) -> BenchmarkResult:
    for _ in range(warmup):
        _consume(iterator, payload)
        gc.collect()

    counts: list[int] = []
    durations: list[float] = []
    peaks: list[int] = []

    for _ in range(trials):
        count, duration, peak = _consume(iterator, payload)
        counts.append(count)
        durations.append(duration)
        peaks.append(peak)
        gc.collect()

    if len(set(counts)) != 1:
        raise RuntimeError(
            f"Benchmark for {label!r} yielded inconsistent counts: {counts}."
        )

    return BenchmarkResult(
        label=label, maintainables=counts[0], durations=durations, peaks=peaks
    )


def describe_results(
    *,
    payload: bytes,
    logical_products: int,
    variables_per_product: int,
    results: Sequence[BenchmarkResult],
) -> None:
    payload_size = len(payload)
    print("Benchmark results")
    print("=================")
    print(f"Logical products: {logical_products}")
    print(f"Variables per product: {variables_per_product}")
    print(f"Total variables: {logical_products * variables_per_product}")
    print(f"Payload size: {_format_bytes(payload_size)}")

    for result in results:
        median_duration = result.median_duration
        best_duration = result.best_duration
        median_peak = result.median_peak
        throughput = (
            result.maintainables / median_duration if median_duration else float("inf")
        )
        bytes_per_second = (
            payload_size / median_duration if median_duration else float("inf")
        )
        print()
        print(result.label)
        print("-" * len(result.label))
        print(f"Maintainables parsed: {result.maintainables}")
        print(
            "Durations (s): "
            f"median={median_duration:.4f}, best={best_duration:.4f}, "
            f"runs={[f'{duration:.4f}' for duration in result.durations]}"
        )
        print(
            f"Throughput: {throughput:,.1f} maintainables/s, {bytes_per_second / 1024 / 1024:,.2f} MiB/s"
        )
        print(f"Median peak memory: {_format_bytes(median_peak)}")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark the iterparse helpers against synthetic DDI instances."
    )
    parser.add_argument(
        "--logical-products",
        type=int,
        default=4,
        help="Number of logical products to embed in the synthetic instance.",
    )
    parser.add_argument(
        "--variables-per-product",
        type=int,
        default=500,
        help="Number of variables per logical product.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Number of warm-up runs to execute before capturing metrics.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=3,
        help="Number of timed trials to record for each benchmark.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    payload = build_payload(args.logical_products, args.variables_per_product)

    logical_products = args.logical_products
    variables = args.variables_per_product
    total_variables = logical_products * variables
    print("Configured synthetic workload")
    print("------------------------------")
    print(f"Logical products: {logical_products}")
    print(f"Variables per product: {variables}")
    print(f"Total variables: {total_variables}")
    print(f"Payload size: {_format_bytes(len(payload))}\n")
    verify_payload(payload, expected_variables=total_variables)

    results = [
        run_benchmark(
            payload=payload,
            label="iterparse_ddi",
            iterator=iterparse_ddi,
            warmup=args.warmup,
            trials=args.trials,
        ),
        run_benchmark(
            payload=payload,
            label="iter_variables",
            iterator=iter_variables,
            warmup=args.warmup,
            trials=args.trials,
        ),
    ]

    describe_results(
        payload=payload,
        logical_products=logical_products,
        variables_per_product=variables,
        results=results,
    )


if __name__ == "__main__":
    main()
