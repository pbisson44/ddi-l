"""Preflight helpers shared between validation and fallback schema logic."""

from __future__ import annotations

from .._etree import Element


class _PreflightValidationError(Exception):
    """Lightweight exception used to build structured validation issues."""

    def __init__(
        self,
        message: str,
        node: Element | None = None,
        *,
        path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.reason = message
        self.message = message
        self.elem = node
        self.obj = node
        self.path = path


def _ensure_identification_elements(root: Element, *, reusable_namespace: str) -> None:
    """Validate that required identification nodes exist for a DDI instance."""
    missing: list[str] = []
    for name in ("Agency", "ID", "Version"):
        child = root.find(f"{{{reusable_namespace}}}{name}")
        if child is None:
            missing.append(name)
    if missing:
        raise _PreflightValidationError(
            f"Missing required identification element(s): {', '.join(missing)}",
            root,
        )


def _child_text(element: Element, namespace: str, tag: str) -> str | None:
    child = element.find(f"{{{namespace}}}{tag}")
    if child is None:
        return None
    if child.text is None:
        return None
    text = child.text.strip()
    return text or None


__all__ = [
    "_PreflightValidationError",
    "_child_text",
    "_ensure_identification_elements",
]
