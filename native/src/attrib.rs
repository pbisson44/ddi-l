//! `Attrib`: an element's attributes as a live mapping, like lxml's.

use std::sync::Arc;

use pyo3::exceptions::{PyKeyError, PyTypeError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};

use crate::tree::{touch, Name, NameRef, Node, Val};

/// Set `key` to `value` in `attrs`, keeping the attribute's place if it is there.
pub fn set_attr(
    py: Python<'_>,
    attrs: &mut Vec<(NameRef, Val)>,
    key: &Bound<'_, PyAny>,
    value: &Bound<'_, PyAny>,
) -> PyResult<()> {
    let key = key
        .cast::<PyString>()
        .map_err(|_| PyTypeError::new_err("attribute names must be strings"))?;
    let text = key.to_str()?;
    let value = Val::from_py(value);
    match attrs.iter_mut().find(|(name, _)| &*name.text == text) {
        Some(slot) => slot.1 = value,
        None => attrs.push((Name::from_py(py, key)?, value)),
    }
    Ok(())
}

#[pyclass(frozen, mapping, module = "ddi_l_native._core", name = "Attrib")]
pub struct Attrib {
    pub node: Arc<Node>,
}

impl Attrib {
    fn find<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
    ) -> PyResult<Option<Bound<'py, PyAny>>> {
        let Ok(key) = key.cast::<PyString>() else {
            return Ok(None);
        };
        let key = key.to_str()?;
        let data = self.node.data.get(py);
        Ok(data.attr(key).map(|value| value.to_py(py, data.src())))
    }

    fn take(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<bool> {
        let Ok(key) = key.cast::<PyString>() else {
            return Ok(false);
        };
        let key = key.to_str()?;
        let removed = {
            let mut data = self.node.data.get_mut(py);
            match data.attrs.iter().position(|(name, _)| &*name.text == key) {
                Some(at) => {
                    data.attrs.remove(at);
                    true
                }
                None => false,
            }
        };
        if removed {
            touch(py, &self.node);
        }
        Ok(removed)
    }

    fn set(
        &self,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        set_attr(py, &mut self.node.data.get_mut(py).attrs, key, value)?;
        touch(py, &self.node);
        Ok(())
    }

    fn as_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        let data = self.node.data.get(py);
        for (name, value) in &data.attrs {
            dict.set_item(name.to_py(py), value.to_py(py, data.src()))?;
        }
        Ok(dict)
    }
}

#[pymethods]
impl Attrib {
    fn __len__(&self, py: Python<'_>) -> usize {
        self.node.data.get(py).attrs.len()
    }

    fn __getitem__<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
    ) -> PyResult<Bound<'py, PyAny>> {
        self.find(py, key)?
            .ok_or_else(|| PyKeyError::new_err(key.clone().unbind()))
    }

    fn __setitem__(
        &self,
        py: Python<'_>,
        key: &Bound<'_, PyAny>,
        value: &Bound<'_, PyAny>,
    ) -> PyResult<()> {
        self.set(py, key, value)
    }

    fn __delitem__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<()> {
        if self.take(py, key)? {
            Ok(())
        } else {
            Err(PyKeyError::new_err(key.clone().unbind()))
        }
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        Ok(self.keys(py)?.try_iter()?.into_any())
    }

    fn __contains__(&self, py: Python<'_>, key: &Bound<'_, PyAny>) -> PyResult<bool> {
        Ok(self.find(py, key)?.is_some())
    }

    fn __eq__(&self, py: Python<'_>, other: &Bound<'_, PyAny>) -> PyResult<bool> {
        let other = match other.cast::<Attrib>() {
            Ok(attrib) => attrib.get().as_dict(py)?.into_any(),
            Err(_) => other.clone(),
        };
        self.as_dict(py)?.eq(other)
    }

    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        Ok(self.as_dict(py)?.repr()?.to_string())
    }

    fn keys<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let data = self.node.data.get(py);
        PyList::new(py, data.attrs.iter().map(|(name, _)| name.to_py(py)))
    }

    fn values<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let data = self.node.data.get(py);
        PyList::new(
            py,
            data.attrs
                .iter()
                .map(|(_, value)| value.to_py(py, data.src())),
        )
    }

    fn items<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let data = self.node.data.get(py);
        let list = PyList::empty(py);
        for (name, value) in &data.attrs {
            list.append(PyTuple::new(
                py,
                [name.to_py(py).into_any(), value.to_py(py, data.src())],
            )?)?;
        }
        Ok(list)
    }

    #[pyo3(signature = (key, default=None))]
    fn get<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
        default: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        Ok(self
            .find(py, key)?
            .or_else(|| default.cloned())
            .unwrap_or_else(|| py.None().into_bound(py)))
    }

    #[pyo3(signature = (key, *default))]
    fn pop<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
        default: &Bound<'py, PyTuple>,
    ) -> PyResult<Bound<'py, PyAny>> {
        match self.find(py, key)? {
            Some(value) => {
                self.take(py, key)?;
                Ok(value)
            }
            None if !default.is_empty() => default.get_item(0),
            None => Err(PyKeyError::new_err(key.clone().unbind())),
        }
    }

    #[pyo3(signature = (key, default=None))]
    fn setdefault<'py>(
        &self,
        py: Python<'py>,
        key: &Bound<'py, PyAny>,
        default: Option<&Bound<'py, PyAny>>,
    ) -> PyResult<Bound<'py, PyAny>> {
        if let Some(value) = self.find(py, key)? {
            return Ok(value);
        }
        let value = default.cloned().unwrap_or_else(|| py.None().into_bound(py));
        self.set(py, key, &value)?;
        Ok(value)
    }

    #[pyo3(signature = (other=None, **extra))]
    fn update(
        &self,
        py: Python<'_>,
        other: Option<&Bound<'_, PyAny>>,
        extra: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<()> {
        if let Some(other) = other {
            let pairs = if other.hasattr("keys")? {
                other.call_method0("items")?
            } else {
                other.clone()
            };
            for pair in pairs.try_iter()? {
                let pair = pair?;
                self.set(py, &pair.get_item(0)?, &pair.get_item(1)?)?;
            }
        }
        if let Some(extra) = extra {
            for (key, value) in extra.iter() {
                self.set(py, &key, &value)?;
            }
        }
        Ok(())
    }

    fn clear(&self, py: Python<'_>) {
        self.node.data.get_mut(py).attrs.clear();
        touch(py, &self.node);
    }

    fn copy<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        self.as_dict(py)
    }
}
