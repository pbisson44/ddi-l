"""Pytest configuration that enables consistent logging across the test suite."""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from importlib import resources
from pathlib import Path

import pytest

from tests.helpers import maintainable_fixtures

_DEFAULT_LEVEL = os.getenv("PYTEST_LOG_LEVEL", "INFO").upper()
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_ERROR_LOG_ENV_VAR = "PYTEST_ERROR_LOG"
_DEFAULT_ERROR_LOG = Path("pytest-error.log")
_ERROR_LOG_CONFIG_KEY = "_pytest_error_log_path"


@pytest.fixture(scope="session")
def examples_dir() -> Iterator[Path]:
    """Provide access to packaged example assets within ``ddi_l``."""

    resource = resources.files("ddi_l").joinpath("examples")
    with resources.as_file(resource) as path:
        yield path


@pytest.fixture(scope="session")
def fixtures_dir(examples_dir: Path) -> Path:
    """Return the directory containing XML fixtures bundled with the package."""

    return examples_dir / "tests" / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def configure_fixture_directory(fixtures_dir: Path) -> Iterator[None]:
    """Synchronize helper modules with the packaged fixture location."""

    maintainable_fixtures.MODEL_FIXTURE_DIR = fixtures_dir / "models"
    yield


@pytest.fixture(autouse=True)
def restore_lint_registries() -> Iterator[None]:
    """Undo lint rules and profiles a test registers.

    ``ddi_l.lint`` keeps its rules in module-level dicts, and there is no public
    way to unregister one, so a test that calls ``register_rule`` changes what
    ``run_lint`` does for every test that follows it. That is not hypothetical:
    a custom rule registered in ``tests/test_lint.py`` leaked into the HTTP API's
    example assertions, which passed in isolation and failed in a full run --
    the worst shape a test failure can take.

    Restoring the two dicts around every test also makes ``register_rule``'s
    "already registered" guard survive a second run in the same process.
    """
    from ddi_l import lint

    rules = dict(lint._REGISTRY)
    profiles = dict(lint._PROFILE_REGISTRY)
    try:
        yield
    finally:
        lint._REGISTRY.clear()
        lint._REGISTRY.update(rules)
        lint._PROFILE_REGISTRY.clear()
        lint._PROFILE_REGISTRY.update(profiles)


def _configure_root_logger(level_name: str) -> None:
    """Ensure the root logger uses the desired level and format.

    Args:
        level_name: String representation of the desired logging level.
    """

    level = getattr(logging, level_name, logging.INFO)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(level=level, format=_LOG_FORMAT)
    else:
        root_logger.setLevel(level)
        formatter = logging.Formatter(_LOG_FORMAT)
        for handler in root_logger.handlers:
            handler.setLevel(level)
            handler.setFormatter(formatter)


_configure_root_logger(_DEFAULT_LEVEL)


@pytest.fixture(autouse=True)
def log_test_execution(request: pytest.FixtureRequest) -> Iterator[None]:
    """Log the start and completion of every test for easier debugging."""

    logger = logging.getLogger(request.node.module.__name__)
    logger.info("Starting test %s", request.node.name)
    try:
        yield
    finally:
        logger.info("Finished test %s", request.node.name)


def _resolve_error_log_path(config: pytest.Config) -> Path:
    """Return the fully-qualified path for storing pytest error output."""

    raw_path = os.getenv(_ERROR_LOG_ENV_VAR, str(_DEFAULT_ERROR_LOG))
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path(config.rootpath) / path
    return path


def pytest_configure(config: pytest.Config) -> None:
    """Prepare the error log location before the test session starts."""

    path = _resolve_error_log_path(config)
    setattr(config, _ERROR_LOG_CONFIG_KEY, path)
    if path.exists():
        path.unlink()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Persist failure details into a log file to keep console output concise."""

    path = getattr(session.config, _ERROR_LOG_CONFIG_KEY, None)
    if path is None:
        return

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    if reporter is None:
        return

    reports = reporter.getreports("failed") + reporter.getreports("error")
    if not reports:
        return

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as log_file:
        for index, report in enumerate(reports):
            when = getattr(report, "when", "call")
            log_file.write(f"{report.nodeid} [{when}]\n")

            longreprtext = getattr(report, "longreprtext", None)
            if longreprtext:
                log_file.write(longreprtext)
            else:
                log_file.write(str(report.longrepr))

            if index < len(reports) - 1:
                log_file.write("\n" + "=" * 80 + "\n\n")

    reporter.write_sep("=", f"Stored failure details in {path}")
