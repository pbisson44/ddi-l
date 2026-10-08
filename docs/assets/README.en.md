---
description: >-
  The ddi-l logo, favicon and documentation stylesheets, and the rules for
  using them.
---

# Documentation assets

Branding and styling assets used by MkDocs.

## Logo and favicon

`logo.svg` is the header mark: stacked records wrapped by an open circular
arrow, for a dataset moving through the DDI *Lifecycle*. It is drawn entirely in
`currentColor`, so it inherits the header's foreground and stays legible in all
six palettes, including high contrast, without a second asset. Do not add
palette-specific fills to it.

`favicon.svg` is a separate file rather than the same one reused. A browser tab
renders at 16–32px against the browser's chrome, not the site's, so there is no
inherited colour to take: it carries its own ground and drops the lifecycle arc,
which turns to mud at that size.

## Stylesheets

| File | Purpose |
| ------ | --------- |
| `palette.css` | Colour tokens for the six schemes: `default`, `slate`, `high-contrast`, and the `deuteranopia` / `protanopia` / `tritanopia` colour-vision palettes. |
| `accessibility.css` | Skip link, screen-reader-only utility, reduced-motion overrides, the version banner, and the accessibility palette menu. |
| `landing.css` | Call-to-action buttons and the card grid, used only by `index.*.md`. |

The accessibility palettes are chosen from a menu in the header rather than the
theme toggle: Material cycles its toggle through every palette that declares
one, so putting all six there meant six clicks to get back to light mode. See
the comments in `mkdocs.yml` and `docs/overrides/partials/palette.html`.
