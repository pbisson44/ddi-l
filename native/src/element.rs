//! `Element`: the standard library's element API over the native tree.
//!
//! Each node has at most one Python object at a time, so `is` and `id()`
//! behave as they do for lxml: the same object while one is alive. An
//! element can be in one place only; adding it somewhere moves it, as lxml
//! does.

use std::collections::HashSet;
use std::sync::{Arc, Weak};

use pyo3::exceptions::{PyIndexError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyDict, PyList, PyModule, PySlice, PyString, PyTuple};

use crate::attrib::{set_attr, Attrib};
use crate::tree::{
    deep_copy, detach, is_ancestor_or_self, touch, touch_parent, Node, NodeData, Tag, Val,
};

static ELEMENT_PATH: PyOnceLock<Py<PyModule>> = PyOnceLock::new();

fn element_path(py: Python<'_>) -> PyResult<&Bound<'_, PyModule>> {
    ELEMENT_PATH
        .get_or_try_init(py, || {
            PyModule::import(py, "xml.etree.ElementPath").map(Bound::unbind)
        })
        .map(|module| module.bind(py))
}

#[pyclass(frozen, module = "ddi_l_native._core", name = "Element")]
pub struct Element {
    pub node: Arc<Node>,
}

impl Drop for Element {
    fn drop(&mut self) {
        self.node.set_proxy(std::ptr::null_mut());
    }
}

/// The Python object for `node`: the one alive, or a new one.
pub fn wrap<'py>(py: Python<'py>, node: &Arc<Node>) -> PyResult<Bound<'py, Element>> {
    let ptr = node.proxy_ptr();
    if !ptr.is_null() {
        // SAFETY: the pointer is set only to a live `Element` for this node,
        // and that element clears it when it is dropped, with the GIL held.
        return Ok(unsafe { Bound::from_borrowed_ptr(py, ptr).cast_into_unchecked() });
    }
    let element = Bound::new(py, Element { node: node.clone() })?;
    node.set_proxy(element.as_ptr());
    Ok(element)
}

/// `slf`'s node, recording `slf` as its object if it has none yet (an
/// element made by the constructor).
pub fn own<'a>(slf: &'a Bound<'_, Element>) -> &'a Arc<Node> {
    let node = &slf.get().node;
    if node.proxy_ptr().is_null() {
        node.set_proxy(slf.as_ptr());
    }
    node
}

pub fn element_node(value: &Bound<'_, PyAny>) -> PyResult<Arc<Node>> {
    match value.cast::<Element>() {
        Ok(element) => Ok(own(element).clone()),
        Err(_) => Err(PyTypeError::new_err(format!(
            "expected an Element, not {}",
            value.get_type().name()?
        ))),
    }
}

pub fn new_node(
    py: Python<'_>,
    tag: &Bound<'_, PyAny>,
    attrib: Option<&Bound<'_, PyAny>>,
    extra: Option<&Bound<'_, PyDict>>,
) -> PyResult<Arc<Node>> {
    let mut data = NodeData::new(Tag::from_py(py, tag)?);
    if let Some(attrib) = attrib {
        let attrib = attrib.cast::<PyDict>().map_err(|_| {
            PyTypeError::new_err(format!(
                "attrib must be dict, not {}",
                attrib
                    .get_type()
                    .name()
                    .map(|n| n.to_string())
                    .unwrap_or_default()
            ))
        })?;
        for (key, value) in attrib.iter() {
            set_attr(py, &mut data.attrs, &key, &value)?;
        }
    }
    if let Some(extra) = extra {
        for (key, value) in extra.iter() {
            set_attr(py, &mut data.attrs, &key, &value)?;
        }
    }
    Ok(Node::new(data))
}

fn index_in(index: isize, length: usize, message: &str) -> PyResult<usize> {
    let length = length as isize;
    let index = if index < 0 { index + length } else { index };
    if index < 0 || index >= length {
        return Err(PyIndexError::new_err(message.to_owned()));
    }
    Ok(index as usize)
}

/// The indices a slice selects in a sequence of `length`.
fn slice_indices(slice: &Bound<'_, PySlice>, length: usize) -> PyResult<Vec<usize>> {
    use pyo3::types::PySliceMethods;
    let found = slice.indices(length as isize)?;
    let mut indices = Vec::with_capacity(found.slicelength);
    let mut index = found.start;
    for _ in 0..found.slicelength {
        indices.push(index as usize);
        index += found.step;
    }
    Ok(indices)
}

/// Give `parent` exactly `children`, moving each from wherever it was.
fn set_children(py: Python<'_>, parent: &Arc<Node>, children: Vec<Arc<Node>>) -> PyResult<()> {
    for child in &children {
        if is_ancestor_or_self(py, child, parent) {
            return Err(PyValueError::new_err("cannot append parent to itself"));
        }
    }
    let mut seen = HashSet::with_capacity(children.len());
    let children: Vec<Arc<Node>> = children
        .into_iter()
        .filter(|child| seen.insert(Arc::as_ptr(child)))
        .collect();
    let old = std::mem::take(&mut parent.data.get_mut(py).children);
    let old_set: HashSet<*const Node> = old.iter().map(Arc::as_ptr).collect();
    for child in &old {
        if !seen.contains(&Arc::as_ptr(child)) {
            child.data.get_mut(py).parent = Weak::new();
        }
    }
    for child in &children {
        if !old_set.contains(&Arc::as_ptr(child)) {
            detach(py, child);
            child.data.get_mut(py).parent = Arc::downgrade(parent);
        }
    }
    parent.data.get_mut(py).children = children;
    touch(py, parent);
    Ok(())
}

fn append_node(py: Python<'_>, parent: &Arc<Node>, child: Arc<Node>) -> PyResult<()> {
    if is_ancestor_or_self(py, &child, parent) {
        return Err(PyValueError::new_err("cannot append parent to itself"));
    }
    detach(py, &child);
    child.data.get_mut(py).parent = Arc::downgrade(parent);
    parent.data.get_mut(py).children.push(child);
    touch(py, parent);
    Ok(())
}

/// Whether ElementPath must read `path` (as `_elementtree` decides): it has
/// path syntax outside a `{namespace}`, or a `{}`/`{*}` wildcard.
fn needs_element_path(path: &str) -> bool {
    let bytes = path.as_bytes();
    if bytes.len() >= 3
        && bytes[0] == b'{'
        && (bytes[1] == b'}' || (bytes[1] == b'*' && bytes[2] == b'}'))
    {
        return true;
    }
    let mut outside = true;
    for &byte in bytes {
        match byte {
            b'{' => outside = false,
            b'}' => outside = true,
            b'/' | b'*' | b'[' | b'@' | b'.' if outside => return true,
            _ => {}
        }
    }
    false
}

/// The plain tag `path` names, if ElementPath is not needed.
fn plain_tag(path: &Bound<'_, PyAny>, namespaces: Option<&Bound<'_, PyAny>>) -> Option<String> {
    if namespaces.is_some_and(|namespaces| !namespaces.is_none()) {
        return None;
    }
    let text = path.cast::<PyString>().ok()?.to_str().ok()?;
    (!needs_element_path(text)).then(|| text.to_owned())
}

fn children_named(py: Python<'_>, node: &Arc<Node>, tag: &str) -> Vec<Arc<Node>> {
    node.data
        .get(py)
        .children
        .iter()
        .filter(|child| child.data.get(py).tag.name() == Some(tag))
        .cloned()
        .collect()
}

fn opt_val<'py>(py: Python<'py>, data: &NodeData, value: &Option<Val>) -> Bound<'py, PyAny> {
    match value {
        Some(value) => value.to_py(py, data.src()),
        None => py.None().into_bound(py),
    }
}

fn val_from(value: &Bound<'_, PyAny>) -> Option<Val> {
    (!value.is_none()).then(|| Val::from_py(value))
}

#[pymethods]
impl Element {
    #[new]
    #[pyo3(signature = (tag, attrib=None, **extra))]
    fn __new__(
        py: Python<'_>,
        tag: &Bound<'_, PyAny>,
        attrib: Option<&Bound<'_, PyAny>>,
        extra: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        Ok(Element {
            node: new_node(py, tag, attrib, extra)?,
        })
    }

    #[getter]
    fn tag<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyAny> {
        let py = slf.py();
        own(slf).data.get(py).tag.to_py(py)
    }

    #[setter]
    fn set_tag(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let node = own(slf);
        node.data.get_mut(py).tag = Tag::from_py(py, value)?;
        touch(py, node);
        Ok(())
    }

    #[getter]
    fn text<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyAny> {
        let py = slf.py();
        let data = own(slf).data.get(py);
        opt_val(py, &data, &data.text)
    }

    #[setter]
    fn set_text(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) {
        let py = slf.py();
        let node = own(slf);
        node.data.get_mut(py).text = val_from(value);
        touch(py, node);
    }

    #[getter]
    fn tail<'py>(slf: &Bound<'py, Self>) -> Bound<'py, PyAny> {
        let py = slf.py();
        let data = own(slf).data.get(py);
        opt_val(py, &data, &data.tail)
    }

    #[setter]
    fn set_tail(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) {
        let py = slf.py();
        let node = own(slf);
        node.data.get_mut(py).tail = val_from(value);
        touch_parent(py, node);
    }

    /// The line the element's start tag is on, as lxml gives it, if parsed.
    #[getter]
    fn sourceline(slf: &Bound<'_, Self>) -> Option<usize> {
        crate::validate::source_position(slf).map(|(line, _)| line)
    }

    #[getter]
    fn attrib<'py>(slf: &Bound<'py, Self>) -> PyResult<Bound<'py, Attrib>> {
        Bound::new(
            slf.py(),
            Attrib {
                node: own(slf).clone(),
            },
        )
    }

    #[setter]
    fn set_attrib(slf: &Bound<'_, Self>, value: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let node = own(slf);
        let items = value.call_method0("items")?;
        let mut attrs = Vec::new();
        for item in items.try_iter()? {
            let item = item?;
            set_attr(py, &mut attrs, &item.get_item(0)?, &item.get_item(1)?)?;
        }
        node.data.get_mut(py).attrs = attrs;
        touch(py, node);
        Ok(())
    }

    fn __len__(slf: &Bound<'_, Self>) -> usize {
        own(slf).data.get(slf.py()).children.len()
    }

    fn __getitem__<'py>(
        slf: &Bound<'py, Self>,
        index: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        let children = own(slf).data.get(py).children.clone();
        if let Ok(slice) = index.cast::<PySlice>() {
            let list = PyList::empty(py);
            for at in slice_indices(slice, children.len())? {
                list.append(wrap(py, &children[at])?)?;
            }
            return Ok(list.into_any());
        }
        let at = index_in(index.extract()?, children.len(), "child index out of range")?;
        Ok(wrap(py, &children[at])?.into_any())
    }

    fn __setitem__(
        slf: &Bound<'_, Self>,
        index: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let py = slf.py();
        let node = own(slf).clone();
        let mut children = node.data.get(py).children.clone();
        if let Ok(slice) = index.cast::<PySlice>() {
            let new = value
                .try_iter()?
                .map(|item| element_node(&item?))
                .collect::<PyResult<Vec<_>>>()?;
            use pyo3::types::PySliceMethods;
            let found = slice.indices(children.len() as isize)?;
            if found.step == 1 {
                let start = found.start as usize;
                children.splice(start..start + found.slicelength, new);
            } else {
                let indices = slice_indices(slice, children.len())?;
                if indices.len() != new.len() {
                    return Err(PyValueError::new_err(format!(
                        "attempt to assign sequence of size {} to extended slice of size {}",
                        new.len(),
                        indices.len()
                    )));
                }
                for (at, child) in indices.into_iter().zip(new) {
                    children[at] = child;
                }
            }
        } else {
            let at = index_in(
                index.extract()?,
                children.len(),
                "child assignment index out of range",
            )?;
            children[at] = element_node(value)?;
        }
        set_children(py, &node, children)
    }

    fn __delitem__(slf: &Bound<'_, Self>, index: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let node = own(slf).clone();
        let children = node.data.get(py).children.clone();
        let removed: HashSet<usize> = if let Ok(slice) = index.cast::<PySlice>() {
            slice_indices(slice, children.len())?.into_iter().collect()
        } else {
            [index_in(
                index.extract()?,
                children.len(),
                "child assignment index out of range",
            )?]
            .into()
        };
        let kept = children
            .into_iter()
            .enumerate()
            .filter(|(at, _)| !removed.contains(at))
            .map(|(_, child)| child)
            .collect();
        set_children(py, &node, kept)
    }

    fn __iter__(slf: &Bound<'_, Self>) -> ChildIter {
        ChildIter {
            parent: own(slf).clone(),
            index: 0,
        }
    }

    fn __contains__(slf: &Bound<'_, Self>, item: &Bound<'_, PyAny>) -> bool {
        let Ok(item) = item.cast::<Element>() else {
            return false;
        };
        let child = &item.get().node;
        own(slf)
            .data
            .get(slf.py())
            .children
            .iter()
            .any(|candidate| Arc::ptr_eq(candidate, child))
    }

    fn __repr__(slf: &Bound<'_, Self>) -> PyResult<String> {
        let py = slf.py();
        let tag = own(slf).data.get(py).tag.to_py(py);
        Ok(format!(
            "<Element {} at {:#x}>",
            tag.repr()?,
            slf.as_ptr() as usize
        ))
    }

    fn __deepcopy__<'py>(
        slf: &Bound<'py, Self>,
        _memo: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, Element>> {
        let py = slf.py();
        wrap(py, &deep_copy(py, own(slf), true))
    }

    fn append(slf: &Bound<'_, Self>, subelement: &Bound<'_, PyAny>) -> PyResult<()> {
        append_node(slf.py(), own(slf), element_node(subelement)?)
    }

    fn extend(slf: &Bound<'_, Self>, elements: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let parent = own(slf).clone();
        let children = elements
            .try_iter()?
            .map(|item| element_node(&item?))
            .collect::<PyResult<Vec<_>>>()?;
        for child in children {
            append_node(py, &parent, child)?;
        }
        Ok(())
    }

    fn insert(slf: &Bound<'_, Self>, index: isize, subelement: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let parent = own(slf).clone();
        let child = element_node(subelement)?;
        if is_ancestor_or_self(py, &child, &parent) {
            return Err(PyValueError::new_err("cannot append parent to itself"));
        }
        // Insert before the child now at `index`, as lxml does.
        let (anchor, old_at) = {
            let data = parent.data.get(py);
            let length = data.children.len() as isize;
            let at = if index < 0 {
                (index + length).max(0)
            } else {
                index.min(length)
            };
            let old_at = data.children.iter().position(|c| Arc::ptr_eq(c, &child));
            (data.children.get(at as usize).cloned(), old_at)
        };
        detach(py, &child);
        {
            let mut data = parent.data.get_mut(py);
            let at = match anchor {
                Some(anchor) if Arc::ptr_eq(&anchor, &child) => {
                    old_at.unwrap_or(data.children.len())
                }
                Some(anchor) => data
                    .children
                    .iter()
                    .position(|c| Arc::ptr_eq(c, &anchor))
                    .unwrap_or(data.children.len()),
                None => data.children.len(),
            };
            data.children.insert(at, child.clone());
        }
        child.data.get_mut(py).parent = Arc::downgrade(&parent);
        touch(py, &parent);
        Ok(())
    }

    fn remove(slf: &Bound<'_, Self>, subelement: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = slf.py();
        let parent = own(slf).clone();
        let child = element_node(subelement)?;
        {
            let mut data = parent.data.get_mut(py);
            let Some(at) = data.children.iter().position(|c| Arc::ptr_eq(c, &child)) else {
                return Err(PyValueError::new_err("list.remove(x): x not in list"));
            };
            data.children.remove(at);
        }
        child.data.get_mut(py).parent = Weak::new();
        touch(py, &parent);
        Ok(())
    }

    fn clear(slf: &Bound<'_, Self>) {
        let py = slf.py();
        let node = own(slf);
        touch_parent(py, node);
        let children = {
            let mut data = node.data.get_mut(py);
            data.attrs.clear();
            data.text = None;
            data.tail = None;
            std::mem::take(&mut data.children)
        };
        for child in children {
            child.data.get_mut(py).parent = Weak::new();
        }
        touch(py, node);
    }

    #[pyo3(signature = (path, namespaces=None))]
    fn find<'py>(
        slf: &Bound<'py, Self>,
        path: &Bound<'py, PyAny>,
        namespaces: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        let Some(tag) = plain_tag(path, namespaces) else {
            return element_path(py)?.call_method1("find", (slf, path, namespaces));
        };
        let node = own(slf);
        let found = node
            .data
            .get(py)
            .children
            .iter()
            .find(|child| child.data.get(py).tag.name() == Some(&tag))
            .cloned();
        match found {
            Some(child) => Ok(wrap(py, &child)?.into_any()),
            None => Ok(py.None().into_bound(py)),
        }
    }

    #[pyo3(signature = (path, default=None, namespaces=None))]
    fn findtext<'py>(
        slf: &Bound<'py, Self>,
        path: &Bound<'py, PyAny>,
        default: Option<&Bound<'py, PyAny>>,
        namespaces: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        let Some(tag) = plain_tag(path, namespaces) else {
            return element_path(py)?.call_method1("findtext", (slf, path, default, namespaces));
        };
        match children_named(py, own(slf), &tag).first() {
            Some(child) => {
                let data = child.data.get(py);
                Ok(match &data.text {
                    Some(text) => text.to_py(py, data.src()),
                    None => PyString::new(py, "").into_any(),
                })
            }
            None => Ok(default.cloned().unwrap_or_else(|| py.None().into_bound(py))),
        }
    }

    #[pyo3(signature = (path, namespaces=None))]
    fn findall<'py>(
        slf: &Bound<'py, Self>,
        path: &Bound<'py, PyAny>,
        namespaces: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        let Some(tag) = plain_tag(path, namespaces) else {
            return element_path(py)?.call_method1("findall", (slf, path, namespaces));
        };
        let list = PyList::empty(py);
        for child in children_named(py, own(slf), &tag) {
            list.append(wrap(py, &child)?)?;
        }
        Ok(list.into_any())
    }

    #[pyo3(signature = (path, namespaces=None))]
    fn iterfind<'py>(
        slf: &Bound<'py, Self>,
        path: &Bound<'py, PyAny>,
        namespaces: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        element_path(slf.py())?.call_method1("iterfind", (slf, path, namespaces))
    }

    #[pyo3(signature = (tag=None))]
    fn iter(slf: &Bound<'_, Self>, tag: Option<&Bound<'_, PyAny>>) -> PyResult<TreeIter> {
        let sought = match tag {
            None => Sought::All,
            Some(tag) if tag.is_none() => Sought::All,
            Some(tag) => match tag.cast::<PyString>() {
                Ok(text) if text.to_str()? == "*" => Sought::All,
                Ok(text) => Sought::Name(text.to_str()?.into()),
                Err(_) => Sought::Obj(tag.clone().unbind()),
            },
        };
        Ok(TreeIter::new(own(slf).clone(), sought, false))
    }

    fn itertext(slf: &Bound<'_, Self>) -> TreeIter {
        TreeIter::new(own(slf).clone(), Sought::All, true)
    }

    #[pyo3(signature = (key, default=None))]
    fn get<'py>(
        slf: &Bound<'py, Self>,
        key: &Bound<'py, PyAny>,
        default: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let py = slf.py();
        if let Ok(key) = key.cast::<PyString>() {
            let key = key.to_str()?;
            let data = own(slf).data.get(py);
            if let Some(value) = data.attr(key) {
                return Ok(value.to_py(py, data.src()));
            }
        }
        Ok(default.cloned().unwrap_or_else(|| py.None().into_bound(py)))
    }

    fn set(
        slf: &Bound<'_, Self>,
        key: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        let py = slf.py();
        let node = own(slf);
        set_attr(py, &mut node.data.get_mut(py).attrs, key, value)?;
        touch(py, node);
        Ok(())
    }

    fn keys<'py>(slf: &Bound<'py, Self>) -> PyResult<Bound<'py, PyList>> {
        let py = slf.py();
        let data = own(slf).data.get(py);
        PyList::new(py, data.attrs.iter().map(|(name, _)| name.to_py(py)))
    }

    fn items<'py>(slf: &Bound<'py, Self>) -> PyResult<Bound<'py, PyList>> {
        let py = slf.py();
        let data = own(slf).data.get(py);
        let list = PyList::empty(py);
        for (name, value) in &data.attrs {
            list.append(PyTuple::new(
                py,
                [name.to_py(py).into_any(), value.to_py(py, data.src())],
            )?)?;
        }
        Ok(list)
    }

    fn makeelement<'py>(
        slf: &Bound<'py, Self>,
        tag: &Bound<'py, PyAny>,
        attrib: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, Element>> {
        let py = slf.py();
        wrap(py, &new_node(py, tag, Some(attrib), None)?)
    }
}

#[pyclass(module = "ddi_l_native._core")]
pub struct ChildIter {
    parent: Arc<Node>,
    index: usize,
}

#[pymethods]
impl ChildIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<Option<Bound<'py, Element>>> {
        let py = slf.py();
        let child = slf.parent.data.get(py).children.get(slf.index).cloned();
        match child {
            Some(child) => {
                slf.index += 1;
                Ok(Some(wrap(py, &child)?))
            }
            None => Ok(None),
        }
    }
}

pub enum Sought {
    All,
    Name(Box<str>),
    Obj(Py<PyAny>),
}

/// `iter()` and `itertext()`, walking the tree as it is at each step, as
/// `_elementtree` does.
#[pyclass(module = "ddi_l_native._core")]
pub struct TreeIter {
    root: Option<Arc<Node>>,
    stack: Vec<(Arc<Node>, usize)>,
    sought: Sought,
    text: bool,
}

impl TreeIter {
    pub fn new(root: Arc<Node>, sought: Sought, text: bool) -> TreeIter {
        TreeIter {
            root: Some(root),
            stack: Vec::new(),
            sought,
            text,
        }
    }
}

#[pymethods]
impl TreeIter {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__<'py>(mut slf: PyRefMut<'py, Self>) -> PyResult<Option<Bound<'py, PyAny>>> {
        let py = slf.py();
        let this = &mut *slf;
        loop {
            let node = if this.stack.is_empty() {
                match this.root.take() {
                    Some(root) => root,
                    None => return Ok(None),
                }
            } else {
                let (parent, index) = this.stack.last_mut().expect("not empty");
                let next = parent.data.get(py).children.get(*index).cloned();
                match next {
                    Some(child) => {
                        *index += 1;
                        child
                    }
                    None => {
                        let (done, _) = this.stack.pop().expect("not empty");
                        // Only inner text: not the tail of where it began.
                        if this.text && !this.stack.is_empty() {
                            let data = done.data.get(py);
                            if let Some(tail) = &data.tail {
                                let tail = tail.to_py(py, data.src());
                                drop(data);
                                if tail.is_truthy()? {
                                    return Ok(Some(tail));
                                }
                            }
                        }
                        continue;
                    }
                }
            };
            this.stack.push((node.clone(), 0));
            if this.text {
                let data = node.data.get(py);
                if let Some(text) = &data.text {
                    let text = text.to_py(py, data.src());
                    drop(data);
                    if text.is_truthy()? {
                        return Ok(Some(text));
                    }
                }
                continue;
            }
            let found = match &this.sought {
                Sought::All => true,
                Sought::Name(name) => node.data.get(py).tag.name() == Some(name),
                Sought::Obj(sought) => {
                    let tag = node.data.get(py).tag.to_py(py);
                    tag.eq(sought.bind(py))?
                }
            };
            if found {
                return Ok(Some(wrap(py, &node)?.into_any()));
            }
        }
    }
}
