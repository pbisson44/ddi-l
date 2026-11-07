//! The tree: nodes shared by `Arc` and changed only with the GIL held.
//!
//! A node keeps the bytes it was parsed from, so text that needed no
//! decoding stays a range of them until Python asks for it. Each node also
//! caches the digest of its content; any change clears it on the node and
//! its ancestors.

use std::borrow::Cow;
use std::cell::{Ref, RefCell, RefMut};
use std::sync::atomic::{AtomicPtr, Ordering};
use std::sync::{Arc, Weak};

use pyo3::exceptions::PyTypeError;
use pyo3::ffi;
use pyo3::prelude::*;
use pyo3::sync::PyOnceLock;
use pyo3::types::{PyBytes, PyString};

/// A `RefCell` borrowed only with a `Python` token.
///
/// The extension is built for the stable ABI, which free-threaded
/// interpreters cannot load, so holding a token means holding the GIL: no
/// two threads borrow the cell at once.
pub struct GilCell<T>(RefCell<T>);

// SAFETY: see the type's documentation; every borrow takes a `Python` token,
// except `unshared`, used only on nodes no other thread can reach yet.
unsafe impl<T: Send> Sync for GilCell<T> {}

impl<T> GilCell<T> {
    pub fn new(value: T) -> Self {
        Self(RefCell::new(value))
    }

    pub fn get<'a>(&'a self, _py: Python<'_>) -> Ref<'a, T> {
        self.0.borrow()
    }

    pub fn get_mut<'a>(&'a self, _py: Python<'_>) -> RefMut<'a, T> {
        self.0.borrow_mut()
    }

    /// For a tree being built, which nothing else can reach yet.
    pub fn unshared(&self) -> RefMut<'_, T> {
        self.0.borrow_mut()
    }

    pub fn into_inner(self) -> T {
        self.0.into_inner()
    }
}

/// The bytes a tree was parsed from.
pub struct Source {
    pub bytes: Py<PyBytes>,
    /// Where each line starts, made the first time a position is asked for.
    pub lines: std::sync::OnceLock<Vec<u32>>,
}

impl Source {
    pub fn new(bytes: Py<PyBytes>) -> Source {
        Source {
            bytes,
            lines: std::sync::OnceLock::new(),
        }
    }

    pub fn data<'a>(&'a self, py: Python<'_>) -> &'a [u8] {
        self.bytes.as_bytes(py)
    }

    /// The 1-based line and 0-based column (in characters) of `offset`.
    pub fn position(&self, py: Python<'_>, offset: u32) -> (usize, usize) {
        let data = self.data(py);
        let lines = self.lines.get_or_init(|| {
            let mut starts = vec![0u32];
            starts.extend(memchr::memchr_iter(b'\n', data).map(|at| at as u32 + 1));
            starts
        });
        let line = lines.partition_point(|&start| start <= offset);
        let start = lines[line - 1] as usize;
        let end = (offset as usize).min(data.len());
        let column = data[start..end]
            .iter()
            .filter(|&&b| (b & 0xC0) != 0x80)
            .count();
        (line, column)
    }
}

/// A tag or attribute name in Clark notation, with its Python string made once.
pub struct Name {
    pub text: Box<str>,
    py: PyOnceLock<Py<PyString>>,
}

pub type NameRef = Arc<Name>;

impl Name {
    pub fn new(text: &str) -> NameRef {
        Arc::new(Name {
            text: text.into(),
            py: PyOnceLock::new(),
        })
    }

    pub fn from_py(py: Python<'_>, value: &Bound<'_, PyString>) -> PyResult<NameRef> {
        let name = Name::new(value.to_str()?);
        let _ = name.py.set(py, value.clone().unbind());
        Ok(name)
    }

    pub fn to_py<'py>(&self, py: Python<'py>) -> Bound<'py, PyString> {
        self.py
            .get_or_init(py, || PyString::new(py, &self.text).unbind())
            .bind(py)
            .clone()
    }
}

/// An element's tag: a name, or whatever else Python set it to.
pub enum Tag {
    Name(NameRef),
    Obj(Py<PyAny>),
}

impl Tag {
    pub fn from_py(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<Tag> {
        match value.cast::<PyString>() {
            Ok(text) => Ok(Tag::Name(Name::from_py(py, text)?)),
            Err(_) => Ok(Tag::Obj(value.clone().unbind())),
        }
    }

    pub fn to_py<'py>(&self, py: Python<'py>) -> Bound<'py, PyAny> {
        match self {
            Tag::Name(name) => name.to_py(py).into_any(),
            Tag::Obj(obj) => obj.bind(py).clone(),
        }
    }

    pub fn name(&self) -> Option<&str> {
        match self {
            Tag::Name(name) => Some(&name.text),
            Tag::Obj(_) => None,
        }
    }

    pub fn clone_ref(&self, py: Python<'_>) -> Tag {
        match self {
            Tag::Name(name) => Tag::Name(name.clone()),
            Tag::Obj(obj) => Tag::Obj(obj.clone_ref(py)),
        }
    }
}

/// Text, a tail or an attribute value.
pub enum Val {
    /// Bytes of the node's source that need no decoding.
    Src(u32, u32),
    Own(Box<str>),
    Str(Py<PyString>),
    /// Something other than a string, set from Python.
    Obj(Py<PyAny>),
}

impl Val {
    pub fn from_py(value: &Bound<'_, PyAny>) -> Val {
        match value.cast::<PyString>() {
            Ok(text) => Val::Str(text.clone().unbind()),
            Err(_) => Val::Obj(value.clone().unbind()),
        }
    }

    pub fn to_py<'py>(&self, py: Python<'py>, src: Option<&Source>) -> Bound<'py, PyAny> {
        match self {
            Val::Src(start, end) => {
                let data = src.expect("a source range needs its source").data(py);
                PyString::new(py, as_text(&data[*start as usize..*end as usize])).into_any()
            }
            Val::Own(text) => PyString::new(py, text).into_any(),
            Val::Str(text) => text.bind(py).clone().into_any(),
            Val::Obj(obj) => obj.bind(py).clone(),
        }
    }

    /// The value as text; an error if Python set it to something else.
    pub fn text<'a>(&'a self, py: Python<'_>, src: Option<&'a Source>) -> PyResult<Cow<'a, str>> {
        match self {
            Val::Src(start, end) => {
                let data = src.expect("a source range needs its source").data(py);
                Ok(Cow::Borrowed(as_text(
                    &data[*start as usize..*end as usize],
                )))
            }
            Val::Own(text) => Ok(Cow::Borrowed(text)),
            Val::Str(text) => text.to_cow(py),
            Val::Obj(obj) => Err(PyTypeError::new_err(format!(
                "cannot serialize {} (type {})",
                obj.bind(py).repr()?,
                obj.bind(py).get_type().name()?
            ))),
        }
    }

    pub fn clone_ref(&self, py: Python<'_>) -> Val {
        match self {
            Val::Src(start, end) => Val::Src(*start, *end),
            Val::Own(text) => Val::Own(text.clone()),
            Val::Str(text) => Val::Str(text.clone_ref(py)),
            Val::Obj(obj) => Val::Obj(obj.clone_ref(py)),
        }
    }
}

/// Bytes the parser checked are UTF-8.
pub fn as_text(bytes: &[u8]) -> &str {
    // SAFETY: the parser validates the whole input as UTF-8 before it makes
    // any range, and ranges start and end on character boundaries.
    unsafe { std::str::from_utf8_unchecked(bytes) }
}

pub struct NodeData {
    pub tag: Tag,
    pub attrs: Vec<(NameRef, Val)>,
    pub text: Option<Val>,
    pub tail: Option<Val>,
    pub children: Vec<Arc<Node>>,
    pub parent: Weak<Node>,
    pub src: Option<Arc<Source>>,
    pub digest: Option<[u8; 16]>,
    /// Where the element's start tag begins in `src`, if it was parsed.
    pub start: u32,
}

pub const NO_START: u32 = u32::MAX;

impl NodeData {
    pub fn new(tag: Tag) -> NodeData {
        NodeData {
            tag,
            attrs: Vec::new(),
            text: None,
            tail: None,
            children: Vec::new(),
            parent: Weak::new(),
            src: None,
            digest: None,
            start: NO_START,
        }
    }

    pub fn src(&self) -> Option<&Source> {
        self.src.as_deref()
    }

    pub fn attr(&self, name: &str) -> Option<&Val> {
        self.attrs
            .iter()
            .find(|(key, _)| &*key.text == name)
            .map(|(_, value)| value)
    }
}

impl Drop for NodeData {
    /// Drop a deep tree without recursing once per level.
    fn drop(&mut self) {
        let mut pending = std::mem::take(&mut self.children);
        while let Some(child) = pending.pop() {
            if let Ok(node) = Arc::try_unwrap(child) {
                let mut data = node.data.into_inner();
                pending.append(&mut data.children);
            }
        }
    }
}

pub struct Node {
    pub data: GilCell<NodeData>,
    /// The Python object for this node while there is one. Not owned: the
    /// object clears it when it is dropped.
    pub proxy: AtomicPtr<ffi::PyObject>,
}

impl Node {
    pub fn new(data: NodeData) -> Arc<Node> {
        Arc::new(Node {
            data: GilCell::new(data),
            proxy: AtomicPtr::new(std::ptr::null_mut()),
        })
    }

    pub fn proxy_ptr(&self) -> *mut ffi::PyObject {
        self.proxy.load(Ordering::Acquire)
    }

    pub fn set_proxy(&self, ptr: *mut ffi::PyObject) {
        self.proxy.store(ptr, Ordering::Release);
    }

    pub fn parent(&self, py: Python<'_>) -> Option<Arc<Node>> {
        self.data.get(py).parent.upgrade()
    }
}

/// Forget the digests of `node` and its ancestors: their content changed.
pub fn touch(py: Python<'_>, node: &Arc<Node>) {
    let mut current = Some(node.clone());
    while let Some(node) = current {
        let mut data = node.data.get_mut(py);
        // A node without a digest has none above it either.
        if data.digest.take().is_none() {
            return;
        }
        current = data.parent.upgrade();
    }
}

/// Forget the digests above `node`: its tail changed, and a tail is part of
/// its parent's content.
pub fn touch_parent(py: Python<'_>, node: &Arc<Node>) {
    if let Some(parent) = node.parent(py) {
        touch(py, &parent);
    }
}

/// Whether `node` is `other` or one of its ancestors.
pub fn is_ancestor_or_self(py: Python<'_>, node: &Arc<Node>, other: &Arc<Node>) -> bool {
    let mut current = Some(other.clone());
    while let Some(candidate) = current {
        if Arc::ptr_eq(&candidate, node) {
            return true;
        }
        current = candidate.parent(py);
    }
    false
}

/// Take `node` out of its parent's children, if it has a parent.
pub fn detach(py: Python<'_>, node: &Arc<Node>) {
    let Some(parent) = node.parent(py) else {
        return;
    };
    {
        let mut data = parent.data.get_mut(py);
        if let Some(index) = data
            .children
            .iter()
            .position(|child| Arc::ptr_eq(child, node))
        {
            data.children.remove(index);
        }
    }
    node.data.get_mut(py).parent = Weak::new();
    touch(py, &parent);
}

/// A copy of the subtree under `node`; the copy has no parent and no tail
/// unless `keep_tail`.
pub fn deep_copy(py: Python<'_>, node: &Arc<Node>, keep_tail: bool) -> Arc<Node> {
    let root = copy_one(py, node, keep_tail);
    let mut pending = vec![(node.clone(), root.clone())];
    while let Some((original, copy)) = pending.pop() {
        let children: Vec<Arc<Node>> = original.data.get(py).children.clone();
        let mut copies = Vec::with_capacity(children.len());
        for child in &children {
            let child_copy = copy_one(py, child, true);
            child_copy.data.get_mut(py).parent = Arc::downgrade(&copy);
            pending.push((child.clone(), child_copy.clone()));
            copies.push(child_copy);
        }
        copy.data.get_mut(py).children = copies;
    }
    root
}

fn copy_one(py: Python<'_>, node: &Arc<Node>, keep_tail: bool) -> Arc<Node> {
    let data = node.data.get(py);
    let mut copy = NodeData::new(data.tag.clone_ref(py));
    copy.attrs = data
        .attrs
        .iter()
        .map(|(name, value)| (name.clone(), value.clone_ref(py)))
        .collect();
    copy.text = data.text.as_ref().map(|value| value.clone_ref(py));
    if keep_tail {
        copy.tail = data.tail.as_ref().map(|value| value.clone_ref(py));
    }
    copy.src = data.src.clone();
    copy.digest = data.digest;
    copy.start = data.start;
    Node::new(copy)
}
