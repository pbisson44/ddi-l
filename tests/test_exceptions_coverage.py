"""Edge cases and error paths in ddi_l.exceptions."""

import io

from ddi_l.exceptions import (
    DDIError,
    DDIParseError,
    DDIReadError,
    DDIReferenceError,
    DDIValidationError,
    DDIWriteError,
    ErrorLocation,
    ModelBuildError,
    ModelValidationError,
    _coerce_filename,
    _string_looks_like_xml,
    build_error_location,
    element_xpath,
    location_from_element,
    location_from_source,
)

# ---------------------------------------------------------------------------
# _string_looks_like_xml
# ---------------------------------------------------------------------------


def test_string_looks_like_xml_true():
    assert _string_looks_like_xml("<root/>") is True


def test_string_looks_like_xml_with_whitespace():
    assert _string_looks_like_xml("  <root/>") is True


def test_string_looks_like_xml_false():
    assert _string_looks_like_xml("not xml") is False


def test_string_looks_like_xml_empty():
    assert _string_looks_like_xml("") is False


def test_string_looks_like_xml_whitespace_only():
    assert _string_looks_like_xml("   ") is False


# ---------------------------------------------------------------------------
# _coerce_filename
# ---------------------------------------------------------------------------


def test_coerce_filename_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    assert _coerce_filename(p) == str(p)


def test_coerce_filename_str_existing(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    assert _coerce_filename(str(p)) == str(p)


def test_coerce_filename_str_xml_content():
    assert _coerce_filename("<root/>") is None


def test_coerce_filename_str_nonexistent():
    assert _coerce_filename("/nonexistent/path/abc123.xml") is None


def test_coerce_filename_file_object(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    with open(p) as f:
        assert _coerce_filename(f) == str(p)


def test_coerce_filename_named_stream():
    stream = io.BytesIO(b"<root/>")
    stream.name = "my_file.xml"
    assert _coerce_filename(stream) == "my_file.xml"


def test_coerce_filename_unnamed_stream():
    stream = io.BytesIO(b"<root/>")
    assert _coerce_filename(stream) is None


def test_coerce_filename_none():
    assert _coerce_filename(None) is None


def test_coerce_filename_int():
    assert _coerce_filename(42) is None


# ---------------------------------------------------------------------------
# ErrorLocation
# ---------------------------------------------------------------------------


def test_error_location_describe_filename_line_column():
    loc = ErrorLocation(filename="test.xml", line=10, column=5)
    assert loc.describe() == "test.xml:10:5"


def test_error_location_describe_filename_line():
    loc = ErrorLocation(filename="test.xml", line=10)
    assert loc.describe() == "test.xml:10"


def test_error_location_describe_filename_only():
    loc = ErrorLocation(filename="test.xml")
    assert loc.describe() == "test.xml"


def test_error_location_describe_line_column_no_filename():
    loc = ErrorLocation(line=10, column=5)
    assert loc.describe() == "line 10, column 5"


def test_error_location_describe_line_no_filename():
    loc = ErrorLocation(line=10)
    assert loc.describe() == "line 10"


def test_error_location_describe_column_only():
    loc = ErrorLocation(column=5)
    assert loc.describe() == "column 5"


def test_error_location_describe_xpath():
    loc = ErrorLocation(xpath="/root/child")
    assert loc.describe() == "xpath /root/child"


def test_error_location_describe_element_tag_no_xpath():
    loc = ErrorLocation(element_tag="MyElement")
    assert loc.describe() == "element <MyElement>"


def test_error_location_describe_empty():
    loc = ErrorLocation()
    assert loc.describe() is None


def test_error_location_merge_with_none():
    loc = ErrorLocation(filename="a.xml")
    assert loc.merge(None) is loc


def test_error_location_merge_fills_gaps():
    a = ErrorLocation(filename="a.xml")
    b = ErrorLocation(line=10, xpath="/root")
    merged = a.merge(b)
    assert merged.filename == "a.xml"
    assert merged.line == 10
    assert merged.xpath == "/root"


def test_error_location_combine_all_none():
    assert ErrorLocation.combine(None, None) is None


def test_error_location_combine_single():
    loc = ErrorLocation(line=5)
    assert ErrorLocation.combine(None, loc, None) is not None
    assert ErrorLocation.combine(None, loc, None).line == 5  # type: ignore[union-attr]


def test_error_location_from_element_none():
    assert ErrorLocation.from_element(None) is None


def test_error_location_from_element_with_tag():
    class FakeElement:
        tag = "{http://ns}MyTag"
        sourceline = 42
        sourcecolumn = None

    loc = ErrorLocation.from_element(FakeElement())
    assert loc is not None
    assert loc.element_tag == "MyTag"
    assert loc.line == 42


def test_error_location_from_element_plain_tag():
    class FakeElement:
        tag = "SimpleTag"
        sourceline = None
        sourcecolumn = None

    loc = ErrorLocation.from_element(FakeElement())
    assert loc is not None
    assert loc.element_tag == "SimpleTag"


def test_error_location_from_element_no_info():
    class FakeElement:
        tag = None
        sourceline = None
        sourcecolumn = None

    loc = ErrorLocation.from_element(FakeElement())
    assert loc is None


def test_error_location_from_issue():
    class FakeIssue:
        xpath = "/root"
        line = 10
        column = 5

    loc = ErrorLocation.from_issue(FakeIssue())  # type: ignore[arg-type]
    assert loc is not None
    assert loc.xpath == "/root"
    assert loc.line == 10


def test_error_location_from_issue_empty():
    class FakeIssue:
        xpath = None
        line = None
        column = None

    assert ErrorLocation.from_issue(FakeIssue()) is None  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# location_from_element / location_from_source / element_xpath
# ---------------------------------------------------------------------------


def test_location_from_element_delegates():
    class FakeElement:
        tag = "{ns}Tag"
        sourceline = 5
        sourcecolumn = None

    loc = location_from_element(FakeElement())
    assert loc is not None
    assert loc.line == 5


def test_location_from_source_path(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")
    loc = location_from_source(p)
    assert loc is not None
    assert loc.filename == str(p)


def test_location_from_source_none():
    assert location_from_source(42) is None


def test_element_xpath_clark_notation():
    class FakeElement:
        tag = "{http://ns}MyTag"

    assert element_xpath(FakeElement()) == "/MyTag"


def test_element_xpath_plain_tag():
    class FakeElement:
        tag = "MyTag"

    assert element_xpath(FakeElement()) == "/MyTag"


def test_element_xpath_no_tag():
    assert element_xpath(42) is None


def test_element_xpath_empty_tag():
    class FakeElement:
        tag = ""

    assert element_xpath(FakeElement()) is None


# ---------------------------------------------------------------------------
# build_error_location
# ---------------------------------------------------------------------------


def test_build_error_location_explicit_line_column():
    loc = build_error_location(line=10, column=5)
    assert loc is not None
    assert loc.line == 10
    assert loc.column == 5


def test_build_error_location_element():
    class FakeElement:
        tag = "{ns}Tag"
        sourceline = 42
        sourcecolumn = None

    loc = build_error_location(element=FakeElement())
    assert loc is not None
    assert loc.line == 42


def test_build_error_location_sources(tmp_path):
    p = tmp_path / "a.xml"
    p.write_text("<root/>")
    loc = build_error_location(sources=[p])
    assert loc is not None
    assert loc.filename == str(p)


def test_build_error_location_all_empty():
    assert build_error_location() is None


# ---------------------------------------------------------------------------
# DDIError
# ---------------------------------------------------------------------------


def test_ddi_error_message_property():
    err = DDIError("something went wrong")
    assert err.message == "something went wrong"
    assert str(err) == "something went wrong"


def test_ddi_error_with_location():
    loc = ErrorLocation(filename="test.xml", line=10)
    err = DDIError("bad", location=loc)
    assert "test.xml:10" in str(err)
    assert err.location is loc


def test_ddi_error_with_cause():
    cause = ValueError("inner")
    err = DDIError("outer", cause=cause)
    assert err.original_exception is cause
    assert err.__cause__ is cause


def test_ddi_error_with_location_method():
    err = DDIError("msg")
    loc = ErrorLocation(filename="test.xml")
    new_err = err.with_location(loc)
    assert new_err.location.filename == "test.xml"  # type: ignore[union-attr]
    assert new_err.message == "msg"


def test_ddi_error_with_location_merge():
    err = DDIError("msg", location=ErrorLocation(line=10))
    new_err = err.with_location(ErrorLocation(filename="test.xml"))
    assert new_err.location.line == 10  # type: ignore[union-attr]
    assert new_err.location.filename == "test.xml"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# DDIParseError
# ---------------------------------------------------------------------------


def test_parse_error_with_element():
    class FakeElement:
        tag = "{ns}Tag"
        sourceline = 5
        sourcecolumn = None

    err = DDIParseError("bad xml", element=FakeElement())
    assert err.location is not None
    assert err.location.line == 5


def test_parse_error_tag_mismatch():
    err = DDIParseError.tag_mismatch("{ns}Expected", "{ns}Actual")
    assert "Expected" in str(err)
    assert "Actual" in str(err)
    assert err.expected_tag == "{ns}Expected"
    assert err.actual_tag == "{ns}Actual"


def test_parse_error_tag_mismatch_plain():
    err = DDIParseError.tag_mismatch("Expected", "Actual")
    assert "Expected" in str(err)
    assert "Actual" in str(err)


# ---------------------------------------------------------------------------
# DDIValidationError
# ---------------------------------------------------------------------------


def test_validation_error_with_issues():
    class FakeIssue:
        message = "bad field"
        xpath = "/root"
        line = 10
        column = 5

    err = DDIValidationError("validation failed", issues=[FakeIssue()])  # type: ignore[list-item]
    assert len(err.issues) == 1


def test_validation_error_from_schema_error():
    class FakeIssue:
        message = "missing element"
        xpath = "/root/child"
        line = 5
        column = None

    class FakeSchemaError(Exception):
        def __init__(self):
            super().__init__("Schema error")
            self.issues = [FakeIssue()]

    err = DDIValidationError.from_schema_error(FakeSchemaError())
    assert err.message == "missing element"
    assert len(err.issues) == 1


def test_validation_error_from_schema_error_no_issues():
    class FakeSchemaError(Exception):
        def __init__(self):
            super().__init__("Schema error")
            self.issues = []

    err = DDIValidationError.from_schema_error(FakeSchemaError())
    assert err.message == "Schema error"


def test_validation_error_from_schema_error_with_sources(tmp_path):
    p = tmp_path / "test.xml"
    p.write_text("<root/>")

    class FakeSchemaError(Exception):
        def __init__(self):
            super().__init__("Error")
            self.issues = []

    err = DDIValidationError.from_schema_error(FakeSchemaError(), sources=[p])
    assert err.location is not None
    assert err.location.filename == str(p)


# ---------------------------------------------------------------------------
# ModelValidationError
# ---------------------------------------------------------------------------


def test_model_validation_error_missing_field():
    err = ModelValidationError.missing_field(str, "name")
    assert "str requires name" in str(err)
    assert err.model_type is str
    assert err.field_name == "name"


def test_model_validation_error_missing_field_with_context():
    err = ModelValidationError.missing_field(str, "name", context="when URN is absent")
    assert "when URN is absent" in str(err)


def test_model_validation_error_invalid_value():
    err = ModelValidationError.invalid_value(str, "age", -1)
    assert "invalid age" in str(err)
    assert "-1" in str(err)


def test_model_validation_error_invalid_value_with_reason():
    err = ModelValidationError.invalid_value(str, "age", -1, reason="must be positive")
    assert "must be positive" in str(err)


# ---------------------------------------------------------------------------
# ModelBuildError
# ---------------------------------------------------------------------------


def test_model_build_error():
    err = ModelBuildError("builder failed")
    assert str(err) == "builder failed"


# ---------------------------------------------------------------------------
# DDIReferenceError
# ---------------------------------------------------------------------------


def test_reference_error_unresolved_urn():
    err = DDIReferenceError.unresolved(urn="urn:ddi:test:1:1.0")
    assert "urn:ddi:test:1:1.0" in str(err)
    assert err.reference_urn == "urn:ddi:test:1:1.0"


def test_reference_error_unresolved_identifier():
    err = DDIReferenceError.unresolved(identifier="var1", type_of_object="Variable")
    assert "Variable" in str(err)
    assert "var1" in str(err)
    assert err.reference_type == "Variable"


def test_reference_error_unresolved_no_args():
    err = DDIReferenceError.unresolved()
    assert "Could not resolve reference" in str(err)


# ---------------------------------------------------------------------------
# DDIReadError / DDIWriteError
# ---------------------------------------------------------------------------


def test_read_error():
    err = DDIReadError("read failed")
    assert str(err) == "read failed"


def test_write_error():
    err = DDIWriteError("write failed")
    assert str(err) == "write failed"
