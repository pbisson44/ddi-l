//! A hardened XML 1.0 parser with namespaces that builds the tree directly.
//!
//! It reads what Python's standard parser reads and builds the same tree:
//! tags and attribute names in Clark notation, namespace declarations
//! dropped, comments and processing instructions dropped (the text around
//! them joined), every whitespace text kept. A document type declaration is
//! refused, so there are no entities beyond the five predefined ones and
//! nothing is fetched.

use std::collections::HashMap;
use std::sync::Arc;

use memchr::{memchr, memchr2, memmem};

use crate::tree::{as_text, Name, NameRef, Node, NodeData, Source, Tag, Val};

pub const XML_NS: &str = "http://www.w3.org/XML/1998/namespace";
pub const DOCTYPE_REFUSED: &str = "Document type declarations are not permitted in DDI documents.";

pub const INVALID: &str = "not well-formed (invalid token)";

#[derive(Debug)]
pub struct ParseError {
    pub message: String,
    pub offset: usize,
    /// Reported without a position, as the other backends do.
    pub bare: bool,
}

fn error<T>(message: &str, offset: usize) -> Result<T, ParseError> {
    Err(ParseError {
        message: message.to_owned(),
        offset,
        bare: false,
    })
}

/// An element and where it is in the source: start, end of its start tag,
/// start of its end tag, end (the last two equal the second when it is
/// empty), and its depth.
pub struct Placed {
    pub node: Arc<Node>,
    pub span: [u32; 4],
    pub depth: u32,
}

pub struct Parsed {
    pub root: Arc<Node>,
    /// Every element in document order, when asked for.
    pub placed: Vec<Placed>,
}

pub fn parse(data: &[u8], src: &Arc<Source>, index: bool) -> Result<Parsed, ParseError> {
    if data.len() >= u32::MAX as usize {
        return error("document too large", 0);
    }
    let mut parser = Parser {
        data,
        pos: 0,
        src: src.clone(),
        index,
        placed: Vec::new(),
        uris: vec!["".into(), XML_NS.into()],
        uri_ids: HashMap::new(),
        names: HashMap::new(),
        scope: Vec::new(),
        attrs: Vec::new(),
        cache: vec![None; CACHE_SLOTS],
    };
    parser.uri_ids.insert("".into(), 0);
    parser.uri_ids.insert(XML_NS.into(), 1);
    let root = parser.document()?;
    Ok(Parsed {
        root,
        placed: parser.placed,
    })
}

// ---- Characters --------------------------------------------------------------

const fn table(start: bool) -> [bool; 256] {
    let mut table = [false; 256];
    let mut byte = 0;
    while byte < 256 {
        let b = byte as u8;
        table[byte] = b >= 0x80
            || b.is_ascii_alphabetic()
            || b == b'_'
            || b == b':'
            || (!start && (b.is_ascii_digit() || b == b'-' || b == b'.'));
        byte += 1;
    }
    table
}

static NAME_START: [bool; 256] = table(true);
static NAME_CHAR: [bool; 256] = table(false);

fn is_space(byte: u8) -> bool {
    matches!(byte, b' ' | b'\t' | b'\n' | b'\r')
}

fn is_xml_char(ch: char) -> bool {
    matches!(ch, '\t' | '\n' | '\r' | '\u{20}'..='\u{D7FF}' | '\u{E000}'..='\u{FFFD}' | '\u{10000}'..)
}

fn is_control(byte: u8) -> bool {
    byte < 0x20 && !matches!(byte, b'\t' | b'\n' | b'\r')
}

/// The first control character XML forbids, checking 32 bytes at a time
/// (a loop the compiler vectorises).
fn first_control(data: &[u8]) -> Option<usize> {
    let mut chunks = data.chunks_exact(32);
    for (number, chunk) in (&mut chunks).enumerate() {
        let mut found = 0u8;
        for &byte in chunk {
            found |= (byte < 0x20) as u8
                & (byte != b'\t') as u8
                & (byte != b'\n') as u8
                & (byte != b'\r') as u8;
        }
        if found != 0 {
            return chunk
                .iter()
                .position(|&b| is_control(b))
                .map(|at| number * 32 + at);
        }
    }
    let done = data.len() - chunks.remainder().len();
    chunks
        .remainder()
        .iter()
        .position(|&b| is_control(b))
        .map(|at| done + at)
}

/// The input must be UTF-8 holding only characters XML allows.
fn check_characters(data: &[u8]) -> Result<(), ParseError> {
    if let Err(problem) = std::str::from_utf8(data) {
        return error(INVALID, problem.valid_up_to());
    }
    if let Some(offset) = first_control(data) {
        return error(INVALID, offset);
    }
    // U+FFFE and U+FFFF are not characters.
    let finder = memmem::Finder::new(b"\xEF\xBF");
    for offset in finder.find_iter(data) {
        if matches!(data.get(offset + 2), Some(0xBE | 0xBF)) {
            return error(INVALID, offset);
        }
    }
    Ok(())
}

// ---- Text being gathered -------------------------------------------------------

/// The character data since the last tag: none, one range of the source,
/// or decoded text.
enum Acc {
    None,
    Src(u32, u32),
    Own(String),
}

impl Acc {
    fn own(&mut self, data: &[u8]) -> &mut String {
        if let Acc::Src(start, end) = *self {
            *self = Acc::Own(as_text(&data[start as usize..end as usize]).to_owned());
        } else if let Acc::None = self {
            *self = Acc::Own(String::new());
        }
        match self {
            Acc::Own(text) => text,
            _ => unreachable!(),
        }
    }

    fn range(&mut self, data: &[u8], start: usize, end: usize) {
        if start == end {
            return;
        }
        if let Acc::None = self {
            *self = Acc::Src(start as u32, end as u32);
        } else {
            self.own(data).push_str(as_text(&data[start..end]));
        }
    }

    /// Text with its line ends normalised to `\n`.
    fn lines(&mut self, data: &[u8], start: usize, end: usize) {
        if memchr(b'\r', &data[start..end]).is_none() {
            return self.range(data, start, end);
        }
        let text = as_text(&data[start..end])
            .replace("\r\n", "\n")
            .replace('\r', "\n");
        if !text.is_empty() {
            self.own(data).push_str(&text);
        }
    }

    fn take(&mut self) -> Option<Val> {
        match std::mem::replace(self, Acc::None) {
            Acc::None => None,
            Acc::Src(start, end) => Some(Val::Src(start, end)),
            Acc::Own(text) => Some(Val::Own(text.into_boxed_str())),
        }
    }
}

// ---- The parser ----------------------------------------------------------------

struct Open<'a> {
    node: Arc<Node>,
    qname: &'a [u8],
    scope_len: usize,
    placed: usize,
}

/// A start tag read: the new element, whether it is empty, its qualified
/// name and the scope length to restore at its end.
type StartTag<'a> = (Arc<Node>, bool, &'a [u8], usize);

struct RawAttr<'a> {
    qname: &'a [u8],
    value: Val,
    at: usize,
}

struct Parser<'a> {
    data: &'a [u8],
    pos: usize,
    src: Arc<Source>,
    index: bool,
    placed: Vec<Placed>,
    uris: Vec<Box<str>>,
    uri_ids: HashMap<Box<str>, u32>,
    names: HashMap<(u32, &'a [u8]), NameRef>,
    /// In-scope namespace bindings, innermost last: prefix ("" for the
    /// default namespace), its `prefix_key` and URI id (0 for none).
    scope: Vec<(&'a [u8], u64, u32)>,
    attrs: Vec<RawAttr<'a>>,
    cache: Vec<Option<(u32, &'a [u8], NameRef)>>,
}

const CACHE_SLOTS: usize = 509;

/// A prefix of up to seven bytes packed in a word, or `LONG`.
const LONG: u64 = u64::MAX;

fn prefix_key(prefix: &[u8]) -> u64 {
    if prefix.len() > 7 {
        return LONG;
    }
    let mut key = prefix.len() as u64;
    for &byte in prefix {
        key = (key << 8) | byte as u64;
    }
    key
}

fn find_colon(name: &[u8]) -> Option<usize> {
    name.iter().position(|&b| b == b':')
}

impl<'a> Parser<'a> {
    fn document(&mut self) -> Result<Arc<Node>, ParseError> {
        let data = self.data;
        if data.starts_with(b"\xEF\xBB\xBF") {
            self.pos = 3;
        }
        check_characters(data)?;
        let rest = &data[self.pos..];
        if rest.starts_with(b"<?xml") && rest.get(5).is_some_and(|&b| is_space(b) || b == b'?') {
            self.declaration()?;
        }
        self.misc(true)?;
        if self.pos >= data.len() {
            return error("no element found", data.len());
        }
        let root = self.elements()?;
        self.misc(false)?;
        Ok(root)
    }

    fn skip_space(&mut self) -> bool {
        let start = self.pos;
        while self.pos < self.data.len() && is_space(self.data[self.pos]) {
            self.pos += 1;
        }
        self.pos > start
    }

    fn peek(&self, offset: usize) -> Option<u8> {
        self.data.get(self.pos + offset).copied()
    }

    fn starts_with(&self, prefix: &[u8]) -> bool {
        self.data[self.pos..].starts_with(prefix)
    }

    fn name(&mut self) -> Result<&'a [u8], ParseError> {
        let data = self.data;
        let start = self.pos;
        if !data.get(start).is_some_and(|&b| NAME_START[b as usize]) {
            return error(INVALID, start);
        }
        let mut end = start + 1;
        while end < data.len() && NAME_CHAR[data[end] as usize] {
            end += 1;
        }
        self.pos = end;
        Ok(&data[start..end])
    }

    /// The XML declaration: version, then encoding and standalone if given.
    fn declaration(&mut self) -> Result<(), ParseError> {
        let start = self.pos;
        let Some(length) = memmem::find(&self.data[start..], b"?>") else {
            return error("unclosed token", start);
        };
        let end = start + length;
        self.pos = start + 5;
        let mut seen = Vec::new();
        loop {
            let spaced = self.skip_space();
            if self.pos >= end {
                break;
            }
            if !spaced {
                return error("XML declaration not well-formed", self.pos);
            }
            let name = self.name()?;
            self.skip_space();
            if self.peek(0) != Some(b'=') {
                return error("XML declaration not well-formed", self.pos);
            }
            self.pos += 1;
            self.skip_space();
            let Some(quote @ (b'"' | b'\'')) = self.peek(0) else {
                return error("XML declaration not well-formed", self.pos);
            };
            let Some(close) = memchr(quote, &self.data[self.pos + 1..end]) else {
                return error("XML declaration not well-formed", self.pos);
            };
            self.pos += close + 2;
            seen.push(name);
        }
        let expected: [&[u8]; 3] = [b"version", b"encoding", b"standalone"];
        let mut next = 0;
        for name in &seen {
            match expected[next..]
                .iter()
                .position(|candidate| candidate == name)
            {
                Some(found) => next += found + 1,
                None => return error("XML declaration not well-formed", start),
            }
        }
        if seen.first() != Some(&&b"version"[..]) {
            return error("XML declaration not well-formed", start);
        }
        self.pos = end + 2;
        Ok(())
    }

    /// Whitespace, comments and processing instructions before or after the
    /// root element.
    fn misc(&mut self, prolog: bool) -> Result<(), ParseError> {
        loop {
            self.skip_space();
            if self.pos >= self.data.len() {
                return Ok(());
            }
            if self.starts_with(b"<!--") {
                self.comment()?;
            } else if self.starts_with(b"<?") {
                self.instruction()?;
            } else if prolog && self.starts_with(b"<!DOCTYPE") {
                return Err(ParseError {
                    message: DOCTYPE_REFUSED.to_owned(),
                    offset: self.pos,
                    bare: true,
                });
            } else if prolog
                && self.peek(0) == Some(b'<')
                && self.peek(1).is_some_and(|b| NAME_START[b as usize])
            {
                return Ok(());
            } else if prolog {
                return error(
                    if self.peek(0) == Some(b'<') {
                        INVALID
                    } else {
                        "syntax error"
                    },
                    self.pos,
                );
            } else {
                return error("junk after document element", self.pos);
            }
        }
    }

    fn comment(&mut self) -> Result<(), ParseError> {
        let start = self.pos;
        let body = start + 4;
        let Some(dashes) = memmem::find(&self.data[body..], b"--") else {
            return error("unclosed token", start);
        };
        if self.data.get(body + dashes + 2) != Some(&b'>') {
            return error(INVALID, body + dashes);
        }
        self.pos = body + dashes + 3;
        Ok(())
    }

    fn instruction(&mut self) -> Result<(), ParseError> {
        let start = self.pos;
        self.pos += 2;
        let target = self.name()?;
        if target.eq_ignore_ascii_case(b"xml") {
            return error("XML or text declaration not at start of entity", start);
        }
        if !self.starts_with(b"?>") && !self.skip_space() {
            return error(INVALID, self.pos);
        }
        let Some(end) = memmem::find(&self.data[self.pos..], b"?>") else {
            return error("unclosed token", start);
        };
        self.pos += end + 2;
        Ok(())
    }

    fn cdata(&mut self, text: &mut Acc) -> Result<(), ParseError> {
        let start = self.pos;
        let body = start + 9;
        let Some(length) = memmem::find(&self.data[body..], b"]]>") else {
            return error("unclosed CDATA section", start);
        };
        text.lines(self.data, body, body + length);
        self.pos = body + length + 3;
        Ok(())
    }

    /// A character or entity reference, at `&`.
    fn reference(&mut self) -> Result<char, ParseError> {
        let start = self.pos;
        let rest = &self.data[start + 1..];
        let Some(semicolon) = memchr(b';', &rest[..rest.len().min(32)]) else {
            return error(INVALID, start);
        };
        let body = &rest[..semicolon];
        let found = if let Some(number) = body.strip_prefix(b"#") {
            let (digits, radix) = match number.strip_prefix(b"x") {
                Some(hex) => (hex, 16),
                None => (number, 10),
            };
            if digits.is_empty() || !digits.iter().all(|b| (*b as char).is_digit(radix)) {
                return error(INVALID, start);
            }
            match u32::from_str_radix(as_text(digits), radix)
                .ok()
                .and_then(char::from_u32)
            {
                Some(ch) if is_xml_char(ch) => ch,
                _ => return error("reference to invalid character number", start),
            }
        } else {
            match body {
                b"lt" => '<',
                b"gt" => '>',
                b"amp" => '&',
                b"apos" => '\'',
                b"quot" => '"',
                _ if !body.is_empty()
                    && NAME_START[body[0] as usize]
                    && body.iter().all(|&b| NAME_CHAR[b as usize]) =>
                {
                    return error("undefined entity", start)
                }
                _ => return error(INVALID, start),
            }
        };
        self.pos = start + semicolon + 2;
        Ok(found)
    }

    fn uri_id(&mut self, uri: &str) -> u32 {
        if let Some(&id) = self.uri_ids.get(uri) {
            return id;
        }
        let id = self.uris.len() as u32;
        self.uris.push(uri.into());
        self.uri_ids.insert(uri.into(), id);
        id
    }

    fn lookup(&self, prefix: &[u8]) -> Option<u32> {
        if prefix == b"xml" {
            return Some(1);
        }
        let key = prefix_key(prefix);
        self.scope
            .iter()
            .rev()
            .find(|(bound, bound_key, _)| *bound_key == key && (key != LONG || *bound == prefix))
            .map(|(_, _, id)| *id)
    }

    fn intern(&mut self, uri: u32, local: &'a [u8]) -> NameRef {
        // A small cache in front of the map: a miss costs a map lookup, so
        // names chosen to collide in it cost no more than without it.
        let mut slot = uri as usize ^ local.len().wrapping_mul(31);
        for &byte in local {
            slot = slot.wrapping_mul(33) ^ byte as usize;
        }
        let slot = slot % CACHE_SLOTS;
        if let Some((cached_uri, cached_local, name)) = &self.cache[slot] {
            if *cached_uri == uri && *cached_local == local {
                return name.clone();
            }
        }
        let name = self.intern_slow(uri, local);
        self.cache[slot] = Some((uri, local, name.clone()));
        name
    }

    fn intern_slow(&mut self, uri: u32, local: &'a [u8]) -> NameRef {
        if let Some(name) = self.names.get(&(uri, local)) {
            return name.clone();
        }
        let local_text = as_text(local);
        let name = if uri == 0 {
            Name::new(local_text)
        } else {
            Name::new(&format!("{{{}}}{}", self.uris[uri as usize], local_text))
        };
        self.names.insert((uri, local), name.clone());
        name
    }

    /// The Clark name of a qualified name; `element` names take the default
    /// namespace when unprefixed.
    fn resolve(
        &mut self,
        qname: &'a [u8],
        at: usize,
        element: bool,
    ) -> Result<NameRef, ParseError> {
        match find_colon(qname) {
            None => {
                let uri = if element {
                    self.lookup(b"").unwrap_or(0)
                } else {
                    0
                };
                Ok(self.intern(uri, qname))
            }
            Some(colon) => {
                let (prefix, local) = (&qname[..colon], &qname[colon + 1..]);
                if prefix.is_empty()
                    || local.is_empty()
                    || find_colon(local).is_some()
                    || !NAME_START[local[0] as usize]
                {
                    return error(INVALID, at);
                }
                if prefix == b"xmlns" {
                    return error(
                        "reserved prefix (xmlns) must not be declared or undeclared",
                        at,
                    );
                }
                match self.lookup(prefix) {
                    Some(uri) => Ok(self.intern(uri, local)),
                    None => error("unbound prefix", at),
                }
            }
        }
    }

    /// An attribute value, at its opening quote.
    fn value(&mut self) -> Result<Val, ParseError> {
        let data = self.data;
        let quote = data[self.pos];
        let start = self.pos + 1;
        let Some(length) = memchr(quote, &data[start..]) else {
            return error("unclosed token", self.pos);
        };
        let end = start + length;
        self.pos = end + 1;
        let raw = &data[start..end];
        if !raw
            .iter()
            .any(|b| matches!(b, b'<' | b'&' | b'\t' | b'\n' | b'\r'))
        {
            return Ok(Val::Src(start as u32, end as u32));
        }
        let mut text = String::with_capacity(raw.len());
        let mut at = start;
        while at < end {
            match data[at] {
                b'<' => return error(INVALID, at),
                b'&' => {
                    let saved = self.pos;
                    self.pos = at;
                    text.push(self.reference()?);
                    at = self.pos;
                    self.pos = saved;
                }
                b'\r' => {
                    text.push(' ');
                    at += if data.get(at + 1) == Some(&b'\n') {
                        2
                    } else {
                        1
                    };
                }
                b'\t' | b'\n' => {
                    text.push(' ');
                    at += 1;
                }
                _ => {
                    let run = data[at..end]
                        .iter()
                        .position(|b| matches!(b, b'<' | b'&' | b'\t' | b'\n' | b'\r'))
                        .unwrap_or(end - at);
                    text.push_str(as_text(&data[at..at + run]));
                    at += run;
                }
            }
        }
        Ok(Val::Own(text.into_boxed_str()))
    }

    /// A start tag, at `<`.
    fn start_tag(&mut self) -> Result<StartTag<'a>, ParseError> {
        let data = self.data;
        let start = self.pos;
        self.pos += 1;
        let qname = self.name()?;
        self.attrs.clear();
        let empty = loop {
            let spaced = self.skip_space();
            match self.peek(0) {
                Some(b'>') => {
                    self.pos += 1;
                    break false;
                }
                Some(b'/') => {
                    if self.peek(1) != Some(b'>') {
                        return error(INVALID, self.pos);
                    }
                    self.pos += 2;
                    break true;
                }
                Some(_) if spaced => {
                    let at = self.pos;
                    let name = self.name()?;
                    self.skip_space();
                    if self.peek(0) != Some(b'=') {
                        return error(INVALID, self.pos);
                    }
                    self.pos += 1;
                    self.skip_space();
                    if !matches!(self.peek(0), Some(b'"' | b'\'')) {
                        return error(INVALID, self.pos);
                    }
                    let value = self.value()?;
                    self.attrs.push(RawAttr {
                        qname: name,
                        value,
                        at,
                    });
                }
                None => return error("unclosed token", start),
                Some(_) => return error(INVALID, self.pos),
            }
        };

        let scope_len = self.scope.len();
        let mut attrs = std::mem::take(&mut self.attrs);
        for (i, attr) in attrs.iter().enumerate() {
            if attrs[..i].iter().any(|other| other.qname == attr.qname) {
                return error("duplicate attribute", attr.at);
            }
            let prefix: &'a [u8] = if attr.qname == b"xmlns" {
                b""
            } else if let Some(prefix) = attr.qname.strip_prefix(b"xmlns:") {
                if prefix.is_empty() {
                    return error(INVALID, attr.at);
                }
                prefix
            } else {
                continue;
            };
            let uri = match &attr.value {
                Val::Src(a, b) => as_text(&data[*a as usize..*b as usize]).to_owned(),
                Val::Own(text) => text.to_string(),
                _ => unreachable!(),
            };
            if prefix == b"xmlns" || (prefix == b"xml") != (uri == XML_NS) {
                return error("reserved prefix (xml) must not be undeclared or bound to another namespace name", attr.at);
            }
            if !prefix.is_empty() && uri.is_empty() {
                return error(INVALID, attr.at);
            }
            let id = self.uri_id(&uri);
            self.scope.push((prefix, prefix_key(prefix), id));
        }

        let tag = self.resolve(qname, start, true)?;
        let mut resolved: Vec<(NameRef, Val)> = Vec::with_capacity(attrs.len());
        for attr in attrs.drain(..) {
            if attr.qname == b"xmlns" || attr.qname.starts_with(b"xmlns:") {
                continue;
            }
            let name = self.resolve(attr.qname, attr.at, false)?;
            if resolved.iter().any(|(other, _)| Arc::ptr_eq(other, &name)) {
                return error("duplicate attribute", attr.at);
            }
            resolved.push((name, attr.value));
        }
        self.attrs = attrs;

        let mut node = NodeData::new(Tag::Name(tag));
        node.attrs = resolved;
        node.src = Some(self.src.clone());
        node.start = start as u32;
        let node = Node::new(node);
        if self.index {
            let end = self.pos as u32;
            self.placed.push(Placed {
                node: node.clone(),
                span: [start as u32, end, end, end],
                depth: 0,
            });
        }
        Ok((node, empty, qname, scope_len))
    }

    /// The root element and everything in it, at the root's `<`.
    fn elements(&mut self) -> Result<Arc<Node>, ParseError> {
        let data = self.data;
        let (root, empty, qname, scope_len) = self.start_tag()?;
        if empty {
            self.scope.truncate(scope_len);
            return Ok(root);
        }
        let mut stack = vec![Open {
            node: root.clone(),
            qname,
            scope_len,
            placed: 0,
        }];
        let mut text = Acc::None;
        // Where gathered text goes: the text of an element just opened, or
        // the tail of one just closed.
        let mut last = root.clone();
        let mut last_is_tail = false;

        let flush = |text: &mut Acc, last: &Arc<Node>, tail: bool| {
            if let Some(value) = text.take() {
                let mut node = last.data.unshared();
                if tail {
                    node.tail = Some(value);
                } else {
                    node.text = Some(value);
                }
            }
        };

        loop {
            let Some(found) = memchr2(b'<', b'&', &data[self.pos..]) else {
                return error("no element found", data.len());
            };
            if found > 0 {
                let (start, end) = (self.pos, self.pos + found);
                let segment = &data[start..end];
                match memchr2(b']', b'\r', segment) {
                    None => text.range(data, start, end),
                    Some(_) => {
                        if let Some(at) = memmem::find(segment, b"]]>") {
                            return error(INVALID, start + at);
                        }
                        text.lines(data, start, end);
                    }
                }
                self.pos = end;
            }
            if data[self.pos] == b'&' {
                let ch = self.reference()?;
                let mut buffer = [0u8; 4];
                text.own(data).push_str(ch.encode_utf8(&mut buffer));
                continue;
            }
            match self.peek(1) {
                Some(b'/') => {
                    let close_start = self.pos;
                    let open = stack.pop().expect("an element is open");
                    let name_end = close_start + 2 + open.qname.len();
                    if data.get(close_start + 2..name_end) == Some(open.qname)
                        && !data.get(name_end).is_some_and(|&b| NAME_CHAR[b as usize])
                    {
                        self.pos = name_end;
                    } else {
                        self.pos += 2;
                        self.name()?;
                        return error("mismatched tag", close_start);
                    }
                    self.skip_space();
                    if self.peek(0) != Some(b'>') {
                        return error(INVALID, self.pos);
                    }
                    self.pos += 1;
                    flush(&mut text, &last, last_is_tail);
                    self.scope.truncate(open.scope_len);
                    if self.index {
                        let span = &mut self.placed[open.placed].span;
                        span[2] = close_start as u32;
                        span[3] = self.pos as u32;
                    }
                    last = open.node;
                    last_is_tail = true;
                    if stack.is_empty() {
                        return Ok(root);
                    }
                }
                Some(b'!') => {
                    if self.starts_with(b"<!--") {
                        self.comment()?;
                    } else if self.starts_with(b"<![CDATA[") {
                        self.cdata(&mut text)?;
                    } else {
                        return error(INVALID, self.pos);
                    }
                }
                Some(b'?') => self.instruction()?,
                _ => {
                    flush(&mut text, &last, last_is_tail);
                    let placed = self.placed.len();
                    let (node, empty, qname, scope_len) = self.start_tag()?;
                    let parent = &stack.last().expect("an element is open").node;
                    node.data.unshared().parent = Arc::downgrade(parent);
                    parent.data.unshared().children.push(node.clone());
                    if self.index {
                        self.placed[placed].depth = stack.len() as u32;
                    }
                    if empty {
                        self.scope.truncate(scope_len);
                        last = node;
                        last_is_tail = true;
                    } else {
                        stack.push(Open {
                            node: node.clone(),
                            qname,
                            scope_len,
                            placed,
                        });
                        last = node;
                        last_is_tail = false;
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn check(data: &[u8]) -> Result<(), ParseError> {
        check_characters(data)
    }

    #[test]
    fn characters() {
        assert!(check(b"<a>\x01</a>").is_err());
        assert!(check(b"<a>\xEF\xBF\xBE</a>").is_err());
        assert!(check(b"<a>\xff</a>").is_err());
        assert!(check("<a>caf\u{e9}\t\r\n</a>".as_bytes()).is_ok());
    }
}
