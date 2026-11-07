//! Native XML core for ddi-l.
//!
//! A hardened parser that builds a tree whose elements behave like the
//! standard library's (`xml.etree.ElementTree`), keeping the bytes they were
//! read from, plus the content digests and source index the lossless
//! writer uses.

use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyTuple};

mod attrib;
mod digest;
mod element;
mod parse;
mod table;
mod tree;
mod validate;

use element::{element_node, new_node, own, wrap, Element};
use table::{Index, Table};
use tree::{Source, Tag};

fn parse_error(py: Python<'_>, data: &[u8], problem: parse::ParseError) -> PyErr {
    let raise = || -> PyResult<PyErr> {
        let class = py.import("xml.etree.ElementTree")?.getattr("ParseError")?;
        if problem.bare {
            return Ok(PyErr::from_value(class.call1((problem.message,))?));
        }
        let offset = problem.offset.min(data.len());
        let before = &data[..offset];
        let line = before.iter().filter(|&&b| b == b'\n').count() + 1;
        let line_start = memchr::memrchr(b'\n', before).map_or(0, |at| at + 1);
        let column = before[line_start..]
            .iter()
            .filter(|&&b| (b & 0xC0) != 0x80)
            .count();
        let error = class.call1((format!(
            "{}: line {}, column {}",
            problem.message, line, column
        ),))?;
        error.setattr("position", (line, column))?;
        Ok(PyErr::from_value(error))
    };
    raise().unwrap_or_else(|error| error)
}

/// Parse XML `data` (UTF-8 bytes) into a tree; with `index`, also return
/// every element's place in the source.
#[pyfunction]
#[pyo3(name = "parse", signature = (data, *, index=false))]
fn parse_xml<'py>(
    py: Python<'py>,
    data: &Bound<'py, PyAny>,
    index: bool,
) -> PyResult<Bound<'py, PyAny>> {
    let bytes = match data.cast::<PyBytes>() {
        Ok(bytes) => bytes.clone(),
        Err(_) => py
            .import("builtins")?
            .getattr("bytes")?
            .call1((data,))?
            .cast_into::<PyBytes>()?,
    };
    let source = Arc::new(Source::new(bytes.unbind()));
    let input = source.data(py);
    let parsed = py
        .detach(|| parse::parse(input, &source, index))
        .map_err(|problem| parse_error(py, input, problem))?;
    let root = wrap(py, &parsed.root)?;
    if !index {
        return Ok(root.into_any());
    }
    let index = Bound::new(
        py,
        Index {
            placed: parsed.placed,
            source,
        },
    )?;
    Ok(PyTuple::new(py, [root.into_any(), index.into_any()])?.into_any())
}

/// `xml.etree.ElementTree.SubElement` for native elements.
#[pyfunction]
#[pyo3(name = "SubElement", signature = (parent, tag, attrib=None, **extra))]
fn sub_element<'py>(
    parent: &Bound<'py, PyAny>,
    tag: &Bound<'py, PyAny>,
    attrib: Option<&Bound<'py, PyAny>>,
    extra: Option<&Bound<'py, PyDict>>,
) -> PyResult<Bound<'py, Element>> {
    let py = parent.py();
    let parent = element_node(parent)?;
    let child = new_node(py, tag, attrib, extra)?;
    child.data.get_mut(py).parent = Arc::downgrade(&parent);
    parent.data.get_mut(py).children.push(child.clone());
    tree::touch(py, &parent);
    wrap(py, &child)
}

/// The content digest of `element`, as `ddi_l._lossless` computes it.
#[pyfunction]
#[pyo3(name = "digest")]
fn content_digest<'py>(element: &Bound<'py, Element>) -> PyResult<Bound<'py, PyBytes>> {
    let py = element.py();
    Ok(PyBytes::new(py, &digest::digest(py, own(element))?))
}

/// The element `element` is a child of, if any (the standard library's
/// elements have no such method, so native ones have none either).
#[pyfunction]
fn parent<'py>(element: &Bound<'py, Element>) -> PyResult<Option<Bound<'py, Element>>> {
    let py = element.py();
    match own(element).parent(py) {
        Some(node) => Ok(Some(wrap(py, &node)?)),
        None => Ok(None),
    }
}

/// Whether `element` or anything in it has a tag in namespace `uri`.
#[pyfunction]
fn uses_namespace(element: &Bound<'_, Element>, uri: &str) -> bool {
    let py = element.py();
    let prefix = format!("{{{uri}}}");
    let mut pending = vec![own(element).clone()];
    while let Some(node) = pending.pop() {
        let data = node.data.get(py);
        if let Tag::Name(name) = &data.tag {
            if name.text.starts_with(&prefix) {
                return true;
            }
        }
        pending.extend(data.children.iter().cloned());
    }
    false
}

#[pymodule]
fn _core(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<Element>()?;
    module.add_class::<attrib::Attrib>()?;
    module.add_class::<Index>()?;
    module.add_class::<Table>()?;
    module.add_class::<table::Span>()?;
    module.add_function(wrap_pyfunction!(parse_xml, module)?)?;
    module.add_function(wrap_pyfunction!(sub_element, module)?)?;
    module.add_function(wrap_pyfunction!(content_digest, module)?)?;
    module.add_function(wrap_pyfunction!(uses_namespace, module)?)?;
    module.add_function(wrap_pyfunction!(parent, module)?)?;
    module.add_class::<validate::Schema>()?;
    module.add_function(wrap_pyfunction!(validate::source_position, module)?)?;
    Ok(())
}
