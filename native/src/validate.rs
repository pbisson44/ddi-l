//! Schema validation over the IR that `ddi_l.schema_loader._ir` compiles.
//!
//! One walk over the tree finds every element that may break the schema.
//! The checks are conservative: an element is passed only when it is
//! certainly valid, and anything uncertain (a value outside the forms this
//! module recognises, an `xsi:type`, a wildcard) is flagged too. Python then
//! asks xmlschema about each flagged element alone, so the errors reported
//! are xmlschema's, word for word, while a valid document never needs it.
//!
//! A flag is `LOCAL` (the element's own attributes, text or simple content:
//! its children are checked here) or `OPAQUE` (its content model failed, or
//! it needs something only xmlschema does: xmlschema checks its whole
//! subtree). A document whose `xs:ID` values repeat, or that uses
//! `xs:IDREF`, is left to xmlschema entirely.

use std::cmp::Ordering;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyList;
use regex::Regex;
use serde::Deserialize;

use crate::element::{own, wrap, Element};
use crate::tree::{Node, NodeData, Tag};

const XSI: &str = "{http://www.w3.org/2001/XMLSchema-instance}";

pub const LOCAL: u8 = 0;
pub const OPAQUE: u8 = 1;
pub const WILDCARD: u8 = 2;

// ---- The IR, as written --------------------------------------------------------

#[derive(Deserialize)]
struct Ir {
    format: u32,
    names: Vec<String>,
    name_sets: Vec<Vec<u32>>,
    roots: HashMap<String, u32>,
    attributes: HashMap<String, u32>,
    elements: Vec<ElementIr>,
    complex: Vec<ComplexIr>,
    simple: Vec<SimpleIr>,
    models: Vec<ModelIr>,
    wildcards: Vec<WildcardIr>,
}

#[derive(Deserialize)]
struct ElementIr {
    #[serde(rename = "abstract")]
    is_abstract: bool,
    fixed: Option<String>,
    #[serde(rename = "type")]
    kind: (String, u32),
}

#[derive(Deserialize)]
struct AttrIr {
    #[serde(rename = "type")]
    simple: u32,
    #[serde(rename = "use")]
    usage: String,
    fixed: Option<String>,
}

#[derive(Deserialize)]
struct ComplexIr {
    #[serde(rename = "abstract")]
    is_abstract: bool,
    attrs: HashMap<String, AttrIr>,
    any_attr: Option<u32>,
    content: String,
    #[serde(default)]
    mixed: bool,
    model: Option<u32>,
    simple: Option<u32>,
}

#[derive(Deserialize, Default)]
struct FacetsIr {
    #[serde(default)]
    patterns: Vec<Vec<String>>,
    #[serde(default)]
    enumerations: Vec<Vec<String>>,
    #[serde(default)]
    length: Vec<String>,
    #[serde(default, rename = "minLength")]
    min_length: Vec<String>,
    #[serde(default, rename = "maxLength")]
    max_length: Vec<String>,
    #[serde(default, rename = "minInclusive")]
    min_inclusive: Vec<String>,
    #[serde(default, rename = "maxInclusive")]
    max_inclusive: Vec<String>,
    #[serde(default, rename = "minExclusive")]
    min_exclusive: Vec<String>,
    #[serde(default, rename = "maxExclusive")]
    max_exclusive: Vec<String>,
    #[serde(default, rename = "totalDigits")]
    total_digits: Vec<String>,
    #[serde(default, rename = "fractionDigits")]
    fraction_digits: Vec<String>,
    #[serde(default)]
    other: Vec<String>,
}

#[derive(Deserialize)]
struct SimpleIr {
    ws: Option<String>,
    variety: String,
    builtin: Option<String>,
    item: Option<u32>,
    members: Option<Vec<u32>>,
    #[serde(default)]
    facets: FacetsIr,
}

#[derive(Deserialize)]
struct StateIr {
    accept: bool,
    edges: Vec<(u32, u32, u32)>,
    wild: Vec<(u32, u32)>,
}

#[derive(Deserialize)]
struct ModelIr {
    states: Vec<StateIr>,
    cdata_ok: bool,
    empty_choice: bool,
}

#[derive(Deserialize)]
struct WildcardIr {
    namespaces: Vec<String>,
    process: String,
}

// ---- Compiled --------------------------------------------------------------------

#[derive(Clone, Copy, PartialEq)]
enum Space {
    Preserve,
    Replace,
    Collapse,
}

struct Simple {
    space: Space,
    variety: u8, // 0 atomic, 1 list, 2 union
    builtin: String,
    item: u32,
    members: Vec<u32>,
    facets: FacetsIr,
    /// Patterns per restriction step; `None` where one does not compile.
    patterns: Vec<Option<Vec<Regex>>>,
    id: bool,
    idref: bool,
}

/// A compiled schema the validator runs.
#[pyclass(frozen, module = "ddi_l_native._core", name = "Schema")]
pub struct Schema {
    name_ids: HashMap<String, u32>,
    name_sets: Vec<Vec<u32>>,
    roots: HashMap<u32, u32>,
    attributes: HashMap<u32, u32>,
    elements: Vec<ElementIr>,
    complex: Vec<(ComplexIr, HashMap<u32, AttrIr>)>,
    simple: Vec<Simple>,
    models: Vec<ModelIr>,
    wildcards: Vec<WildcardIr>,
}

fn space_of(ws: Option<&str>, builtin: &str) -> Space {
    match ws {
        Some("preserve") => Space::Preserve,
        Some("replace") => Space::Replace,
        Some("collapse") => Space::Collapse,
        _ => match builtin {
            "xs:string" | "xs:anySimpleType" => Space::Preserve,
            "xs:normalizedString" => Space::Replace,
            _ => Space::Collapse,
        },
    }
}

/// xmlschema's patterns are Python regular expressions, anchored with
/// `^(?:...)$(?!\n\Z)`; without the look-ahead, Rust's `$` means the same.
fn compile_pattern(pattern: &str) -> Option<Regex> {
    let body = pattern.strip_suffix(r"$(?!\n\Z)")?.strip_prefix('^')?;
    Regex::new(&format!(r"\A{body}\z")).ok()
}

#[pymethods]
impl Schema {
    #[new]
    fn new(text: &str) -> PyResult<Schema> {
        let ir: Ir =
            serde_json::from_str(text).map_err(|e| PyValueError::new_err(e.to_string()))?;
        if ir.format != 1 {
            return Err(PyValueError::new_err(format!(
                "unknown IR format {}",
                ir.format
            )));
        }
        let name_ids = ir
            .names
            .iter()
            .enumerate()
            .map(|(at, name)| (name.clone(), at as u32))
            .collect();
        let numbered = |map: HashMap<String, u32>| -> PyResult<HashMap<u32, u32>> {
            map.into_iter()
                .map(|(k, v)| {
                    k.parse::<u32>()
                        .map(|k| (k, v))
                        .map_err(|e| PyValueError::new_err(e.to_string()))
                })
                .collect()
        };
        let mut simple: Vec<Simple> = ir
            .simple
            .into_iter()
            .map(|s| {
                let builtin = s.builtin.clone().unwrap_or_default();
                let patterns = s
                    .facets
                    .patterns
                    .iter()
                    .map(|step| {
                        step.iter()
                            .map(|p| compile_pattern(p))
                            .collect::<Option<Vec<_>>>()
                    })
                    .collect();
                Simple {
                    space: space_of(s.ws.as_deref(), &builtin),
                    variety: match s.variety.as_str() {
                        "list" => 1,
                        "union" => 2,
                        _ => 0,
                    },
                    id: builtin == "xs:ID",
                    idref: builtin == "xs:IDREF" || builtin == "xs:IDREFS",
                    builtin,
                    item: s.item.unwrap_or(0),
                    members: s.members.unwrap_or_default(),
                    facets: s.facets,
                    patterns,
                }
            })
            .collect();
        // A list or union of references is a reference too.
        for at in 0..simple.len() {
            let idref = match simple[at].variety {
                1 => simple[simple[at].item as usize].idref,
                2 => simple[at].members.iter().any(|m| simple[*m as usize].idref),
                _ => simple[at].idref,
            };
            simple[at].idref = idref;
        }
        let complex = ir
            .complex
            .into_iter()
            .map(|mut c| {
                let attrs = std::mem::take(&mut c.attrs)
                    .into_iter()
                    .filter_map(|(k, v)| k.parse::<u32>().ok().map(|k| (k, v)))
                    .collect();
                (c, attrs)
            })
            .collect();
        Ok(Schema {
            name_ids,
            name_sets: ir.name_sets,
            roots: numbered(ir.roots)?,
            attributes: numbered(ir.attributes)?,
            elements: ir.elements,
            complex,
            simple,
            models: ir.models,
            wildcards: ir.wildcards,
        })
    }

    /// Validate the tree under `root`. Returns `None` when the document is
    /// left to xmlschema, or the flagged elements in document order as
    /// `(element, kind, declaration or wildcard, depth)`.
    fn validate<'py>(&self, root: &Bound<'py, Element>) -> PyResult<Option<Bound<'py, PyList>>> {
        let py = root.py();
        let mut walk = Walk {
            schema: self,
            py,
            found: Vec::new(),
            ids: HashSet::new(),
            whole: false,
        };
        let node = own(root).clone();
        let decl = node
            .data
            .get(py)
            .tag
            .name()
            .and_then(|name| self.name_ids.get(name))
            .and_then(|id| self.roots.get(id))
            .copied();
        match decl {
            None => return Ok(None),
            Some(decl) => walk.element(&node, decl, 0),
        }
        if walk.whole {
            return Ok(None);
        }
        let list = PyList::empty(py);
        for (node, kind, id, depth) in walk.found {
            list.append((wrap(py, &node)?, kind, id, depth))?;
        }
        Ok(Some(list))
    }
}

/// The 1-based line and 0-based column where `element`'s start tag began,
/// if it was parsed.
#[pyfunction]
pub fn source_position(element: &Bound<'_, Element>) -> Option<(usize, usize)> {
    let py = element.py();
    let data = own(element).data.get(py);
    if data.start == crate::tree::NO_START {
        return None;
    }
    Some(data.src()?.position(py, data.start))
}

struct Walk<'s, 'py> {
    schema: &'s Schema,
    py: Python<'py>,
    found: Vec<(Arc<Node>, u8, u32, u32)>,
    ids: HashSet<String>,
    /// The document needs xmlschema as a whole.
    whole: bool,
}

fn is_space(ch: char) -> bool {
    matches!(ch, ' ' | '\t' | '\n' | '\r')
}

fn blank(text: &str) -> bool {
    text.chars().all(is_space)
}

fn namespace_of(name: &str) -> &str {
    name.strip_prefix('{')
        .and_then(|rest| rest.split_once('}'))
        .map_or("", |(uri, _)| uri)
}

impl<'s, 'py> Walk<'s, 'py> {
    fn flag(&mut self, node: &Arc<Node>, kind: u8, id: u32, depth: u32) {
        self.found.push((node.clone(), kind, id, depth));
    }

    fn name_id(&self, name: &str) -> Option<u32> {
        self.schema.name_ids.get(name).copied()
    }

    fn in_set(&self, set: u32, name: u32) -> bool {
        self.schema.name_sets[set as usize]
            .binary_search(&name)
            .is_ok()
    }

    fn element(&mut self, node: &Arc<Node>, decl: u32, depth: u32) {
        let py = self.py;
        let schema = self.schema;
        let el = &schema.elements[decl as usize];
        let data = node.data.get(py);
        if el.is_abstract
            || data.attr(&format!("{XSI}type")).is_some()
            || data.attr(&format!("{XSI}nil")).is_some()
        {
            drop(data);
            return self.flag(node, OPAQUE, decl, depth);
        }
        let mut local = el.fixed.is_some();
        let (kind, number) = (el.kind.0.as_str(), el.kind.1);
        if kind == "s" {
            local |= !self.attributes_ok(&data, None)
                || !data.children.is_empty()
                || !self.text_ok(&data, number);
            drop(data);
            if local {
                self.flag(node, LOCAL, decl, depth);
            }
            return;
        }
        let (ct, _) = &schema.complex[number as usize];
        if ct.is_abstract {
            drop(data);
            return self.flag(node, OPAQUE, decl, depth);
        }
        local |= !self.attributes_ok(&data, Some(number));
        match ct.content.as_str() {
            "simple" => {
                local |= !data.children.is_empty() || !self.text_ok(&data, ct.simple.unwrap_or(0));
                drop(data);
                if local {
                    self.flag(node, LOCAL, decl, depth);
                }
                return;
            }
            "empty" => {
                if !data.children.is_empty() {
                    drop(data);
                    return self.flag(node, OPAQUE, decl, depth);
                }
                let text = self.text_of(&data);
                local |= !text.as_deref().is_none_or(blank);
                drop(data);
                if local {
                    self.flag(node, LOCAL, decl, depth);
                }
                return;
            }
            _ => {}
        }
        let model = &schema.models[ct.model.unwrap_or(0) as usize];
        if model.empty_choice {
            drop(data);
            return self.flag(node, OPAQUE, decl, depth);
        }
        if !ct.mixed && !model.cdata_ok {
            let text_blank = self.text_of(&data).as_deref().is_none_or(blank);
            let tails_blank = data.children.iter().all(|child| {
                let child = child.data.get(py);
                match &child.tail {
                    None => true,
                    Some(tail) => tail
                        .text(py, child.src())
                        .map(|t| blank(&t))
                        .unwrap_or(false),
                }
            });
            local |= !(text_blank && tails_blank);
        }
        // The content model, child by child.
        let children = data.children.clone();
        drop(data);
        let mut state = 0usize;
        let mut decls: Vec<(u32, bool)> = Vec::with_capacity(children.len());
        for child in &children {
            let child_data = child.data.get(py);
            let Tag::Name(name) = &child_data.tag else {
                drop(child_data);
                return self.flag(node, OPAQUE, decl, depth);
            };
            let row = &model.states[state];
            let id = self.name_id(&name.text);
            let mut next = None;
            if let Some(id) = id {
                for &(set, target, element) in &row.edges {
                    if self.in_set(set, id) {
                        next = Some((target, element, false));
                        break;
                    }
                }
            }
            if next.is_none() {
                let uri = namespace_of(&name.text);
                for &(wildcard, target) in &row.wild {
                    let w = &schema.wildcards[wildcard as usize];
                    let matches = w.namespaces.iter().any(|ns| ns == "##any" || ns == uri)
                        && !w
                            .namespaces
                            .iter()
                            .any(|ns| ns.starts_with("##") && ns != "##any");
                    if matches {
                        next = Some((target, wildcard, true));
                        break;
                    }
                }
            }
            drop(child_data);
            match next {
                Some((target, element, wild)) => {
                    state = target as usize;
                    decls.push((element, wild));
                }
                None => return self.flag(node, OPAQUE, decl, depth),
            }
        }
        if !model.states[state].accept {
            return self.flag(node, OPAQUE, decl, depth);
        }
        if local {
            self.flag(node, LOCAL, decl, depth);
        }
        for (child, (element, wild)) in children.iter().zip(decls) {
            if !wild {
                self.element(child, element, depth + 1);
            } else if schema.wildcards[element as usize].process != "skip" {
                self.flag(child, WILDCARD, element, depth + 1);
            }
        }
    }

    fn text_of(&self, data: &NodeData) -> Option<String> {
        data.text.as_ref().map(|text| {
            text.text(self.py, data.src())
                .map(|t| t.into_owned())
                .unwrap_or_else(|_| "\u{0}".into())
        })
    }

    fn text_ok(&mut self, data: &NodeData, simple: u32) -> bool {
        let text = self.text_of(data).unwrap_or_default();
        self.value_ok(simple, &text)
    }

    /// Whether the element's attributes are certainly valid for complex type
    /// `complex` (or for a simple type, which has none).
    fn attributes_ok(&mut self, data: &NodeData, complex: Option<u32>) -> bool {
        let schema = self.schema;
        let (ct, attrs) = match complex {
            Some(c) => {
                let (ct, attrs) = &schema.complex[c as usize];
                (Some(ct), Some(attrs))
            }
            None => (None, None),
        };
        let mut seen: HashSet<u32> = HashSet::new();
        for (name, value) in &data.attrs {
            let Ok(value) = value.text(self.py, data.src()) else {
                return false;
            };
            let id = self.name_id(&name.text);
            let declared = match (id, attrs) {
                (Some(id), Some(attrs)) => attrs.get(&id),
                _ => None,
            };
            if let Some(attr) = declared {
                seen.insert(id.unwrap_or(0));
                if attr.usage == "prohibited"
                    || attr
                        .fixed
                        .as_ref()
                        .is_some_and(|fixed| fixed != value.as_ref())
                    || !self.value_ok(attr.simple, &value)
                {
                    return false;
                }
                continue;
            }
            if name.text.starts_with(XSI) {
                let global = id.and_then(|id| schema.attributes.get(&id)).copied();
                match global {
                    Some(simple) if self.value_ok(simple, &value) => continue,
                    _ => return false,
                }
            }
            let Some(wildcard) = ct.and_then(|ct| ct.any_attr) else {
                return false;
            };
            let w = &schema.wildcards[wildcard as usize];
            let uri = namespace_of(&name.text);
            if !w.namespaces.iter().any(|ns| ns == "##any" || ns == uri)
                || w.namespaces
                    .iter()
                    .any(|ns| ns.starts_with("##") && ns != "##any")
            {
                return false;
            }
            if w.process != "skip" {
                match id.and_then(|id| schema.attributes.get(&id)).copied() {
                    Some(simple) if self.value_ok(simple, &value) => {}
                    Some(_) => return false,
                    None if w.process == "strict" => return false,
                    None => {}
                }
            }
        }
        if let Some(attrs) = attrs {
            for (id, attr) in attrs {
                if attr.usage == "required" && !seen.contains(id) {
                    return false;
                }
            }
        }
        true
    }

    /// Whether `raw` is certainly a valid value of simple type `simple`.
    fn value_ok(&mut self, simple: u32, raw: &str) -> bool {
        let schema = self.schema;
        let t = &schema.simple[simple as usize];
        if t.idref {
            self.whole = true;
            return false;
        }
        let value = normalize(raw, t.space);
        let ok = match t.variety {
            0 => builtin_ok(&t.builtin, &value) && facets_ok(t, &value),
            1 => {
                let items: Vec<&str> = value.split(' ').filter(|item| !item.is_empty()).collect();
                let facets = &t.facets;
                facets.patterns.is_empty()
                    && facets.enumerations.is_empty()
                    && lengths_ok(facets, items.len())
                    && bounds_free(facets)
                    && items.iter().all(|item| self.value_ok(t.item, item))
            }
            _ => {
                no_facets(&t.facets)
                    && t.members
                        .clone()
                        .into_iter()
                        .any(|member| self.value_ok(member, raw))
            }
        };
        if ok && t.id && !self.ids.insert(value.clone()) {
            self.whole = true;
            return false;
        }
        ok
    }
}

fn normalize(raw: &str, space: Space) -> String {
    match space {
        Space::Preserve => raw.to_owned(),
        Space::Replace => raw.replace(['\t', '\n', '\r'], " "),
        Space::Collapse => raw
            .split(is_space)
            .filter(|part| !part.is_empty())
            .collect::<Vec<_>>()
            .join(" "),
    }
}

fn no_facets(f: &FacetsIr) -> bool {
    f.patterns.is_empty()
        && f.enumerations.is_empty()
        && f.length.is_empty()
        && f.min_length.is_empty()
        && f.max_length.is_empty()
        && bounds_free(f)
}

fn bounds_free(f: &FacetsIr) -> bool {
    f.min_inclusive.is_empty()
        && f.max_inclusive.is_empty()
        && f.min_exclusive.is_empty()
        && f.max_exclusive.is_empty()
        && f.total_digits.is_empty()
        && f.fraction_digits.is_empty()
        && f.other.is_empty()
}

fn lengths_ok(f: &FacetsIr, length: usize) -> bool {
    let all = |bounds: &[String], test: &dyn Fn(usize) -> bool| {
        bounds.iter().all(|b| b.parse::<usize>().is_ok_and(test))
    };
    all(&f.length, &|n| length == n)
        && all(&f.min_length, &|n| length >= n)
        && all(&f.max_length, &|n| length <= n)
}

fn string_like(builtin: &str) -> bool {
    matches!(
        builtin,
        "xs:string"
            | "xs:normalizedString"
            | "xs:token"
            | "xs:language"
            | "xs:NMTOKEN"
            | "xs:Name"
            | "xs:NCName"
            | "xs:ID"
    )
}

fn decimal_like(builtin: &str) -> bool {
    matches!(
        builtin,
        "xs:decimal" | "xs:integer" | "xs:nonNegativeInteger" | "xs:positiveInteger"
    )
}

fn facets_ok(t: &Simple, value: &str) -> bool {
    let f = &t.facets;
    if !f.other.is_empty() {
        return false;
    }
    for step in &t.patterns {
        match step {
            Some(patterns) if patterns.iter().any(|p| p.is_match(value)) => {}
            _ => return false,
        }
    }
    // Patterns are tested on lines; a value spanning lines is left to xmlschema.
    if !t.patterns.is_empty() && value.contains(['\n', '\r']) {
        return false;
    }
    if !f
        .enumerations
        .iter()
        .all(|step| step.iter().any(|literal| literal == value))
    {
        return false;
    }
    let has_lengths = !(f.length.is_empty() && f.min_length.is_empty() && f.max_length.is_empty());
    if has_lengths && (!string_like(&t.builtin) || !lengths_ok(f, value.chars().count())) {
        return false;
    }
    let has_bounds = !bounds_free(f);
    if has_bounds {
        if !decimal_like(&t.builtin) {
            return false;
        }
        let Some(number) = Decimal::parse(value) else {
            return false;
        };
        let all = |bounds: &[String], test: &dyn Fn(Ordering) -> bool| {
            bounds
                .iter()
                .all(|b| Decimal::parse(b).is_some_and(|bound| test(number.cmp(&bound))))
        };
        let digits = |bounds: &[String], have: usize| {
            bounds
                .iter()
                .all(|b| b.parse::<usize>().is_ok_and(|n| have <= n))
        };
        if !(all(&f.min_inclusive, &|o| o != Ordering::Less)
            && all(&f.max_inclusive, &|o| o != Ordering::Greater)
            && all(&f.min_exclusive, &|o| o == Ordering::Greater)
            && all(&f.max_exclusive, &|o| o == Ordering::Less)
            && digits(&f.total_digits, number.total_digits())
            && digits(&f.fraction_digits, number.fraction.len()))
        {
            return false;
        }
    }
    true
}

// ---- Values certainly valid for a builtin type ------------------------------------

fn ascii_all(value: &str, allowed: impl Fn(u8) -> bool) -> bool {
    !value.is_empty() && value.bytes().all(allowed)
}

fn name_char(b: u8) -> bool {
    b.is_ascii_alphanumeric() || matches!(b, b'.' | b'-' | b'_')
}

fn ncname(value: &str) -> bool {
    value
        .as_bytes()
        .first()
        .is_some_and(|b| b.is_ascii_alphabetic() || *b == b'_')
        && value.bytes().all(name_char)
}

fn digits(value: &str) -> bool {
    !value.is_empty() && value.bytes().all(|b| b.is_ascii_digit())
}

/// A decimal number, for comparing with facet bounds.
#[derive(PartialEq, Eq)]
struct Decimal {
    negative: bool,
    whole: String,
    fraction: String,
}

impl Decimal {
    fn parse(text: &str) -> Option<Decimal> {
        let (negative, rest) = match text.as_bytes().first()? {
            b'-' => (true, &text[1..]),
            b'+' => (false, &text[1..]),
            _ => (false, text),
        };
        let (whole, fraction) = rest.split_once('.').unwrap_or((rest, ""));
        if (whole.is_empty() && fraction.is_empty())
            || !whole.bytes().all(|b| b.is_ascii_digit())
            || !fraction.bytes().all(|b| b.is_ascii_digit())
        {
            return None;
        }
        let whole = whole.trim_start_matches('0').to_owned();
        let fraction = fraction.trim_end_matches('0').to_owned();
        let zero = whole.is_empty() && fraction.is_empty();
        Some(Decimal {
            negative: negative && !zero,
            whole,
            fraction,
        })
    }

    fn total_digits(&self) -> usize {
        (self.whole.len() + self.fraction.len()).max(1)
    }

    fn magnitude(&self, other: &Decimal) -> Ordering {
        self.whole
            .len()
            .cmp(&other.whole.len())
            .then_with(|| self.whole.cmp(&other.whole))
            .then_with(|| self.fraction.cmp(&other.fraction))
    }
}

impl Ord for Decimal {
    fn cmp(&self, other: &Decimal) -> Ordering {
        match (self.negative, other.negative) {
            (false, true) => Ordering::Greater,
            (true, false) => Ordering::Less,
            (false, false) => self.magnitude(other),
            (true, true) => other.magnitude(self),
        }
    }
}

impl PartialOrd for Decimal {
    fn partial_cmp(&self, other: &Decimal) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn decimal(value: &str) -> bool {
    Decimal::parse(value).is_some()
}

fn integer(value: &str) -> bool {
    let rest = value.strip_prefix(['+', '-']).unwrap_or(value);
    digits(rest)
}

fn floating(value: &str, max_exponent: i32) -> bool {
    if matches!(value, "INF" | "-INF" | "NaN") {
        return true;
    }
    let (mantissa, exponent) = match value.find(['e', 'E']) {
        Some(at) => (&value[..at], Some(&value[at + 1..])),
        None => (value, None),
    };
    decimal(mantissa)
        && exponent.is_none_or(|e| {
            integer(e)
                && e.trim_start_matches(['+', '-']).len() <= 3
                && e.parse::<i32>().is_ok_and(|n| n.abs() <= max_exponent)
        })
}

fn days_in(year: u32, month: u32) -> u32 {
    match month {
        2 if (year % 4 == 0 && year % 100 != 0) || year % 400 == 0 => 29,
        2 => 28,
        4 | 6 | 9 | 11 => 30,
        _ => 31,
    }
}

fn two(value: &str) -> Option<u32> {
    (value.len() == 2 && digits(value))
        .then(|| value.parse().ok())
        .flatten()
}

/// A timezone, or nothing.
fn zone(value: &str) -> bool {
    if value.is_empty() || value == "Z" {
        return true;
    }
    let Some(rest) = value.strip_prefix(['+', '-']) else {
        return false;
    };
    let Some((hours, minutes)) = rest.split_once(':') else {
        return false;
    };
    match (two(hours), two(minutes)) {
        (Some(h), Some(m)) => m < 60 && (h < 14 || (h == 14 && m == 0)),
        _ => false,
    }
}

fn year(value: &str) -> Option<u32> {
    (value.len() == 4 && digits(value))
        .then(|| value.parse::<u32>().ok())
        .flatten()
        .filter(|y| *y > 0)
}

/// `YYYY-MM-DD` and what follows it.
fn date_part(value: &str) -> Option<&str> {
    let (y, rest) = (value.get(..4)?, value.get(4..)?);
    let year = year(y)?;
    let rest = rest.strip_prefix('-')?;
    let month = two(rest.get(..2)?)?;
    let rest = rest.get(2..)?.strip_prefix('-')?;
    let day = two(rest.get(..2)?)?;
    ((1..=12).contains(&month) && day >= 1 && day <= days_in(year, month)).then(|| &rest[2..])
}

/// `hh:mm:ss(.s+)?` and what follows it.
fn time_part(value: &str) -> Option<&str> {
    let hour = two(value.get(..2)?)?;
    let rest = value.get(2..)?.strip_prefix(':')?;
    let minute = two(rest.get(..2)?)?;
    let rest = rest.get(2..)?.strip_prefix(':')?;
    let second = two(rest.get(..2)?)?;
    let mut rest = &rest[2..];
    if let Some(fraction) = rest.strip_prefix('.') {
        let end = fraction
            .bytes()
            .position(|b| !b.is_ascii_digit())
            .unwrap_or(fraction.len());
        if end == 0 {
            return None;
        }
        rest = &fraction[end..];
    }
    (hour < 24 && minute < 60 && second < 60).then_some(rest)
}

fn duration(value: &str) -> bool {
    let rest = value.strip_prefix('-').unwrap_or(value);
    let Some(rest) = rest.strip_prefix('P') else {
        return false;
    };
    let (date, time) = match rest.split_once('T') {
        Some((date, time)) => (date, Some(time)),
        None => (rest, None),
    };
    let mut parts = 0;
    let mut scan = |text: &str, units: &[u8], seconds: bool| -> bool {
        let mut at = 0;
        let mut unit = 0;
        let bytes = text.as_bytes();
        while at < bytes.len() {
            let start = at;
            while at < bytes.len() && bytes[at].is_ascii_digit() {
                at += 1;
            }
            if seconds && at < bytes.len() && bytes[at] == b'.' {
                at += 1;
                let fraction = at;
                while at < bytes.len() && bytes[at].is_ascii_digit() {
                    at += 1;
                }
                if at == fraction || bytes.get(at) != Some(&b'S') {
                    return false;
                }
            }
            if at == start || at >= bytes.len() {
                return false;
            }
            let Some(found) = units[unit..].iter().position(|u| *u == bytes[at]) else {
                return false;
            };
            unit += found + 1;
            at += 1;
            parts += 1;
        }
        true
    };
    if !scan(date, b"YMD", false) {
        return false;
    }
    match time {
        Some(time) => !time.is_empty() && scan(time, b"HMS", true) && parts > 0,
        None => parts > 0,
    }
}

fn builtin_ok(builtin: &str, value: &str) -> bool {
    match builtin {
        "xs:string" | "xs:anySimpleType" | "xs:normalizedString" | "xs:token" => true,
        "xs:language" => {
            let mut parts = value.split('-');
            parts.next().is_some_and(|p| {
                (1..=8).contains(&p.len()) && p.bytes().all(|b| b.is_ascii_alphabetic())
            }) && parts
                .all(|p| (1..=8).contains(&p.len()) && p.bytes().all(|b| b.is_ascii_alphanumeric()))
        }
        "xs:NMTOKEN" => ascii_all(value, |b| name_char(b) || b == b':'),
        "xs:Name" => {
            value
                .as_bytes()
                .first()
                .is_some_and(|b| b.is_ascii_alphabetic() || matches!(b, b'_' | b':'))
                && value.bytes().all(|b| name_char(b) || b == b':')
        }
        "xs:NCName" | "xs:ID" => ncname(value),
        "xs:boolean" => matches!(value, "true" | "false" | "1" | "0"),
        "xs:decimal" => decimal(value),
        "xs:integer" => integer(value),
        "xs:nonNegativeInteger" => digits(value.strip_prefix('+').unwrap_or(value)),
        "xs:positiveInteger" => {
            let rest = value.strip_prefix('+').unwrap_or(value);
            digits(rest) && rest.bytes().any(|b| b != b'0')
        }
        "xs:float" => floating(value, 30),
        "xs:double" => floating(value, 300),
        "xs:anyURI" => {
            !value.is_empty()
                && value
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b"-._~:/?#@!$&'()*+,;=".contains(&b))
        }
        "xs:date" => date_part(value).is_some_and(zone),
        "xs:dateTime" => date_part(value)
            .and_then(|rest| rest.strip_prefix('T'))
            .and_then(time_part)
            .is_some_and(zone),
        "xs:time" => time_part(value).is_some_and(zone),
        "xs:gYear" => value.get(..4).and_then(year).is_some() && zone(&value[4..]),
        "xs:gYearMonth" => {
            value.get(..4).and_then(year).is_some()
                && value.get(4..5) == Some("-")
                && value
                    .get(5..7)
                    .and_then(two)
                    .is_some_and(|m| (1..=12).contains(&m))
                && zone(value.get(7..).unwrap_or("-"))
        }
        "xs:duration" => duration(value),
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn dates_and_durations() {
        assert!(builtin_ok("xs:date", "2024-02-29"));
        assert!(!builtin_ok("xs:date", "2023-02-29"));
        assert!(builtin_ok("xs:dateTime", "2024-01-31T23:59:59.5+05:30"));
        assert!(!builtin_ok("xs:dateTime", "2024-01-31T24:00:00"));
        assert!(builtin_ok("xs:duration", "P1Y2M3DT4H5M6.5S"));
        assert!(!builtin_ok("xs:duration", "P"));
        assert!(!builtin_ok("xs:duration", "PT"));
        assert!(!builtin_ok("xs:duration", "P1D2Y"));
        assert!(builtin_ok("xs:gYearMonth", "2024-12Z"));
    }

    #[test]
    fn numbers_compare() {
        let a = Decimal::parse("-1.50").unwrap();
        let b = Decimal::parse("-1.5").unwrap();
        assert_eq!(a.cmp(&b), Ordering::Equal);
        assert!(Decimal::parse("10").unwrap() > Decimal::parse("9.99").unwrap());
        assert!(Decimal::parse("-0").unwrap() == Decimal::parse("0").unwrap());
    }
}
