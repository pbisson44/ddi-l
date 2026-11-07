//! Content digests, as `ddi_l._lossless._digests` computes them.
//!
//! A digest covers the tag, the attributes in name order, the text, and
//! each child with its tail; an element's own tail is its parent's. Each
//! node caches its digest, and a change clears it on the node and its
//! ancestors, so an unchanged subtree is never hashed twice.

use std::borrow::Cow;
use std::sync::Arc;

use blake2::digest::consts::U16;
use blake2::{Blake2b, Digest};
use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;

use crate::tree::{Node, NodeData, Source, Tag, Val};

type Blake2b128 = Blake2b<U16>;

fn text_bytes(
    hash: &mut Blake2b128,
    py: Python<'_>,
    src: Option<&Source>,
    value: &Option<Val>,
) -> PyResult<()> {
    match value {
        None => hash.update(b"\x00"),
        Some(value) => hash.update(value.text(py, src)?.as_bytes()),
    }
    Ok(())
}

fn compute(py: Python<'_>, data: &NodeData) -> PyResult<[u8; 16]> {
    let src = data.src();
    let mut hash = Blake2b128::new();
    let Tag::Name(tag) = &data.tag else {
        return Err(PyTypeError::new_err("a digest needs a string tag"));
    };
    hash.update(tag.text.as_bytes());
    let mut attrs: Vec<(&str, Cow<'_, str>)> = data
        .attrs
        .iter()
        .map(|(name, value)| Ok((&*name.text, value.text(py, src)?)))
        .collect::<PyResult<_>>()?;
    attrs.sort_by(|a, b| a.0.cmp(b.0));
    for (name, value) in attrs {
        hash.update(b"\x01");
        hash.update(name.as_bytes());
        hash.update(b"\x02");
        hash.update(value.as_bytes());
    }
    hash.update(b"\x03");
    text_bytes(&mut hash, py, src, &data.text)?;
    for child in &data.children {
        let child = child.data.get(py);
        match &child.tag {
            Tag::Name(_) => {
                hash.update(b"\x04");
                hash.update(child.digest.expect("children are hashed first"));
            }
            Tag::Obj(_) => {
                hash.update(b"\x05");
                text_bytes(&mut hash, py, child.src(), &child.text)?;
            }
        }
        hash.update(b"\x06");
        text_bytes(&mut hash, py, child.src(), &child.tail)?;
    }
    Ok(hash.finalize().into())
}

/// The digest of `root`, hashing only what changed since it was last asked.
pub fn digest(py: Python<'_>, root: &Arc<Node>) -> PyResult<[u8; 16]> {
    if let Some(found) = root.data.get(py).digest {
        return Ok(found);
    }
    let mut stack = vec![(root.clone(), false)];
    while let Some((node, children_done)) = stack.pop() {
        if children_done {
            let found = compute(py, &node.data.get(py))?;
            node.data.get_mut(py).digest = Some(found);
            continue;
        }
        let data = node.data.get(py);
        if data.digest.is_some() {
            continue;
        }
        stack.push((node.clone(), true));
        for child in &data.children {
            let child_data = child.data.get(py);
            if child_data.digest.is_none() && matches!(child_data.tag, Tag::Name(_)) {
                stack.push((child.clone(), false));
            }
        }
    }
    Ok(root.data.get(py).digest.expect("just computed"))
}
