---
description: >-
  The ddi-l logo, favicon and documentation stylesheets, and the rules for
  using them.
---

# Documentation assets

Branding and styling assets used by MkDocs.

## Logo and favicon

The header mark lives at `docs/overrides/.icons/ddi/logo.svg`: stacked records
wrapped by an open circular arrow, for a dataset moving through the DDI
*Lifecycle*. It is drawn entirely in `currentColor`, so it takes the header's
foreground in every palette, including high contrast, without a second asset.
That only works because `theme.icon.logo` makes Material inline it; set as
`theme.logo` it would load as an `<img>`, where `currentColor` is black. Do not
add palette-specific fills to it.

`favicon.svg` is a separate file rather than the same one reused. A browser tab
renders at 16–32px against the browser's chrome, not the site's, so there is no
inherited colour to take: it carries its own ground and drops the lifecycle arc,
which turns to mud at that size.

## Colours

There is one brand colour, blue: a deep blue for the header, the same family
for links and buttons. Orange marks only the keyboard focus ring. Code blocks
and inline code sit on a neutral grey with no border.

There are three palettes: light (`default`), dark (`slate`) and
`high-contrast`. Blue with a sparingly used orange is a pairing that readers
with any common colour-vision deficiency can tell apart, so there are no
separate colour-vision palettes. Every palette entry in `mkdocs.yml` declares
`primary: custom` and `accent: custom`; without them Material's default indigo
rules override `palette.css` in dark mode.

## Stylesheets

| File | Purpose |
| ------ | --------- |
| `palette.css` | Colour tokens for the three palettes, headings, buttons, code and note/info boxes. |
| `accessibility.css` | Skip link, focus ring, screen-reader-only utility, reduced-motion overrides, the version banner, and the palette menu. |
| `landing.css` | Call-to-action buttons and the card grid, used only by `index.*.md`. |

Light and dark are on the header toggle. High contrast is chosen from the
palette menu beside it, which lists all three palettes: Material cycles its
toggle through every palette that declares one, and in high contrast the toggle
has nothing to show, so the menu is also the way back. See the comments in
`mkdocs.yml` and `docs/overrides/partials/palette.html`.
