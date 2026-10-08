"""Expose conversion helpers bound to the pure Python implementation."""

from __future__ import annotations

import sys
from collections.abc import Callable
from typing import Any

from . import _conversion as _conversion_py

_EXPORTED_NAMES = (
    "_element_to_dict",
    "_align_mapping_with_element",
    "_build_element_from_mapping",
    "_collect_declared_namespaces",
    "_denormalize_clark_notation",
    "_normalize_input_mapping",
    "_normalize_prefixed_qnames",
    "_normalize_result_namespaces",
    "from_dict",
    "to_dict",
)

_ORIGINAL_PYTHON_FUNCTIONS = {
    name: getattr(_conversion_py, name) for name in _EXPORTED_NAMES
}


def _wrap_python_function(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    if name == "_build_element_from_mapping":

        def _wrapped(
            tag: str,
            content: Any,
            *,
            process_namespaces: bool = True,
            **kwargs: Any,
        ) -> Any:
            return func(
                tag,
                content,
                process_namespaces=process_namespaces,
                **kwargs,
            )

        _wrapped.__name__ = func.__name__
        _wrapped.__doc__ = func.__doc__
        return _wrapped

    return func


_PYTHON_FUNCTIONS = {
    name: _wrap_python_function(name, func)
    for name, func in _ORIGINAL_PYTHON_FUNCTIONS.items()
}

_ACTIVE_FUNCTIONS: dict[str, Callable[..., Any]] = _PYTHON_FUNCTIONS
_PROXY_FUNCTIONS: dict[str, Callable[..., Any]] = {}


def _sync_conversion_module() -> None:
    for _name, _func in _ORIGINAL_PYTHON_FUNCTIONS.items():
        setattr(_conversion_py, _name, _func)


def _create_proxy(name: str) -> Callable[..., Any]:
    reference = _ORIGINAL_PYTHON_FUNCTIONS.get(name)

    if name == "_build_element_from_mapping":

        def _proxy(*args: Any, **kwargs: Any) -> Any:
            kwargs.setdefault("process_namespaces", True)
            return _ACTIVE_FUNCTIONS[name](*args, **kwargs)

    else:

        def _proxy(*args: Any, **kwargs: Any) -> Any:
            return _ACTIVE_FUNCTIONS[name](*args, **kwargs)

    if reference is not None:
        _proxy.__doc__ = reference.__doc__
    _proxy.__name__ = name
    return _proxy


def _bind_exported_functions(functions: dict[str, Callable[..., Any]]) -> None:
    global _ACTIVE_FUNCTIONS
    _ACTIVE_FUNCTIONS = functions


def get_available_conversion_backends() -> tuple[str, ...]:
    return ("python",)


def set_conversion_backend(backend: str) -> None:
    backend = backend.lower().strip()
    if backend != "python":
        raise RuntimeError("Only the pure Python conversion backend is available")
    _bind_exported_functions(_PYTHON_FUNCTIONS)
    _sync_conversion_module()
    globals()["IMPLEMENTATION"] = backend

    loader_module = sys.modules.get("ddi_l.schema_loader")
    if loader_module is not None:
        loader_module.CONVERSION_IMPLEMENTATION = IMPLEMENTATION  # type: ignore[attr-defined]
        for _name in _EXPORTED_NAMES:
            setattr(loader_module, _name, globals()[_name])


for _export_name in _EXPORTED_NAMES:
    _PROXY_FUNCTIONS[_export_name] = _create_proxy(_export_name)
    globals()[_export_name] = _PROXY_FUNCTIONS[_export_name]

_bind_exported_functions(_PYTHON_FUNCTIONS)
_sync_conversion_module()

IMPLEMENTATION: str = "python"

__all__ = [
    "IMPLEMENTATION",
    "_PYTHON_FUNCTIONS",
    *_EXPORTED_NAMES,
    "get_available_conversion_backends",
    "set_conversion_backend",
]
