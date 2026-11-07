//! The lossless writer's index of a source, as `ddi_l._lossless._Table`
//! builds it: each element's span, children, namespace needs and digest.

use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict, PyList};

use crate::digest::digest;
use crate::element::{wrap, Element};
use crate::parse::{Placed, XML_NS};
use crate::tree::{as_text, Node, Source};

/// A parsed tree with every element's place in the source.
#[pyclass(frozen, module = "ddi_l_native._core", name = "Index")]
pub struct Index {
    pub placed: Vec<Placed>,
    pub source: Arc<Source>,
}

struct SpanData {
    span: [u32; 4],
    depth: u32,
    children: Vec<u32>,
    /// (prefix, URI) pairs as ids into `Table::strings`, in source order.
    declares: Vec<(u32, u32)>,
    tag_needs: Vec<(u32, u32)>,
    needs: Vec<(u32, u32)>,
}

#[pyclass(frozen, module = "ddi_l_native._core", name = "Table")]
pub struct Table {
    source: Arc<Source>,
    nodes: Vec<Arc<Node>>,
    spans: Vec<SpanData>,
    digests: Vec<[u8; 16]>,
    by_digest: HashMap<[u8; 16], Vec<u32>>,
    strings: Vec<String>,
    #[pyo3(get)]
    indent: String,
    #[pyo3(get)]
    newline: String,
}

struct Strings {
    list: Vec<String>,
    ids: HashMap<String, u32>,
}

impl Strings {
    fn id(&mut self, text: &str) -> u32 {
        if let Some(&id) = self.ids.get(text) {
            return id;
        }
        let id = self.list.len() as u32;
        self.list.push(text.to_owned());
        self.ids.insert(text.to_owned(), id);
        id
    }
}

fn is_space(byte: u8) -> bool {
    matches!(byte, b' ' | b'\t' | b'\n' | b'\r')
}

fn prefix_of(name: &[u8]) -> &[u8] {
    match memchr::memchr(b':', name) {
        Some(colon) => &name[..colon],
        None => b"",
    }
}

/// An attribute value as the parser reads it (the source is well-formed).
fn decode(raw: &[u8]) -> String {
    let text = as_text(raw);
    if !raw
        .iter()
        .any(|b| matches!(b, b'&' | b'\t' | b'\n' | b'\r'))
    {
        return text.to_owned();
    }
    let mut out = String::with_capacity(text.len());
    let mut rest = text.replace("\r\n", " ");
    rest = rest.replace(['\t', '\n', '\r'], " ");
    let mut chars = rest.as_str();
    while let Some(amp) = chars.find('&') {
        out.push_str(&chars[..amp]);
        let after = &chars[amp + 1..];
        let semicolon = after.find(';').unwrap_or(after.len());
        let body = &after[..semicolon];
        let found = match body {
            "lt" => Some('<'),
            "gt" => Some('>'),
            "amp" => Some('&'),
            "apos" => Some('\''),
            "quot" => Some('"'),
            _ => body
                .strip_prefix('#')
                .and_then(|number| match number.strip_prefix('x') {
                    Some(hex) => u32::from_str_radix(hex, 16).ok().and_then(char::from_u32),
                    None => number.parse().ok().and_then(char::from_u32),
                }),
        };
        out.push(found.unwrap_or('&'));
        chars = &after[(semicolon + 1).min(after.len())..];
    }
    out.push_str(chars);
    out
}

/// The prefixes a start tag declares and the prefixes its names use.
fn read_start_tag(tag: &[u8]) -> (Vec<(String, String)>, Vec<&[u8]>) {
    let mut declares = Vec::new();
    let mut at = 1;
    while at < tag.len() && !is_space(tag[at]) && tag[at] != b'/' && tag[at] != b'>' {
        at += 1;
    }
    let mut used = vec![prefix_of(&tag[1..at])];
    loop {
        while at < tag.len() && is_space(tag[at]) {
            at += 1;
        }
        if at >= tag.len() || tag[at] == b'/' || tag[at] == b'>' {
            break;
        }
        let name_start = at;
        while at < tag.len() && tag[at] != b'=' && !is_space(tag[at]) {
            at += 1;
        }
        let name = &tag[name_start..at];
        while at < tag.len() && tag[at] != b'"' && tag[at] != b'\'' {
            at += 1;
        }
        let quote = tag[at];
        let value_start = at + 1;
        let value_end = value_start + memchr::memchr(quote, &tag[value_start..]).unwrap_or(0);
        at = value_end + 1;
        let value = &tag[value_start..value_end];
        if name == b"xmlns" {
            declares.push((String::new(), decode(value)));
        } else if let Some(prefix) = name.strip_prefix(b"xmlns:") {
            declares.push((as_text(prefix).to_owned(), decode(value)));
        } else if memchr::memchr(b':', name).is_some() {
            used.push(prefix_of(name));
        }
    }
    (declares, used)
}

/// The file's newline and indentation unit, from its first nested child.
fn layout(data: &[u8], spans: &[SpanData]) -> (String, String) {
    if let Some(first) = spans.iter().find(|span| span.depth == 1) {
        let gap = String::from_utf8_lossy(&data[spans[0].span[1] as usize..first.span[0] as usize]);
        let newline = if gap.contains("\r\n") { "\r\n" } else { "\n" };
        let indent = gap.rsplit('\n').next().unwrap_or("");
        if !indent.is_empty() && indent.trim().is_empty() {
            return (newline.to_owned(), indent.to_owned());
        }
        return (newline.to_owned(), "  ".to_owned());
    }
    ("\n".to_owned(), "  ".to_owned())
}

impl Table {
    fn pairs<'py>(&self, py: Python<'py>, pairs: &[(u32, u32)]) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        for (prefix, uri) in pairs {
            dict.set_item(
                &self.strings[*prefix as usize],
                &self.strings[*uri as usize],
            )?;
        }
        Ok(dict)
    }
}

#[pymethods]
impl Table {
    #[new]
    fn new(py: Python<'_>, index: &Bound<'_, Index>) -> PyResult<Table> {
        let index = index.get();
        let data = index.source.data(py);
        let mut strings = Strings {
            list: Vec::new(),
            ids: HashMap::new(),
        };
        let empty = strings.id("");
        let xml = strings.id("xml");
        let xml_uri = strings.id(XML_NS);

        let mut spans: Vec<SpanData> = Vec::with_capacity(index.placed.len());
        // The in-scope bindings of the open elements, innermost last.
        let mut scopes: Vec<(u32, Arc<HashMap<u32, u32>>)> = Vec::new();
        let base = Arc::new(HashMap::from([(xml, xml_uri)]));
        let mut open: Vec<u32> = Vec::new();
        for (at, placed) in index.placed.iter().enumerate() {
            let depth = placed.depth;
            while scopes.last().is_some_and(|(d, _)| *d >= depth) {
                scopes.pop();
            }
            open.truncate(depth as usize);
            if let Some(&parent) = open.last() {
                spans[parent as usize].children.push(at as u32);
            }
            open.push(at as u32);
            let parent_scope = scopes
                .last()
                .map(|(_, scope)| scope.clone())
                .unwrap_or_else(|| base.clone());
            let [start, open_end, ..] = placed.span;
            let (declared, used) = read_start_tag(&data[start as usize..open_end as usize]);
            let declares: Vec<(u32, u32)> = declared
                .iter()
                .map(|(prefix, uri)| (strings.id(prefix), strings.id(uri)))
                .collect();
            let mut tag_needs: Vec<(u32, u32)> = Vec::new();
            for prefix in used {
                let prefix = strings.id(as_text(prefix));
                if prefix == xml
                    || declares.iter().any(|(p, _)| *p == prefix)
                    || tag_needs.iter().any(|(p, _)| *p == prefix)
                {
                    continue;
                }
                tag_needs.push((prefix, parent_scope.get(&prefix).copied().unwrap_or(empty)));
            }
            let scope = if declares.is_empty() {
                parent_scope
            } else {
                let mut scope = (*parent_scope).clone();
                scope.extend(declares.iter().copied());
                Arc::new(scope)
            };
            scopes.push((depth, scope));
            spans.push(SpanData {
                span: placed.span,
                depth,
                children: Vec::new(),
                declares,
                tag_needs,
                needs: Vec::new(),
            });
        }
        // What a subtree relies on: its own tags' needs plus its children's,
        // less what it declares itself.
        for at in (0..spans.len()).rev() {
            let mut needs = spans[at].tag_needs.clone();
            for &child in &spans[at].children {
                for &(prefix, uri) in &spans[child as usize].needs {
                    if spans[at].declares.iter().any(|(p, _)| *p == prefix)
                        || needs.iter().any(|(p, _)| *p == prefix)
                    {
                        continue;
                    }
                    needs.push((prefix, uri));
                }
            }
            spans[at].needs = needs;
        }

        let nodes: Vec<Arc<Node>> = index
            .placed
            .iter()
            .map(|placed| placed.node.clone())
            .collect();
        if let Some(root) = nodes.first() {
            digest(py, root)?;
        }
        let mut digests = Vec::with_capacity(nodes.len());
        let mut by_digest: HashMap<[u8; 16], Vec<u32>> = HashMap::new();
        for (at, node) in nodes.iter().enumerate() {
            let found = digest(py, node)?;
            digests.push(found);
            by_digest.entry(found).or_default().push(at as u32);
        }
        let (newline, indent) = layout(data, &spans);
        Ok(Table {
            source: index.source.clone(),
            nodes,
            spans,
            digests,
            by_digest,
            strings: strings.list,
            indent,
            newline,
        })
    }

    #[getter]
    fn data<'py>(&self, py: Python<'py>) -> Bound<'py, PyBytes> {
        self.source.bytes.bind(py).clone()
    }

    fn __len__(&self) -> usize {
        self.spans.len()
    }

    fn span(slf: &Bound<'_, Self>, index: usize) -> PyResult<Span> {
        if index >= slf.get().spans.len() {
            return Err(pyo3::exceptions::PyIndexError::new_err(
                "span index out of range",
            ));
        }
        Ok(Span {
            table: slf.clone().unbind(),
            index,
        })
    }

    fn element<'py>(&self, py: Python<'py>, index: usize) -> PyResult<Bound<'py, Element>> {
        wrap(py, &self.nodes[index])
    }

    fn digest<'py>(&self, py: Python<'py>, index: usize) -> Bound<'py, PyBytes> {
        PyBytes::new(py, &self.digests[index])
    }

    fn candidates<'py>(
        &self,
        py: Python<'py>,
        digest: &[u8],
    ) -> PyResult<Option<Bound<'py, PyList>>> {
        let Ok(key) = <[u8; 16]>::try_from(digest) else {
            return Ok(None);
        };
        match self.by_digest.get(&key) {
            Some(found) => Ok(Some(PyList::new(py, found)?)),
            None => Ok(None),
        }
    }

    /// Whether every prefix the source declares is the one `canonical`
    /// (URI to prefix) gives its URI, where it gives one.
    fn canonical_prefixes(&self, canonical: HashMap<String, String>) -> bool {
        self.spans.iter().all(|span| {
            span.declares.iter().all(|(prefix, uri)| {
                let prefix = &self.strings[*prefix as usize];
                prefix.is_empty()
                    || canonical
                        .get(&self.strings[*uri as usize])
                        .is_none_or(|expected| expected == prefix)
            })
        })
    }
}

#[pyclass(frozen, module = "ddi_l_native._core", name = "Span")]
pub struct Span {
    table: Py<Table>,
    index: usize,
}

impl Span {
    fn data(&self) -> &SpanData {
        &self.table.get().spans[self.index]
    }
}

#[pymethods]
impl Span {
    #[getter]
    fn start(&self) -> u32 {
        self.data().span[0]
    }

    #[getter]
    fn open_end(&self) -> u32 {
        self.data().span[1]
    }

    #[getter]
    fn close_start(&self) -> u32 {
        self.data().span[2]
    }

    #[getter]
    fn end(&self) -> u32 {
        self.data().span[3]
    }

    #[getter]
    fn depth(&self) -> u32 {
        self.data().depth
    }

    #[getter]
    fn self_closing(&self) -> bool {
        let span = self.data().span;
        span[1] == span[2] && span[2] == span[3]
    }

    #[getter]
    fn children<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, &self.data().children)
    }

    #[getter]
    fn declares<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        self.table.get().pairs(py, &self.data().declares)
    }

    #[getter]
    fn tag_needs<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        self.table.get().pairs(py, &self.data().tag_needs)
    }

    #[getter]
    fn needs<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        self.table.get().pairs(py, &self.data().needs)
    }
}
