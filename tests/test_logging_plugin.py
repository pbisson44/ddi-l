"""Tests for the custom pytest logging utilities defined in ``tests/conftest``."""

from __future__ import annotations

from pathlib import Path

pytest_plugins = ("pytester",)


def _copy_repo_conftest(pytester) -> None:
    """Ensure the pytester instance uses the repository's test configuration."""

    plugin_code = Path(__file__).with_name("conftest.py").read_text(encoding="utf-8")
    pytester.makeconftest(plugin_code)


def test_failure_details_are_written_to_default_log(pytester) -> None:
    """A failing test should persist its traceback to ``pytest-error.log``."""

    _copy_repo_conftest(pytester)
    pytester.makepyfile(
        """
        def test_fail():
            assert False
        """
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(failed=1)

    log_path = pytester.path / "pytest-error.log"
    assert log_path.exists(), "Expected pytest-error.log to be created"

    contents = log_path.read_text(encoding="utf-8")
    assert "test_fail" in contents
    assert "assert False" in contents

    assert "Stored failure details in" in result.stdout.str()


def test_log_location_honours_environment_variable(pytester, monkeypatch) -> None:
    """When ``PYTEST_ERROR_LOG`` is set, logs should be written to the requested path."""

    _copy_repo_conftest(pytester)
    pytester.makepyfile(
        """
        def test_fail():
            assert False
        """
    )

    monkeypatch.setenv("PYTEST_ERROR_LOG", "logs/failures.log")

    result = pytester.runpytest("-q")
    result.assert_outcomes(failed=1)

    log_path = pytester.path / "logs" / "failures.log"
    assert log_path.exists(), "Expected custom error log to be created"

    contents = log_path.read_text(encoding="utf-8")
    assert "test_fail" in contents


def test_successful_run_does_not_create_error_log(pytester) -> None:
    """Passing tests should not leave behind an error log file."""

    _copy_repo_conftest(pytester)
    pytester.makepyfile(
        """
        def test_pass():
            assert True
        """
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)

    assert not (pytester.path / "pytest-error.log").exists()
