#!/usr/bin/env python
"""ddi-l demo suite runner

This script runs all demos in sequence or allows running individual demos.

Usage:
    python run_demos.py          # Run all demos
    python run_demos.py 1        # Run demo 1 only
    python run_demos.py 1 3 5    # Run demos 1, 3, and 5
    python run_demos.py --list   # List available demos
"""

import importlib.util
import os
import sys
from pathlib import Path

DEMOS = {
    1: ("demo1_basic_document.py", "Basic DDI Document Creation"),
    2: ("demo2_study_unit.py", "Working with StudyUnits"),
    3: ("demo3_variables.py", "Variables and Code Lists"),
    4: ("demo4_questions.py", "Questions and Data Collection"),
    5: ("demo5_reading.py", "Reading and Parsing DDI Documents"),
    6: ("demo6_validation.py", "Validation and Schema Compliance"),
    7: ("demo7_advanced.py", "Advanced Features"),
    8: ("demo8_http_api.py", "The HTTP API (needs the 'server' extra)"),
}


def list_demos():
    """Print available demos."""
    print("\nAvailable Demos:")
    print("-" * 50)
    for num, (filename, description) in DEMOS.items():
        print(f"  {num}. {description}")
        print(f"     File: {filename}")
    print()


def run_demo(demo_num: int) -> bool:
    """Run a specific demo by number."""
    if demo_num not in DEMOS:
        print(f"Error: Demo {demo_num} not found")
        return False

    filename, description = DEMOS[demo_num]
    demo_path = Path(__file__).parent / filename

    if not demo_path.exists():
        print(f"Error: {filename} not found")
        return False

    print(f"\n{'#' * 70}")
    print(f"# Running Demo {demo_num}: {description}")
    print(f"{'#' * 70}")

    try:
        # Load and execute the demo module
        spec = importlib.util.spec_from_file_location(f"demo{demo_num}", demo_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run the main function if it exists
        if hasattr(module, "main"):
            module.main()

        return True
    except Exception as e:
        print(f"\nError running demo {demo_num}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> int:
    """Run the requested demos and return a process exit status.

    Returns:
        ``0`` when every demo requested ran successfully, ``1`` otherwise -- a
        summary that says "5/7 passed" is worthless to CI or a shell if the
        process still exits 0.
    """
    # Create output directory. Honour DDI_DEMO_OUTPUT_DIR the way each demo
    # does, so the summary reports where the files actually went rather than
    # where they would have gone by default.
    override = os.environ.get("DDI_DEMO_OUTPUT_DIR")
    output_dir = Path(override) if override else Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse arguments
    args = sys.argv[1:]

    if not args:
        # Run all demos
        print("=" * 70)
        print("ddi-l demo suite")
        print("=" * 70)
        print("\nRunning all demos...")

        results = {}
        for demo_num in sorted(DEMOS.keys()):
            success = run_demo(demo_num)
            results[demo_num] = success
            print("\n")

        # Summary
        print("=" * 70)
        print("Demo Suite Summary")
        print("=" * 70)
        for demo_num, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            _, description = DEMOS[demo_num]
            print(f"  Demo {demo_num}: {status} - {description}")

        total = len(results)
        passed = sum(results.values())
        print(f"\nTotal: {passed}/{total} demos passed")
        print(f"\nOutput files saved to: {output_dir}")
        return 0 if passed == total else 1

    elif args[0] == "--list":
        list_demos()
        return 0

    elif args[0] == "--help" or args[0] == "-h":
        print(__doc__)
        list_demos()
        return 0

    else:
        # Run specific demos
        failures = 0
        for arg in args:
            try:
                demo_num = int(arg)
            except ValueError:
                print(f"Error: '{arg}' is not a valid demo number")
                list_demos()
                return 2
            if not run_demo(demo_num):
                failures += 1
        return 1 if failures else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
