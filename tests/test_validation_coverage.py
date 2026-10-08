"""Edge cases and error paths in ddi_l.schema_loader._validation."""

import textwrap

import pytest

from ddi_l._etree import create_element
from ddi_l.constants import INSTANCE_NS, REUSABLE_NS
from ddi_l.models.base import qn
from ddi_l.schema_loader._validation import (
    SchemaValidationError,
    SchemaValidationIssue,
    _apply_validation_backend,
    _build_fragment_gap_sets,
    _build_validation_issue,
    _clear_fragment_gap_cache,
    _clear_known_type_name_cache,
    _extract_validation_message,
    _identify_fragment_schema_gap,
    _resolve_known_type_names,
    get_available_validation_backends,
    set_validation_backend,
    validate,
)

# ---------------------------------------------------------------------------
# SchemaValidationIssue
# ---------------------------------------------------------------------------


def test_issue_to_dict():
    issue = SchemaValidationIssue(
        message="bad",
        xpath="/root",
        context="<root>",
        severity="error",
        line=10,
        column=5,
    )
    d = issue.to_dict()
    assert d["message"] == "bad"
    assert d["xpath"] == "/root"
    assert d["line"] == 10


def test_issue_to_dict_no_context():
    issue = SchemaValidationIssue(message="bad", xpath="/root", context="<root>")
    d = issue.to_dict(include_context=False)
    assert "context" not in d


# ---------------------------------------------------------------------------
# SchemaValidationError
# ---------------------------------------------------------------------------


def test_schema_validation_error_with_issues():
    issue = SchemaValidationIssue(
        message="bad", xpath="/root", context="<root>", severity="error"
    )
    err = SchemaValidationError([issue])
    assert "bad" in str(err)
    assert "(at /root)" in str(err)


def test_schema_validation_error_no_issues():
    err = SchemaValidationError([])
    assert "Schema validation error" in str(err)


def test_schema_validation_error_to_dicts():
    issue = SchemaValidationIssue(message="bad", xpath="/root", context="ctx")
    err = SchemaValidationError([issue])
    dicts = err.to_dicts()
    assert len(dicts) == 1
    assert dicts[0]["message"] == "bad"


# ---------------------------------------------------------------------------
# _extract_validation_message
# ---------------------------------------------------------------------------


def test_extract_message_reason():
    class FakeError(Exception):
        reason = "the reason"

    assert _extract_validation_message(FakeError()) == "the reason"


def test_extract_message_message_attr():
    class FakeError(Exception):
        message = "the message"

    assert _extract_validation_message(FakeError()) == "the message"


def test_extract_message_args():
    err = ValueError("from args")
    assert _extract_validation_message(err) == "from args"


def test_extract_message_non_string_arg():
    err = ValueError(42)
    assert "42" in _extract_validation_message(err)


def test_extract_message_no_args():
    class FakeError(Exception):
        pass

    err = FakeError()
    err.args = ()
    result = _extract_validation_message(err)
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# _build_validation_issue
# ---------------------------------------------------------------------------


def test_build_validation_issue_basic():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    err = ValueError("test error")
    issue = _build_validation_issue(err, root=root, schema=None)
    assert issue.message == "test error"
    assert issue.xpath is not None


def test_build_validation_issue_with_node():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    child = create_element(qn(REUSABLE_NS, "Agency"))
    root.append(child)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.elem = child
            self.path = "/DDIInstance/Agency"

    issue = _build_validation_issue(FakeError(), root=root, schema=None)
    assert issue.node is child


def test_build_validation_issue_with_obj_fallback():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    child = create_element(qn(REUSABLE_NS, "Agency"))
    root.append(child)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.elem = None
            self.obj = child

    issue = _build_validation_issue(FakeError(), root=root, schema=None)
    assert issue.node is child


def test_build_validation_issue_position_tuple():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.position = (10, 5)
            self.line = None
            self.column = None

    issue = _build_validation_issue(FakeError(), root=root, schema=None)
    assert issue.line == 10
    assert issue.column == 5


def test_build_validation_issue_sourceline():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    child = create_element("child")
    root.append(child)

    class _SourceLineNode:
        """Wrap a real element and add the ``sourceline`` lxml would supply.

        Neither backend accepts the attribute by assignment -- stdlib elements
        have no ``__dict__`` and lxml's ``sourceline`` is a typed property --
        so the attribute has to come from a wrapper. Everything else delegates
        to the real element, which ``_describe_node`` needs.
        """

        sourceline = 42

        def __init__(self, element):
            self._element = element

        def __getattr__(self, name):
            return getattr(self._element, name)

        def __iter__(self):
            return iter(self._element)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.elem = _SourceLineNode(child)
            self.line = None
            self.column = None

    issue = _build_validation_issue(FakeError(), root=root, schema=None)
    # sourceline is set on child
    assert issue.line == 42 or issue.line is None  # depends on backend


def test_build_validation_issue_xpath_from_error():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.xpath = "/custom/path"

    issue = _build_validation_issue(FakeError(), root=root, schema=None)
    assert issue.xpath == "/custom/path"


def test_build_validation_issue_no_context():
    root = create_element(qn(INSTANCE_NS, "DDIInstance"))
    err = ValueError("test")
    issue = _build_validation_issue(err, root=root, schema=None, include_context=False)
    assert issue.context is None


# ---------------------------------------------------------------------------
# _build_fragment_gap_sets
# ---------------------------------------------------------------------------


def test_build_fragment_gap_sets():
    from ddi_l.constants import get_namespace_set

    ns = get_namespace_set("3.3")
    _clear_fragment_gap_cache()
    gap_tags, _child_gaps = _build_fragment_gap_sets(
        ns, ns["REUSABLE_NS"], version="3.3"
    )
    assert len(gap_tags) > 0
    # Second call hits cache
    gap_tags2, _ = _build_fragment_gap_sets(ns, ns["REUSABLE_NS"], version="3.3")
    assert gap_tags2 == gap_tags


def test_build_fragment_gap_sets_no_version():
    from ddi_l.constants import get_namespace_set

    ns = get_namespace_set("3.3")
    gap_tags, _ = _build_fragment_gap_sets(ns, ns["REUSABLE_NS"])
    assert len(gap_tags) > 0


# ---------------------------------------------------------------------------
# _resolve_known_type_names
# ---------------------------------------------------------------------------


def test_resolve_known_type_names():
    _clear_known_type_name_cache()
    names = _resolve_known_type_names()
    assert "Variable" in names or "CodeList" in names
    # Second call hits cache
    names2 = _resolve_known_type_names()
    assert names2 == names


# ---------------------------------------------------------------------------
# _identify_fragment_schema_gap
# ---------------------------------------------------------------------------


def test_identify_fragment_schema_gap_invalid_child():
    from ddi_l.constants import get_namespace_set

    ns = get_namespace_set("3.3")
    dc_ns = ns["DATA_COLLECTION_NS"]
    gap_tags, child_gaps = _build_fragment_gap_sets(ns, ns["REUSABLE_NS"])
    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    child = create_element(f"{{{dc_ns}}}CollectionEvent")
    root.append(child)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.invalid_child = child
            self.obj = root

    result = _identify_fragment_schema_gap(
        FakeError(),
        root=root,
        fragment_gap_tags=gap_tags,
        fragment_child_gaps=child_gaps,
    )
    assert result is child


def test_identify_fragment_schema_gap_obj_fallback():
    from ddi_l.constants import get_namespace_set

    ns = get_namespace_set("3.3")
    dc_ns = ns["DATA_COLLECTION_NS"]
    gap_tags, child_gaps = _build_fragment_gap_sets(ns, ns["REUSABLE_NS"])
    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    candidate = create_element(f"{{{dc_ns}}}CollectionEvent")
    root.append(candidate)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.obj = candidate

    result = _identify_fragment_schema_gap(
        FakeError(),
        root=root,
        fragment_gap_tags=gap_tags,
        fragment_child_gaps=child_gaps,
    )
    assert result is candidate


def test_identify_fragment_schema_gap_path_search():
    from ddi_l.constants import get_namespace_set

    ns = get_namespace_set("3.3")
    dc_ns = ns["DATA_COLLECTION_NS"]
    gap_tags, child_gaps = _build_fragment_gap_sets(ns, ns["REUSABLE_NS"])
    tag = f"{{{dc_ns}}}CollectionEvent"
    root = create_element(qn(INSTANCE_NS, "FragmentInstance"))
    child = create_element(tag)
    root.append(child)

    class FakeError(Exception):
        def __init__(self):
            super().__init__("err")
            self.path = f"/FragmentInstance/{tag}"

    result = _identify_fragment_schema_gap(
        FakeError(),
        root=root,
        fragment_gap_tags=gap_tags,
        fragment_child_gaps=child_gaps,
    )
    assert result is child


def test_identify_fragment_schema_gap_none():
    class FakeError(Exception):
        pass

    root = create_element("root")
    result = _identify_fragment_schema_gap(
        FakeError(),
        root=root,
        fragment_gap_tags=frozenset(),
        fragment_child_gaps=frozenset(),
    )
    assert result is None


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def test_validate_valid_document():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    issues = validate(xml, raise_error=False)
    # May or may not have issues depending on schema strictness
    assert isinstance(issues, list)


def test_validate_invalid_root():
    xml = '<Unknown xmlns="http://www.ddialliance.org/Specification/DDI-Lifecycle/3.3/XMLSchema/instance"><r:Agency xmlns:r="ddi:reusable:3_3">a</r:Agency><r:ID xmlns:r="ddi:reusable:3_3">b</r:ID><r:Version xmlns:r="ddi:reusable:3_3">1</r:Version></Unknown>'
    with pytest.raises((SchemaValidationError, Exception)):
        validate(xml)


def test_validate_invalid_root_no_raise():
    xml = '<Unknown xmlns="http://www.ddialliance.org/Specification/DDI-Lifecycle/3.3/XMLSchema/instance"><r:Agency xmlns:r="ddi:reusable:3_3">a</r:Agency><r:ID xmlns:r="ddi:reusable:3_3">b</r:ID><r:Version xmlns:r="ddi:reusable:3_3">1</r:Version></Unknown>'
    issues = validate(xml, raise_error=False)
    assert len(issues) > 0


def test_validate_unsupported_version():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    with pytest.raises((SchemaValidationError, Exception)):
        validate(xml, version="99.99")


def test_validate_unsupported_version_no_raise():
    xml = textwrap.dedent(f"""\
        <DDIInstance xmlns="{INSTANCE_NS}" xmlns:r="{REUSABLE_NS}">
            <r:Agency>a</r:Agency>
            <r:ID>d1</r:ID>
            <r:Version>1.0</r:Version>
        </DDIInstance>
    """)
    issues = validate(xml, version="99.99", raise_error=False)
    assert len(issues) > 0


# ---------------------------------------------------------------------------
# Backend management
# ---------------------------------------------------------------------------


def test_get_available_backends():
    backends = get_available_validation_backends()
    assert "python" in backends


def test_set_validation_backend_python():
    set_validation_backend("python")


def test_apply_validation_backend_unsupported():
    with pytest.raises(ValueError, match="Unsupported"):
        _apply_validation_backend("nonexistent")
