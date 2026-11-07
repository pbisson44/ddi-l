"""Lint configuration passed to one call instead of set for the process."""

from __future__ import annotations

import threading

import pytest

from ddi_l import cli, read_ddi
from ddi_l.document import DDIDocument
from ddi_l.lint import (
    LintFinding,
    get_lint_configuration,
    lint_configuration,
    run_lint,
    run_profile,
)
from tests import SAMPLES_DIR

INSTANCE = SAMPLES_DIR / "minimal_instance.xml"
STRICT = lint_configuration(allowed_agencies=["other.agency"])


def _agency(findings: list[LintFinding]) -> list[LintFinding]:
    return [finding for finding in findings if finding.rule_id == "ddi.agency.allowed"]


def test_a_configuration_applies_to_its_own_call():
    document = read_ddi(INSTANCE)

    assert _agency(run_lint(document, configuration=STRICT))
    assert not _agency(run_lint(document))
    assert get_lint_configuration() == lint_configuration()


def test_run_profile_and_lint_methods_take_a_configuration():
    document = read_ddi(INSTANCE)
    assert isinstance(document, DDIDocument)

    result = run_profile(
        document, "DDI_PROFILE_DEFAULT", include_schema=False, configuration=STRICT
    )

    assert _agency(result.lint_findings)
    assert _agency(document.lint(configuration=STRICT))
    assert not _agency(document.lint())


def test_lint_configuration_starts_from_the_documented_default():
    assert lint_configuration().required_citation_languages == ("en",)
    configured = lint_configuration(required_languages=["fr", "en"])
    assert configured.required_languages == ("fr", "en")
    assert configured.required_citation_languages == ("en",)


def test_lint_configuration_checks_its_options():
    with pytest.raises(TypeError, match="Unknown lint option"):
        lint_configuration(no_such_option=True)
    with pytest.raises(ValueError, match="Invalid lint pattern"):
        lint_configuration(placeholder_patterns=["("])


def test_concurrent_calls_keep_their_own_configuration():
    document = read_ddi(INSTANCE)
    seen: dict[str, list[bool]] = {"strict": [], "default": []}
    start = threading.Barrier(2)

    def lint(name: str) -> None:
        configuration = STRICT if name == "strict" else None
        start.wait()
        for _ in range(25):
            findings = run_lint(document, configuration=configuration)
            seen[name].append(bool(_agency(findings)))

    threads = [threading.Thread(target=lint, args=(name,)) for name in seen]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert seen["strict"] == [True] * 25
    assert seen["default"] == [False] * 25


def test_the_cli_leaves_the_process_configuration_alone(capsys):
    status = cli.main(["lint", str(INSTANCE), "--allowed-agency", "other.agency"])

    assert status == 1
    assert "ddi.agency.allowed" in capsys.readouterr().out
    assert get_lint_configuration() == lint_configuration()
